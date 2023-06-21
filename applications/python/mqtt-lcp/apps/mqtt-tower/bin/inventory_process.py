#!/usr/bin/python3
# invenroty_process.py
"""


inventory_process - maintains a list and reports the list \
        of inventory reported by applications for mqtt-tower



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

from utils.global_constants import Global
from utils.global_synonyms import Synonyms
from utils.json_utils import JsonUtils

from structs.mqtt_config import MqttConfig
from structs.io_data import IoData
from structs.inventory import Inventory
from structs.inventory import InventoryData
from structs.inventory import InventoryGroupData

from processes.base_process import BaseProcess
from processes.base_process import SendAfterMessage

from signals_manager import SignalsManager
from cab_signals_manager import CabSignalsManager
from routes_manager import RoutesManager

class InventoryProcess(BaseProcess):
    """ Class that generates inventory and states reports """

    def __init__(self, events=None, queues=None):
        super().__init__(name="inventory",
                         events=events,
                         in_queue=queues[Global.INVENTORY],
                         log_queue=queues[Global.LOGGER])

        self.events = events
        self.admin_nodes = [] # ids of nodes allowed to set traffic and auto-signals on/off
        self.central_traffic_control_enabled = False
        self.auto_signals_enabled = False
        self.mqtt_config = None
        self.self_topic = None
        self.node_topic = None
        self.switch_topic = None
        self.route_topic = None
        self.route_data_topic = None
        self.tower_topic = None
        self.tower_sub_topic = None
        self.app_queue = queues[Global.APPLICATION]
        self.data_path = None
        self.json_helper = JsonUtils()
        self.inventory = Inventory()
        self.routes = {}
        self.signals_manager = None
        self.cab_signals_manager = None
        self.routes_manager = None
        self.inventory_changed = False
        self.check_inventory_send_after_message = None

    def initialize_process(self):
        """ load data from file system """
        super().initialize_process()
        self.mqtt_config = MqttConfig(self.config, self.node_name,
                                      self.host_name, self.log_queue)
        (self.node_topic, self.self_topic, self.tower_topic,
         self.tower_sub_topic, self.switch_topic, self.route_topic, self.route_data_topic) = \
                self.__parse_mqtt_options_config(self.mqtt_config)
        (self.central_traffic_control_enabled, self.auto_signals_enabled, self.admin_nodes) = \
                self.__parse_mqtt_options_traffic(self.config)
        self.__init_tower_inventory()
        self.tower_sub_topic = self.tower_sub_topic.replace("/#", "/res")
        self.self_topic = self.self_topic.replace("/#", "/res")
        self.route_topic = self.route_topic.replace("/#", "")
        (self.data_path, _backup_path) \
            = self.__parse_path_options_config(self.config)
        if self.data_path is None or \
                not os.path.exists(self.data_path):
            self.log_error("!!! Error: data path does not exists: " +
                           str(self.data_path))
        else:
            self.__init_tower_inventory()
            self.__publish_init_tower_state(self.central_traffic_control_enabled, self.auto_signals_enabled)
            self.__init_routes_manager()
            self.__init_signals_manager()
            self.__init_cab_signals_manager()
        self.check_inventory_send_after_message = \
            SendAfterMessage(Global.INVENTORY, None, 1000)  # 1 seconds
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
            elif msg_type == Global.ON:
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
                    self.log_info(
                        "Inventory data has changed, notify other apps]")
                    self.__publish_inventory_changed()
                    self.cab_signals_manager.inventory_has_changed()
                    self.signals_manager.inventory_has_changed()
                self.send_after(self.check_inventory_send_after_message)
                msg_consummed = True
        return msg_consummed

    def get_topic_node_id(self, topic):
        """ parse out node id from topic """
        node_id = Global.UNKNOWN
        if topic is not None:
            topic_parts = topic.split("/")
            if len(topic_parts) > 3:
                node_id = topic_parts[3]
        return node_id

    def process_request_device_message(self, group, node, port, desired, topic):
        """ process request a device change message """
        new_message = IoData()
        new_message.mqtt_message_root = group
        new_message.node_id = node
        new_message.mqtt_port_id = port
        new_message.mqtt_desired = desired
        # set responsd_to topic to none, don't care about response
        new_message.mqtt_respond_to = None
        self.app_queue.put(
            (Global.PUBLISH, {Global.TYPE: Global.REQUEST,
                              Global.TOPIC: topic, Global.BODY: new_message}))

    def find_signal(self, node_id, port_id):
        """ find a switch given a port and node ids """
        signal = None
        inv_groups = self.inventory.inventory_groups
        if inv_groups is not None:
            signals = inv_groups.get(Global.SIGNAL, None)
            if signals is not None:
                key = str(node_id)+":"+str(port_id)
                if node_id is None:
                    key = signals.inventory_by_port_id.get(port_id, None)
                # print(">>> signal key: "+str(key)+" : "+str(node_id)+" : "+str(port_id))
                #if key is None:
                #    print(">>> by port: "+str(signals.inventory_by_port_id) )
                signal = signals.inventory_items.get(key, None)
        return signal

    def find_switch(self, node_id, port_id):
        """ find a switch given a port and node ids """
        switch = None
        inv_groups = self.inventory.inventory_groups
        if inv_groups is not None:
            switches = inv_groups.get(Global.SWITCH, None)
            if switches is not None:
                key = str(node_id)+":"+str(port_id)
                switch = switches.inventory_items.get(key, None)
        return switch

    def find_route(self, node_id, port_id):
        """ find a route given a port and node ids """
        route = None
        inv_groups = self.inventory.inventory_groups
        if inv_groups is not None:
            routes = inv_groups.get(Global.ROUTE, None)
            if routes is not None:
                key = str(node_id)+":"+str(port_id)
                route = routes.inventory_items.get(key, None)
        return route

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
        self.log_info("report desired: " +
                      str(report_desired)+" ... "+str(port_id))
        reported = report_desired
        metadata = None
        is_tower = (msg_body.mqtt_respond_to.find(Global.TOWER) != -1)
        is_admin = msg_body.mqtt_publisher in self.admin_nodes
        # check if requestor is an admin node app
        # if not, do send empty inventory if central traffic control is enabled
        if self.central_traffic_control_enabled and not is_admin:
            print(">>> send empty: "+str(msg_body.mqtt_publisher))
            metadata = self.__generate_empty_inventory_report(
                group=report_desired)
        else:
            if report_desired == Global.REPORT:
                if port_id == Global.INVENTORY:
                    if is_tower:
                        # make sure we done send inventory to another tower
                        self.__generate_empty_inventory_report(
                            group=report_desired)
                    else:
                        metadata = self.__generate_inventory_report()
                elif port_id == Global.SWITCH:
                    metadata = self.__generate_inventory_report(
                        group=Global.SWITCH)
                elif port_id == Global.SIGNAL:
                    metadata = self.__generate_inventory_report(
                        group=Global.SIGNAL)
                elif port_id == Global.BLOCK:
                    metadata = self.__generate_inventory_report(
                        group=Global.BLOCK)
                elif port_id == Global.LOCATOR:
                    metadata = self.__generate_inventory_report(
                        group=Global.LOCATOR)
                elif port_id == Global.ROUTE:
                    metadata = self.__generate_inventory_report(
                        group=Global.ROUTE)
                elif port_id == Global.SENSOR:
                    metadata = self.__generate_inventory_report(
                        group=Global.SENSOR)
                else:
                    self.log_unexpected_message(msg_body=msg_body)
                    metadata = {
                        Global.ERROR: "Unknown report requested: "+str(port_id)}
                    reported = Global.ERROR
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.RESPONSE,
                                             Global.REPORTED: reported,
                                             Global.METADATA: metadata, Global.BODY: msg_body}))

    def __init_tower_inventory(self):
        """ add traffic and auto signals to tower inventory"""
        tower_group = InventoryGroupData()

        traffic_item = InventoryData()
        traffic_item.node_id = self.node_name
        traffic_item.port_id = Global.TRAFFIC
        traffic_item.command_topic = self.tower_sub_topic
        traffic_item.data_topic = self.tower_topic
        traffic_item.key = str(traffic_item.node_id) + ":" + str(traffic_item.port_id)
        tower_group.add_an_item(traffic_item)

        auto_signals_item = InventoryData()
        auto_signals_item.node_id = self.node_name
        auto_signals_item.port_id = Global.AUTO_SIGNALS
        auto_signals_item.command_topic = self.tower_sub_topic
        auto_signals_item.data_topic = self.tower_topic
        auto_signals_item.key = str(auto_signals_item.node_id) + ":" + str(auto_signals_item.port_id)
        tower_group.add_an_item(auto_signals_item)

        self.inventory.inventory_groups.update({Global.TOWER: tower_group})

    def __publish_init_tower_state(self, traffic_control, auto_signals):
        """ publish initial tower state messages for traffic and auto signals"""
        traffic = Global.OFF
        if traffic_control:
            traffic = Global.ON
        self.__publish_tower_data_state(Global.TRAFFIC, traffic)
        auto_sig = Global.OFF
        if auto_signals:
            auto_sig = Global.ON
        self.__publish_tower_data_state(Global.AUTO_SIGNALS, auto_sig)

    def __publish_tower_data_state(self, port, state):
        """ publish state of tower item"""
        topic = self.switch_topic
        data_msg_body = IoData()
        data_msg_body.mqtt_message_root = Global.TOWER
        data_msg_body.mqtt_node_id = self.node_name
        data_msg_body.mqtt_port_id = port
        data_msg_body.mqtt_reported = state
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.DATA,
                                             Global.TOPIC: topic,
                                             Global.BODY: data_msg_body}))


    def __request_switch(self, _node_id, port_id, desired, topic):
        """ request a switch change from a node """
        #print(">>> switch: " + str(port_id))
        msg_body = IoData()
        msg_body.mqtt_desired = desired
        msg_body.mqtt_message_root = Global.SWITCH
        msg_body.mqtt_port_id = port_id
        msg_body.mqtt_respond_to = None  # ignore response, monitor data message
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.REQUEST,
                                             Global.TOPIC: topic, Global.BODY: msg_body}))

    def __request_inventory(self, node_id):
        """ request inventory from a node """
        # print(">>> node activated: " + str(node_id))
        topic = self.node_topic + "/" + node_id + \
            "/" + Global.INVENTORY+"/" + Global.REQ
        msg_body = IoData()
        msg_body.mqtt_desired = Global.REPORT
        msg_body.mqtt_message_root = Global.TOWER
        msg_body.mqtt_node_id = self.get_topic_node_id(topic)
        msg_body.mqtt_port_id = Global.INVENTORY
        msg_body.mqtt_respond_to = self.tower_sub_topic.replace(
            "/res", "/"+Global.INVENTORY+"/res")

        # print(">>> inv req topic: "+str(topic))
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.REQUEST,
                                             Global.TOPIC: topic,
                                             Global.BODY: msg_body}))

    def __process_inventory_response(self, msg_body):
        """ received inventory response, add info to current inventory """
        # print(">>> inventory response: " + str(msg_body.mqtt_node_id))
        node_inventory = Inventory(msg_body.mqtt_metadata)
        # print(">>>\n\n inv response: " + str(node_inventory))
        self.inventory.remove_node_inventory(msg_body.mqtt_node_id)
        self.inventory.add_node_inventory(msg_body.mqtt_node_id,
                                          node_inventory)
        # remove any old state for items no longer served by this node
        #node_item_list = self.inventory.build_node_item_list(
        #    msg_body.mqtt_node_id)
        #print(">>> node items:" + str(node_item_list))
        #if self.sensor_states is not None:
        #    self.__sync_inventory_states(msg_body.node_id)
        self.inventory_changed = True

    def __process_traffic_control_switch_message(self, msg_body=None):
        """ process for control switch requests """
        # print(">>> traffic control msg: " + str(msg_body.mqtt_desired))
        reported = Global.ERROR
        data_reported = None
        message = Global.MSG_ERROR_BAD_DESIRED
        if msg_body.mqtt_port_id == Global.TRAFFIC:
            if msg_body.mqtt_publisher is None or \
                    msg_body.mqtt_publisher not in self.admin_nodes:
                message = Global.MSG_ERROR_BAD_NODE_ID
                data_reported = Global.ERROR
            else:
                desired = msg_body.mqtt_desired
                if Synonyms.is_on(desired):
                    self.central_traffic_control_enabled = True
                    reported = Global.ON
                    data_reported = reported
                    message = None
                    data_reported = reported
                elif Synonyms.is_off(desired):
                    self.central_traffic_control_enabled = False
                    reported = Global.OFF
                    data_reported = reported
                    message = None
                msg_body.mqtt_reported = data_reported
                self.__update_sensor_state(msg_body)
        if message is not None:
            self.log_warning("Error: traffic control enabled could not be set: "+str(message))
        print(">>> ... "+str(data_reported)+" : "+str(message))
        self.inventory_changed = True
        self.__publish_responses(msg_body, reported, message, data_reported)

    def __process_auto_signals_switch_message(self, msg_body=None):
        """ process for auto signal switch requests """
        #print(">>> auto signals msg: " + str(msg_body.mqtt_desired))
        reported = Global.ERROR
        data_reported = None
        message = Global.MSG_ERROR_BAD_DESIRED
        if msg_body.mqtt_port_id == Global.AUTO_SIGNALS:
            if msg_body.mqtt_publisher is None or \
                    msg_body.mqtt_publisher not in self.admin_nodes:
                message = Global.MSG_ERROR_BAD_NODE_ID
            else:
                desired = msg_body.mqtt_desired
                if Synonyms.is_on(desired):
                    self.auto_signals_enabled = True
                    reported = Global.ON
                    message = None
                    data_reported = reported
                elif Synonyms.is_off(desired):
                    self.auto_signals_enabled = False
                    reported = Global.OFF
                    message = None
                    data_reported = reported
                msg_body.mqtt_reported = data_reported
                self.__update_sensor_state(msg_body)
        if message is not None:
            self.log_warning("Error: auto signals enabled could not be set: "+str(message))
            print(">>> admins: "+str(self.admin_nodes) + " : "+str(msg_body.mqtt_publisher))
        #print(">>> ... "+str(data_reported)+" : "+str(message))
        self.__publish_responses(msg_body, reported, message, data_reported)

    def __generate_empty_inventory_report(self, group=None):
        """ generate an empty report data for a group """
        # print(">>> generate empty inventory")
        rett = {Global.INVENTORY: {
            Global.DESCRIPTION: Global.INVENTORY, Global.INVENTORY: {group: {}}}}
        return rett

    def __generate_inventory_report(self, group=None):
        """ generate report data for a group """
        # print(">>> generate inventory")
        rett = None
        if self.inventory is not None:
            rett = self.inventory.encode(requested_group=group)
        return rett

    def __update_sensor_state(self, msg_body):
        """ up the state of a sensor, switch, etc """
        sensor_data = InventoryData()
        sensor_data.parse_mqtt_message(msg_body)

        if self.inventory is not None:
            group = msg_body.mqtt_message_root
            if not self.inventory.sensor_data_momentary(group, sensor_data):
                #print(">>> update sensor: " + str(sensor_data.key)+  \
                #        " : "+str(sensor_data.reported) +
                #        " : "+str(group))
                self.inventory.update_sensor_state(group,
                                                       sensor_data)
                self.signals_manager.update_signals(
                    group, sensor_data)
                self.cab_signals_manager.update_signals(
                    group, sensor_data)
                self.routes_manager.update_routes(
                    group, sensor_data)

    def __publish_responses(self, msg_body, reported, message, data_reported):
        """ format and publish responses """
        # print(">>> response: " + str(reported))
        metadata = None
        if message is not None:
            metadata = {Global.MESSAGE: message}
        self.app_queue.put((Global.PUBLISH, {
            Global.TYPE: Global.RESPONSE,
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


    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse pub topics of config file """
        node_topic = mqtt_config.publish_topics.get(Global.NODE,
                                                    Global.UNKNOWN)
        tower_topic = mqtt_config.publish_topics.get(Global.TOWER,
                                                     Global.UNKNOWN)
        tower_sub_topic = mqtt_config.subscribe_topics.get(Global.TOWER,
                                                           Global.UNKNOWN)
        self_topic = mqtt_config.subscribe_topics.get(Global.SELF,
                                                      Global.UNKNOWN)
        switch_topic = mqtt_config.publish_topics.get(Global.SWITCH,
                                                      Global.UNKNOWN)
        route_topic = mqtt_config.subscribe_topics.get(Global.ROUTE,
                                                      Global.UNKNOWN)
        route_data_topic = mqtt_config.publish_topics.get(Global.ROUTE,
                                                      Global.UNKNOWN)
        return (node_topic, self_topic, tower_topic, \
            tower_sub_topic, switch_topic, route_topic, route_data_topic)

    def __parse_mqtt_options_traffic(self, config):
        """ parse traffic control and auto signals params from config """
        traffic_enabled = False
        auto_signals_enabled = True
        admins = []
        if Global.CONFIG in config:
            if Global.OPTIONS in config[Global.CONFIG]:
                if Global.CONTROL in config[Global.CONFIG][Global.OPTIONS]:
                    control  = config[Global.CONFIG][Global.OPTIONS][Global.CONTROL]
                    print(">>> control: "+str(control))
                    if Global.TRAFFIC in control:
                        traffic_param = control[Global.TRAFFIC]
                        traffic_enabled = bool(Synonyms.is_on(traffic_param))
                    if Global.AUTO_SIGNALS in control:
                        auto_signals_param = control[Global.AUTO_SIGNALS]
                        auto_signals_enabled = bool(Synonyms.is_on(auto_signals_param))
                    if Global.ADMIN+"-"+Global.NODES in control:
                        admins = control[Global.ADMIN+"-"+Global.NODES]
        return (traffic_enabled, auto_signals_enabled, admins)


    def __process_route_request(self, msg_body):
        """ a route request was received """
        self.routes_manager.set_route_switches(msg_body)

    def __init_signals_manager(self):
        """ initialize the signals manager """
        self.signals_manager = SignalsManager(self)

    def __init_cab_signals_manager(self):
        """ initialize cab signals manager """
        self.cab_signals_manager = CabSignalsManager(self)

    def __init_routes_manager(self):
        self.routes_manager = RoutesManager(self)
        self.routes_manager.initialize_routes()

    def __publish_inventory_changed(self):
        """ send a data message notifing inventory has changed """
        self.log_info("Publish Inventory changed...")
        topic = self.mqtt_config.publish_topics.get(Global.INVENTORY,
                                                    Global.UNKNOWN)
        data_msg_body = IoData()
        data_msg_body.mqtt_message_root = Global.TOWER
        data_msg_body.mqtt_node_id = self.get_topic_node_id(topic)
        data_msg_body.mqtt_port_id = Global.INVENTORY
        data_msg_body.mqtt_reported = Global.CHANGED
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.DATA,
                                             Global.TOPIC: topic,
                                             Global.BODY: data_msg_body}))
