#!/usr/bin/python3
# invenroty_process.py
"""


inventory_process - maintains a list and reports the list of inventory reported by applications for mqtt-tower



The MIT License (MIT)

Copyright 2023 richard p hughes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OFSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""


import os
import sys

sys.path.append('../lib')

from utils.json_utils import JsonUtils
from utils.global_constants import Global


from structs.sensor_states import SensorStateData
from structs.sensor_states import SensorStates

from structs.inventory import Inventory
from structs.io_data import IoData
from structs.mqtt_config import MqttConfig

from processes.base_process import SendAfterMessage
from processes.base_process import BaseProcess
from signals_manager import SignalsManager

class InventoryProcess(BaseProcess):
    """ Class that generates inventory and states reports """

    def __init__(self, events=None, queues=None):
        super().__init__(name="inventory",
                         events=events,
                         in_queue=queues[Global.INVENTORY],
                         log_queue=queues[Global.LOGGER])

        self.events = events
        self.central_traffic_control = False
        self.auto_signals = False
        self.mqtt_config = None
        self.self_topic = None
        self.node_topic = None
        self.switch_topic = None
        self.tower_topic = None
        self.inventory_topic = None
        self.app_queue = queues[Global.APPLICATION]
        self.data_path = None
        self.json_helper = JsonUtils()
        self.inventory = Inventory()
        self.sensor_states = SensorStates()
        self.signals_manager = None
        self.inventory_changed = False
        self.check_inventory_send_after_message = None


    def initialize_process(self):
        """ load data from file system """
        super().initialize_process()
        self.mqtt_config = MqttConfig(self.config, self.node_name,
                                      self.host_name, self.log_queue)
        (self.node_topic, self.self_topic, self.tower_topic, \
                self.inventory_topic, self.switch_topic) \
            = self.__parse_mqtt_options_config(self.mqtt_config)
        self.inventory_topic = self.inventory_topic.replace("/#", "/res")
        self.self_topic = self.self_topic.replace("/#", "/res")
        (self.data_path, _backup_path) \
            = self.__parse_path_options_config(self.config)
        if self.data_path is None or \
                not os.path.exists(self.data_path):
            self.log_error("!!! Error: data path does not exists: " +
                           str(self.data_path))
        else:
            self.__init_signals_manager()
        self.check_inventory_send_after_message = \
                    SendAfterMessage(Global.INVENTORY, None, 10000) # 10 seconds
        self.send_after(self.check_inventory_send_after_message)

    def process_message(self, new_message):
        """ process received messages """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            (msg_type, msg_body) = new_message
            # print(">>> msg type: "+ str(msg_type))
            if msg_type == Global.TRAFFIC:
                self.__process_traffic_control_switch_message(msg_body)
                msg_consummed = True
            elif msg_type == Global.AUTO_SIGNALS:
                self.__process_auto_signals_switch_message(msg_body)
                msg_consummed = True
            elif msg_type == Global.ROUTE:
                self.__process_route_request(msg_body)
                msg_consummed = True
            elif msg_type == Global.REQUEST:
                self.__process_request(msg_body)
                msg_consummed = True
            elif msg_type == Global.RESPONSE:
                # report_desired = \
                #    msg_body.get_desired_value_by_key(Global.REPORT)
                if msg_body.mqtt_port_id == Global.INVENTORY:
                    self.__process_inventory_response(msg_body)
                    msg_consummed = True
            elif msg_type == Global.ACTIVATED:
                self.log_info("Node Detected: " + str(msg_body))
                if msg_body != self.node_name and \
                        msg_body.lower().find(Global.TOWER.lower()) == -1:
                    # request inventory for activated nodes except ourselves
                    self.__request_inventory(msg_body)
                    msg_consummed = True
            elif msg_type == Global.STATE:
                # record a change of state of a sensor,switch, etc
                self.__update_sensor_state(msg_body)
                msg_consummed = True
            elif msg_type == Global.INVENTORY:
                if self.__check_for_inventory_changes():
                    self.log_info("Inventory data has changed, notify other apps]")
                    self.__publish_inventory_changed()
                self.send_after(self.check_inventory_send_after_message)
                msg_consummed = True
        return msg_consummed

    #
    # private functions
    #

    def __check_for_inventory_changes(self):
        """ check for changes to roster and reload is necessary"""
        changed = False
        if self.inventory_changed:
            changed = True
            self.inventory_changed = False
        return changed


    def __process_request(self, msg_body):
        """ process request to send inventory reports """
        report_desired = msg_body.mqtt_desired
        port_id = msg_body.mqtt_port_id
        self.log_info("report desired: " + str(report_desired)+" ... "+str(port_id))
        reported = report_desired
        metadata = None
        # check if requestor is the mqtt_dispatcher app
        # if not, do send inventory if central traffic control is enabled
        is_tower = (msg_body.mqtt_respond_to.find(Global.TOWER) != -1)
        is_dispatcher = (msg_body.mqtt_respond_to.find(Global.DISPATCHER) != -1)
        if self.central_traffic_control and not is_dispatcher:
            metadata = self.__generate_empty_inventory_report(group=report_desired)
        else:
            if report_desired == Global.REPORT:
                if port_id == Global.INVENTORY:
                    if is_tower:
                        # make sure we done send inventory to another tower
                        self.__generate_empty_inventory_report(group=report_desired)
                    else:
                        metadata = self.__generate_inventory_report()
                elif port_id == Global.SWITCHES:
                    metadata = self.__generate_inventory_report(group=Global.SWITCH)
                elif port_id == Global.SIGNALS:
                    metadata = self.__generate_inventory_report(group=Global.SIGNAL)
                elif port_id == Global.ROUTES:
                    metadata = self.__generate_inventory_report(group=Global.ROUTE)
                elif port_id == Global.STATES:
                    metadata = self.__generate_sensor_states_report()
                else:
                    self.log_unexpected_message(msg_body=msg_body)
                    metadata = {Global.ERROR: "Unknown report requested: "+str(port_id)}
                    reported = Global.ERROR
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.RESPONSE, \
                                        Global.REPORTED: reported, \
                                        Global.METADATA: metadata, Global.BODY: msg_body}))

    def __report_route_data(self, _node_id, port_id, reported, topic):
        """ send a route data message data"""
        msg_body = IoData()
        msg_body.mqtt_reported = reported
        msg_body.mqtt_message_root = Global.SWITCH
        msg_body.mqtt_port_id = port_id
        msg_body.mqtt_respond_to = None  # ignore response, monitor data message
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.DATA,
                                             Global.TOPIC: topic, Global.BODY: msg_body}))

    def __request_switch(self, _node_id, port_id, desired, topic):
        """ request a switch change from a node """
        print(">>> switch: " + str(port_id))
        msg_body = IoData()
        msg_body.mqtt_desired = desired
        msg_body.mqtt_message_root = Global.SWITCH
        msg_body.mqtt_port_id = port_id
        msg_body.mqtt_respond_to = None  # ignore response, monitor data message
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.REQUEST,
                                             Global.TOPIC: topic, Global.BODY: msg_body}))

    def __request_inventory(self, node_id):
        """ request inventory from a node """
        #print(">>> node activated: " + str(node_id))
        msg_body = IoData()
        msg_body.mqtt_desired = Global.REPORT
        msg_body.mqtt_message_root = Global.TOWER
        msg_body.mqtt_node_id = node_id
        msg_body.mqtt_port_id = Global.INVENTORY
        msg_body.mqtt_respond_to = self.inventory_topic
        topic = self.node_topic + "/" + node_id + \
            "/"+ Global.INVENTORY+"/" + Global.REQ
        # print(">>> inv req topic: "+str(topic))
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.REQUEST,
                                             Global.TOPIC: topic,
                                             Global.BODY: msg_body}))

    def __process_inventory_response(self, msg_body):
        """ received inventory response, add info to current inventory """
        #  print(">>> inventory response: " + str(msg_body.mqtt_node_id))
        node_inventory = Inventory(msg_body.mqtt_metadata)
        # print(">>>\n\n inv response: " + str(node_inventory))
        self.inventory.remove_node_inventory(msg_body.mqtt_node_id)
        self.inventory.add_node_inventory(msg_body.mqtt_node_id,
                                          node_inventory)
        # remove any old state for items no longer served by this node
        node_item_list = self.inventory.build_node_item_list(
            msg_body.mqtt_node_id)
        # print(">>> node items:" + str(node_item_list))
        if self.sensor_states is not None:
            self.sensor_states.sync_node_states(msg_body.mqtt_node_id,
                                                node_item_list)
        self.inventory_changed = True

    def __process_traffic_control_switch_message(self, msg_body=None):
        """ process for control switch requests """
        # print(">>> traffic control msg: " + str(msg_body))
        reported = Global.ERROR
        data_reported = None
        message = Global.MSG_ERROR_BAD_DESIRED
        if msg_body.mqtt_port_id == Global.TRAFFIC:
            desired = msg_body.mqtt_desired
            if desired in [Global.ON]:
                self.central_traffic_control = True
                reported = Global.ON
                data_reported = reported
                message = None
                data_reported = reported
            elif desired in [Global.OFF]:
                self.central_traffic_control = False
                reported = Global.OFF
                data_reported = reported
                message = None
        self.__publish_responses(msg_body, reported, message, data_reported)


    def __process_auto_signals_switch_message(self, msg_body=None):
        """ process for auto signal switch requests """
        # print(">>> auto signals msg: " + str(msg_body))
        reported = Global.ERROR
        data_reported = None
        message = Global.MSG_ERROR_BAD_DESIRED
        if msg_body.mqtt_port_id == Global.AUTO_SIGNALS:
            desired = msg_body.mqtt_desired
            if desired in [Global.ON]:
                self.auto_signals = True
                reported = Global.ON
                message = None
                data_reported = reported
            elif desired in [Global.OFF]:
                self.auto_signals = False
                reported = Global.OFF
                message = None
                data_reported = reported
        self.__publish_responses(msg_body, reported, message, data_reported)

    def __generate_empty_inventory_report(self, group=None):
        """ generate an empty report data for a group """
        #print(">>> generate empty inventory")
        rett = {Global.INVENTORY: {Global.DESCRIPTION: Global.INVENTORY, Global.INVENTORY: {group : {}}}}
        return rett

    def __generate_inventory_report(self, group=None):
        """ generate report data for a group """
        #print(">>> generate inventory")
        rett = None
        if self.inventory is not None:
            rett = self.inventory.encode(requested_group=group)
        return rett

    def __generate_sensor_states_report(self):
        """ generate report data for sensor states """
        rett = None
        if self.sensor_states is not None:
            rett = self.sensor_states.encode()
        return rett

    def __update_sensor_state(self, msg_body):
        """ up the state of a sensor, switch, etc """
        state_data = SensorStateData()
        state_data.node_id = msg_body.mqtt_node_id
        state_data.port_id = msg_body.mqtt_port_id
        state_data.key = state_data.node_id + ":" + state_data.port_id
        state_data.reported = msg_body.mqtt_reported
        state_data.loco_id = [msg_body.mqtt_loco_id
                              ]  # state loco_id are a list
        state_data.metdata = msg_body.mqtt_metadata
        state_data.timestamp = msg_body.mqtt_timestamp
        if msg_body.mqtt_loco_id is not None:
            state_data.loco = [msg_body.mqtt_loco_id]
        #print(">>> update sensor: " + str(state_data))
        if self.sensor_states is not None:
            if not self.sensor_states.sensor_data_momentary(msg_body.mqtt_message_root, state_data):
                self.sensor_states.update_sensor_state(msg_body.mqtt_message_root,
                                                state_data)
                self.signals_manager.update_signals(msg_body.mqtt_message_root, state_data)

    def __publish_responses(self, msg_body, reported, message, data_reported):
        """ format and publish responses """
        # print(">>> response: " + str(reported))
        metadata = None
        if message is not None:
            metadata = {Global.MESSAGE: message}
        self.app_queue.put((Global.PUBLISH, {\
                Global.TYPE: Global.RESPONSE, \
                Global.REPORTED: reported,
                Global.METADATA: metadata,
                Global.DATA: data_reported,
                Global.BODY: msg_body}))

    def __parse_path_options_config(self, config):
        """ parse path options section of config file """
        data_path = None
        backup_path = None
        if Global.CONFIG in config:
            if Global.OPTIONS in config[Global.CONFIG]:
                data_path = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.DATA_PATH, None)
                backup_path = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.BACKUP_PATH, None)
        return (data_path, backup_path)

    def __process_route_request(self, msg_body):
        """ process a request to set a route message"""
        route_ok = False
        # print(">>> route request: " + str(msg_body.mqtt_port_id))
        route = self.__find_route(self.node_name, msg_body.mqtt_port_id)
        if route is not None:
            route_ok = True
            #print(">>> found route: " + str(route.port_id))
            meta = route.metadata
            if meta is not None:
                switches = meta.get(Global.SWITCH, None)
                if switches is not None:
                    for switch in switches:
                        # print(">>> " + str(switch))
                        node_id = switch.get(Global.NODE_ID, None)
                        port_id = switch.get(Global.PORT_ID, None)
                        desired = switch.get(Global.DESIRED, None)
                        if node_id is not None and \
                                port_id is not None and \
                                desired is not None:
                            inv_switch = self.__find_switch(node_id, port_id)
                            if inv_switch is not None:
                                # print(">>> found switch: "+str(port_id))
                                self.__request_switch(node_id, port_id, desired,
                                                      inv_switch.command_topic)
        data_response_reported = Global.ACTIVATED
        if not route_ok:
            data_response_reported = Global.ERROR
        self.__report_route_data(self.node_name, msg_body.mqtt_port_id,
                                 data_response_reported, self.switch_topic)

    def __find_switch(self, node_id, port_id):
        """ find a switch given a port and node ids """
        switch = None
        inv_groups = self.inventory.inventory_groups
        if inv_groups is not None:
            switches = inv_groups.get(Global.SWITCH, None)
            if switches is not None:
                for s in switches.inventory_items:
                    # print(">>> switch ... "+str(s.port_id))
                    if s.node_id == node_id and \
                            s.port_id == port_id:
                        switch = s
                        break
        return switch

    def __find_route(self, node_id, port_id):
        """ find a route given a port and node ids """
        route = None
        inv_groups = self.inventory.inventory_groups
        if inv_groups is not None:
            routes = inv_groups.get(Global.ROUTE, None)
            if routes is not None:
                for r in routes.inventory_items:
                    # print(">>> route ... "+str(r.port_id))
                    if r.node_id == node_id and \
                            r.port_id == port_id:
                        route = r
                        break
        return route

    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse pub topics of config file """
        node_topic = mqtt_config.publish_topics.get(Global.NODE,
                                                    Global.UNKNOWN)
        tower_topic = mqtt_config.publish_topics.get(Global.TOWER,
                                                    Global.UNKNOWN)
        inventory_topic = mqtt_config.subscribe_topics.get(Global.INVENTORY,
                                                    Global.UNKNOWN)
        self_topic = mqtt_config.subscribe_topics.get(Global.SELF,
                                                      Global.UNKNOWN)
        switch_topic = mqtt_config.publish_topics.get(Global.SWITCH,
                                                      Global.UNKNOWN)
        return (node_topic, self_topic, tower_topic, inventory_topic, switch_topic)

    def __init_signals_manager(self):
        """ initialize the signals manager """
        self.signals_manager = SignalsManager(self.app_queue,
                self.sensor_states, self.data_path, self.log_queue)

    def __publish_inventory_changed(self):
        """ send a data message notifing inventory has changed """
        self.log_info("Publish Inventory changed...")
        topic = self.mqtt_config.publish_topics.get(Global.INVENTORY,
                                                    Global.UNKNOWN)
        data_msg_body = IoData()
        data_msg_body.mqtt_message_root = Global.TOWER
        data_msg_body.mqtt_node_id = self.node_name
        data_msg_body.mqtt_port_id = Global.INVENTORY
        data_msg_body.mqtt_reported = Global.CHANGED
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.DATA, \
                                             Global.TOPIC: topic, \
                                             Global.BODY: data_msg_body}))
