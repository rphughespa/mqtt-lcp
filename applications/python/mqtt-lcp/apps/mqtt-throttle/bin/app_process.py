#!/usr/bin/python3
# app_process.py
"""


app_process - the application process for mqtt-throttle


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


import sys
import time
# import copy

sys.path.append('../lib')


from utils.global_constants import Global
from utils.global_synonyms import Synonyms
from utils.utility import Utility

from structs.inventory import Inventory
from structs.gui_message import GuiMessage
from structs.gui_message import GuiMessageEnvelope
from structs.io_data import IoData
from structs.roster import Roster

from processes.base_mqtt_process import BaseMqttProcess
from processes.base_process import SendAfterMessage


class AppProcess(BaseMqttProcess):
    """ Class that waits for an event to occur """

    def __init__(self, events=None, queues=None):
        super().__init__(name="app",
                         events=events,
                         in_queue=queues[Global.APPLICATION],
                         mqtt_queue=queues[Global.MQTT],
                         log_queue=queues[Global.LOGGER])
        self.log_info("Starting")
        self.throttle_id = "pi-throttle"
        self.device_queue = queues[Global.DEVICE]
        self.cab_pub_topic = None
        self.fastclock_pub_topic = None
        self.respond_to_topic = None
        self.socket_child_pairs = {}
        self.switches = {}
        self.routes = {}
        self.signals = {}
        self.sensors = {}
        self.throttle_ping_send_after_message = None
        self.traffic_control = False
        self.auto_signals = False

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        self.log_info("Init socket server")
        (self.cab_pub_topic, self.fastclock_pub_topic,
         self.respond_to_topic) \
            = self.__parse_mqtt_options_config(self.mqtt_config)
        self.publish_roster_report_request(Global.ROSTER)
        self.__publish_tower_report_requests()
        self.throttle_ping_send_after_message = \
            SendAfterMessage(Global.THROTTLE + ":" + Global.PING, None,
                             5000)  # call throttle_ping method every 5 seconds
        self.send_after(self.throttle_ping_send_after_message)

    def process_message(self, new_message=None):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            # print(">>> new message: " + str(new_message))
            (msg_type, msg_body) = new_message
            # print("())() "+str(log_message))
            if msg_type == Global.THROTTLE + ":" + Global.PING:
                self.send_after(self.throttle_ping_send_after_message)
                self.__send_throttle_pings()
                msg_consummed = True
            elif msg_type == Global.PUBLISH:
                # print(">>> app publish: " + str(msg_body))
                if isinstance(msg_body, GuiMessage):
                    msg_consummed = self.__process_publish_messages(msg_body)
                msg_consummed = True
            if not msg_consummed:
                self.log_warning("Unknown Message TYpe Received: " +
                                 str(new_message))
                msg_consummed = True
        return msg_consummed

    def process_other(self):
        """ perform other none message relared tasks """
        super().process_other()
        _now = time.mktime(time.localtime())
        # if now > self.exit_time:
        #    print("crashing app_process")
        #    raise ValueError("app_process - time expired")

    def process_response_roster_report_message(self, msg_body=None):
        """ process response roster message """
        # print(">>> roster message has been received...")
        self.log_info(Global.RECEIVED+": "+ Global.ROSTER)
        super().process_response_roster_report_message(msg_body=msg_body)
        roster_map = {}
        #print(">>> roster: " + str(self.roster))
        if self.roster is not None:
            for _key, loco in self.roster.locos.items():
                roster_item = GuiMessage()
                roster_item.name = loco.name
                roster_item.text = loco.description
                roster_item.dcc_id = loco.dcc_id
                roster_item.image = loco.image
                roster_map[roster_item.dcc_id] = roster_item

        self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.ROSTER,
                                            cab=Global.CAB_ALL,
                                            msg_data=roster_map))
        return True

    def process_response_inventory_message(self, msg_body=None):
        """ process inventory response message """
        self.log_info(Global.RECEIVED+": "+Global.INVENTORY)
        inventory_map = None
        meta = msg_body.mqtt_metadata
        if meta is not None:
            inventory_map = meta.get(Global.INVENTORY, None)
        if inventory_map is None:
            # not a roster response, pass it to super instance
            self.log_error("No Inventory found in tower response: " +
                           str(meta))
        else:
            # found an inventory
            inventory = Inventory({Global.INVENTORY: inventory_map})
            self.__process_signal_inventory(inventory)
            self.__process_switch_inventory(inventory)
            self.__process_route_inventory(inventory)
            self.__process_sensor_inventory(inventory)
            self.__process_inventory_states(inventory)

        return True

    def process_data_signal_message(self, msg_body=None):
        """ process a signal message """
        # print(">>> data signal: " + str(msg_body))
        if msg_body.mqtt_message_root == Global.SIGNAL:
            dcc_id = msg_body.mqtt_loco_id
            if dcc_id is not None:
                # got a cab signal data message
                mode = msg_body.mqtt_reported
                gui_message = GuiMessage()
                gui_message.command = Global.SIGNAL
                gui_message.dcc_id = dcc_id
                gui_message.mode = mode
                gui_message_envelope = GuiMessageEnvelope()
                gui_message_envelope.msg_type = Global.SIGNAL
                gui_message_envelope.msg_data = gui_message
                self.__send_message_to_tk(gui_message_envelope)
                self.__send_group_message(Global.SIGNAL, Global.REFRESH)
                self.log_info(Global.RECEIVED + ": " + Global.SIGNAL+" : "+\
                              str(gui_message.port_id)+" : "+str(gui_message.mode))
        return True

    def process_data_locator_message(self, msg_body=None):
        """ process locator messages """
        # print(">>> locator message: " + str(msg_body.mqtt_loco_id) + " ... " + str(msg_body.mqtt_port_id))
        if msg_body.mqtt_message_root == Global.LOCATOR:
            _mode = msg_body.mqtt_reported
            gui_message = GuiMessage()
            gui_message.command = Global.LOCATOR
            gui_message.dcc_id = msg_body.mqtt_loco_id
            gui_message.port_id = msg_body.mqtt_port_id
            gui_message.node_id = msg_body.mqtt_node_id
            gui_message.mode = msg_body.mqtt_reported
            gui_message.sub_command = Global.RAILCOM
            if msg_body.mqtt_metadata is not None:
                mtype = msg_body.mqtt_metadata.get(Global.TYPE, None)
                gui_message.sub_command = mtype
            gui_message_envelope = GuiMessageEnvelope()
            gui_message_envelope.msg_type = Global.LOCATOR
            gui_message_envelope.msg_data = gui_message
            self.__send_message_to_tk(gui_message_envelope)
            self.__send_group_message(Global.LOCATOR, Global.REFRESH)
            self.log_info(Global.RECEIVED + ": " + Global.LOCATOR+" : "+\
                            str(gui_message.dcc_id)+" : "+str(gui_message.port_id) +" : "+\
                            str(gui_message.mode))
        return True

    def process_data_sensor_message(self, msg_body=None):
        """ process a switch message """
        #print(">>> data sensor")
        return True

    def process_data_block_message(self, msg_body=None):
        """ process a block message """
        #print(">>> data block")
        return True

    def process_data_switch_message(self, msg_body=None):
        """ process a sensor message """
        #print(">>> switch data: "+str(msg_body.mqtt_message_root) + " : " +\
        #            str(msg_body.mqtt_port_id))
        if msg_body.mqtt_message_root == Global.SWITCH:
            if msg_body.mqtt_port_id == Global.POWER:
                # print(">>> switch data")
                power_message = GuiMessage()
                power_message.command = Global.SWITCH
                power_message.port_id = Global.POWER
                power_message.mode = msg_body.mqtt_reported
                self.__send_message_to_tk(GuiMessageEnvelope(
                    msg_type=Global.POWER, msg_data=power_message))
                message = "Power: " + str(msg_body.mqtt_reported)
                self.__send_message_to_tk(GuiMessageEnvelope(
                    msg_type=Global.MESSAGE, msg_data=message))
                self.log_info(Global.RECEIVED + ": " + Global.POWER)
            elif msg_body.mqtt_port_id == Global.TRAFFIC:
                self.traffic_control = Synonyms.is_on(msg_body.mqtt_reported)
                # print(">>> traffic: " + str(self.traffic_control))
                self.__publish_tower_report_requests()
            elif msg_body.mqtt_port_id == Global.AUTO_SIGNALS:
                self.auto_signals = Synonyms.is_on(msg_body.mqtt_reported)
            else:
                # print(">>> switch data, not power")
                switch_message = GuiMessage()
                switch_message.command = Global.SWITCH
                switch_message.port_id = msg_body.mqtt_port_id
                switch_message.node_id = msg_body.mqtt_node_id
                switch_message.mode = msg_body.mqtt_reported
                self.__send_message_to_tk(GuiMessageEnvelope(
                    msg_type=Global.SWITCH, msg_data=switch_message))
                message = Global.SWITCH + ": " \
                    + str(msg_body.mqtt_port_id) + ": " \
                    + str(msg_body.mqtt_reported)
                self.__send_message_to_tk(GuiMessageEnvelope(
                    msg_type=Global.MESSAGE, msg_data=message))
                self.__send_group_message(Global.SWITCH, Global.REFRESH)
                self.log_info(Global.RECEIVED + ": " + Global.SWITCH+" : "+\
                              str(switch_message.port_id)+" : "+str(switch_message.mode))
        return True

    def process_data_cab_message(self, msg_body=None):
        """ process data cab message """
        if msg_body.mqtt_reported == Global.STOLEN:
            message = "Loco: " + str(msg_body.mqtt_cab_id) + ": " \
                + str(msg_body.mqtt_loco_id) + ": " + \
                str(msg_body.mqtt_reported)
            self.__send_message_to_tk(GuiMessageEnvelope(
                msg_type=Global.MESSAGE, msg_data=message))
            self.log_info("rcv: " + message)
            self.__send_message_to_tk(GuiMessageEnvelope(
                msg_type=Global.STOLEN,
                cab=msg_body.mqtt_cab_id,
                msg_data=msg_body.mqtt_loco_id))
        else:
            self.log_unexpected_message(msg_body=msg_body)
        return True

    def process_data_fastclock_message(self, msg_body=None):
        """ process a fastclock message"""
        self.log_info(Global.RECEIVED+": "+str(msg_body.mqtt_desired) +
                      " ... " + str(msg_body.mqtt_port_id))
        fastclock = None
        if msg_body.mqtt_metadata is not None:
            if Global.FASTCLOCK in msg_body.mqtt_metadata:
                fastclock = msg_body.mqtt_metadata[Global.FASTCLOCK]
        if fastclock is not None:
            self.__send_message_to_tk(
                GuiMessageEnvelope(msg_type=Global.FASTCLOCK, msg_data=fastclock))
        return True

    def process_data_route_message(self, msg_body=None):
        """ process a route message """
        # print(">>> data route: " + str(msg_body))
        if msg_body.mqtt_message_root == Global.ROUTE:
            signal_message = GuiMessage()
            signal_message.command = Global.ROUTE
            signal_message.port_id = msg_body.mqtt_port_id
            signal_message.node_id = msg_body.mqtt_node_id
            signal_message.mode = msg_body.mqtt_reported
            self.__send_message_to_tk(GuiMessageEnvelope(
                msg_type=Global.ROUTE, msg_data=signal_message))
            self.__send_group_message(Global.ROUTE, Global.REFRESH)
            self.log_info(Global.RECEIVED + ": " + Global.ROUTE+" : "+\
                        str(signal_message.port_id)+" : "+str(signal_message.mode))
        return True

    def process_data_cab_signal_message(self, msg_body=None):
        """ process a cab signal message"""
        self.log_info(Global.RECEIVED+": "+str(msg_body.mqtt_port_id) +\
                      " ... " + str(msg_body.mqtt_loco_id) + " : " +\
                        str(msg_body.mqtt_reported))
        cab_signal_map = GuiMessage()
        cab_signal_map.dcc_id = msg_body.mqtt_loco_id
        cab_signal_map.mode = msg_body.mqtt_reported
        self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.CAB_SIGNAL,
                                    cab=Global.CAB_ALL,
                                    msg_data=cab_signal_map))

        return True

    def process_response_switch_message(self, _msg_body=None):
        """ process a switch response """
        # ignore response
        return True

    def process_response_fastclock_message(self, msg_body=None):
        """ fastclock response received """
        message = Global.FASTCLOCK + ": " + str(msg_body.mqtt_reported)
        self.__send_message_to_tk(GuiMessageEnvelope(
            msg_type=Global.MESSAGE, msg_data=message))
        return True

    def process_response_cab_message(self, msg_body=None):
        """ process response cab message """
        # print(">>> cab response: " + str(msg_body))
        msg_consummed = False
        if msg_body.mqtt_desired in [Global.CONNECT, Global.DISCONNECT]:
            message = "Throttle: " + str(msg_body.mqtt_reported)
            self.__send_message_to_tk(GuiMessageEnvelope(
                msg_type=Global.MESSAGE, msg_data=message))
            self.log_info("rcv: " + message)
            msg_consummed = True
        elif msg_body.mqtt_desired in [Global.ACQUIRE]:
            if msg_body.mqtt_reported == Global.STEAL_NEEDED:
                self.__send_message_to_tk(GuiMessageEnvelope(
                    msg_type=Global.STEAL_NEEDED,
                    cab=msg_body.mqtt_cab_id,
                    msg_data=msg_body.mqtt_loco_id))
            else:
                message = "Loco: " + str(msg_body.mqtt_cab_id) + ": " \
                    + str(msg_body.mqtt_loco_id) + ": " + \
                    str(msg_body.mqtt_reported)
                self.__send_message_to_tk(GuiMessageEnvelope(
                    msg_type=Global.MESSAGE, msg_data=message))
                self.log_info("rcv: " + message)
            msg_consummed = True
        elif msg_body.mqtt_desired in [Global.STEAL]:
            message = "Loco: " + str(msg_body.mqtt_cab_id) + ": " \
                + str(msg_body.mqtt_loco_id) + ": " + \
                str(msg_body.mqtt_reported)
            self.__send_message_to_tk(GuiMessageEnvelope(
                msg_type=Global.MESSAGE, msg_data=message))
            self.log_info("rcv: " + message)
            msg_consummed = True
        elif msg_body.mqtt_desired == Global.RELEASE:
            message = "Loco: " + str(msg_body.mqtt_cab_id) + ": " \
                + str(msg_body.mqtt_loco_id) + ": " + \
                str(msg_body.mqtt_reported)
            self.__send_message_to_tk(GuiMessageEnvelope(
                msg_type=Global.MESSAGE, msg_data=message))
            self.log_info("rcv: " + message)
            msg_consummed = True
        elif isinstance(msg_body.mqtt_desired, dict):
            speed = msg_body.mqtt_desired.get(Global.SPEED, None)
            direction = msg_body.mqtt_desired.get(Global.DIRECTION, None)
            if speed is not None or direction is not None:
                gui_message = GuiMessage()
                gui_message.cab_id = msg_body.mqtt_cab_id
                gui_message.dcc_id = msg_body.mqtt_loco_id
                gui_message_envelope = GuiMessageEnvelope()
                gui_message_envelope.msg_type = Global.SPEED
                if speed is not None:
                    gui_message.command = Global.SPEED
                    gui_message.speed = speed
                    gui_message_envelope.msg_type = Global.SPEED
                elif direction is not None:
                    gui_message.command = Global.DIRECTION
                    gui_message.direction = direction
                    gui_message_envelope.type = Global.DIRECTION
                gui_message_envelope.msg_data = gui_message
                gui_message_envelope.cab = msg_body.mqtt_cab_id
                self.__send_message_to_tk(gui_message_envelope)
                msg_consummed = True
            elif msg_body.mqtt_desired.get(Global.FUNCTION, None) is not None:
                message = Global.CAB + ": " + str(msg_body.mqtt_cab_id) + ": " \
                    + Global.LOCO + ": " + str(msg_body.mqtt_loco_id) + ": " \
                    + str(msg_body.mqtt_reported)
                self.__send_message_to_tk(GuiMessageEnvelope(
                    msg_type=Global.MESSAGE, msg_data=message))
                self.log_info("rcv: " + message)
                msg_consummed = True
        return msg_consummed

    def process_data_roster_message(self, msg_body=None):
        """ process data roster message """
        self.log_info("roster data received: "+str(msg_body.mqtt_port_id)+" ... "+str(msg_body.mqtt_reported))
        if msg_body.mqtt_reported == Global.CHANGED:
            # roster has changed, request the roster
            self.publish_roster_report_request(Global.ROSTER)
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_tower_message(self, msg_body=None):
        """ process data tower message """
        self.log_info("tower data received: "+str(msg_body.mqtt_port_id)+" ... "+str(msg_body.mqtt_reported))
        if msg_body.mqtt_port_id == Global.INVENTORY and \
                msg_body.mqtt_reported == Global.CHANGED:
            # inventory has changed, request the inventory
            self.__publish_tower_report_requests()
        else:
            self.log_unexpected_message(msg_body=msg_body)
        return True

    #
    # private functions
    #


    def __publish_tower_report_requests(self):
        """ request inventory reports from tower """
        self.publish_tower_report_request(Global.INVENTORY)

    def __publish_power_request(self, gui_message):
        """ request power from mqtt-dcc-command """
        desired = gui_message.mode
        self.log_info(Global.PUBLISH + ": " +
                      Global.POWER + ": " + str(desired))
        now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(Global.POWER, \
                                                Global.UNKNOWN) + "/" +\
                                                Global.POWER + "/req"
        body = IoData()
        body.mqtt_message_root = Global.SWITCH
        body.mqtt_node_id = self.node_name
        body.mqtt_port_id = Global.POWER
        body.mqtt_desired = desired
        # response not needed, will monitor "dt" sensor message
        body.mqtt_respond_to = None
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(
            topic=topic,
            message_io_data=body)

    def __process_inventory_initialize(self):
        """ send message to screen to init their inventory"""
        msg_map = GuiMessage()
        msg_map.name = Global.INVENTORY
        msg_map.mode = Global.CLEAR
        # print(">>> switch: " + str(switch_map))
        self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.INVENTORY,
                                            cab=Global.CAB_ALL,
                                            msg_data=msg_map))

    def __send_group_message(self, group, mode):
        """ send a message for a group """
        message = GuiMessage()
        message.name = Global.INFO_COMMAND
        message.mode = mode
        self.__send_message_to_tk(GuiMessageEnvelope(msg_type=group,
                                                    cab=Global.CAB_ALL,
                                                    msg_data=message))

    def __process_sensor_inventory(self, inventory):
        """ send sensor inventory to screens """
        self.__send_group_message(Global.SENSOR, Global.CLEAR)
        sensor_group = inventory.inventory_groups.get(Global.SENSOR, None)
        self.sensors = {}
        if sensor_group is not None:
            # print(">>> switch map: " + str(switch_group))
            for _k, sensor in sensor_group.inventory_items.items():
                # print(">>> item: " + str(switch))
                sensor_map = GuiMessage()
                sensor_map.name = sensor.key
                sensor_map.node_id = sensor.node_id
                sensor_map.port_id = sensor.port_id
                sensor_map.block_id = sensor.block_id
                sensor_map.dcc_id = sensor.loco_id
                sensor_map.mode = sensor.reported
                # print(">>> switch: " + str(switch_map))
                self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.SENSOR,
                                                    cab=Global.CAB_ALL,
                                                    msg_data=sensor_map))
        self.__send_group_message(Global.SENSOR, Global.REFRESH)

    def __process_switch_inventory(self, inventory):
        """ send switch inventory to screens """
        self.__send_group_message(Global.SWITCH, Global.CLEAR)
        switch_group = inventory.inventory_groups.get(Global.SWITCH, None)
        self.switches = {}
        if switch_group is not None:
            # print(">>> switch map: " + str(switch_group))
            for _k, switch in switch_group.inventory_items.items():
                # print(">>> item: " + str(switch))
                switch_map = GuiMessage()
                switch_map.name = switch.key
                switch_map.node_id = switch.node_id
                switch_map.port_id = switch.port_id
                switch_map.text = switch.command_topic
                switch_map.block_id = switch.block_id
                switch_map.dcc_id = switch.loco_id
                switch_map.mode = switch.reported
                self.switches[switch.key] = switch_map
                # print(">>> switch: " + str(switch_map))
                self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.SWITCH,
                                                    cab=Global.CAB_ALL,
                                                    msg_data=switch_map))
        self.__send_group_message(Global.SWITCH, Global.REFRESH)

    def __process_signal_inventory(self, inventory):
        """ send signal inventory to screens """
        self.__send_group_message(Global.SIGNAL, Global.CLEAR)
        signal_group = inventory.inventory_groups.get(Global.SIGNAL, None)
        self.signals = {}
        if signal_group is not None:
            # print(">>> signal map: " + str(signal_group))
            for _k, signal in signal_group.inventory_items.items():
                # print(">>> item: " + str(signal))
                signal_map = GuiMessage()
                signal_map.name = signal.key
                signal_map.node_id = signal.node_id
                signal_map.port_id = signal.port_id
                signal_map.block_id = signal.block_id
                signal_map.direction = signal.direction
                signal_map.text = signal.command_topic
                signal_map.block_id = signal.block_id
                signal_map.dcc_id = signal.loco_id
                signal_map.mode = signal.reported
                # print(">>> signal: " + str(signal))
                # print(">>> signal map: " + str(signal_map))
                self.signals[signal.key] = signal_map
                self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.SIGNAL,
                                                    cab=Global.CAB_ALL,
                                                    msg_data=signal_map))
        self.__send_group_message(Global.SIGNAL, Global.REFRESH)

    def __process_route_inventory(self, inventory):
        """ send soute inventory to screens """
        self.__send_group_message(Global.ROUTE, Global.CLEAR)
        route_group = inventory.inventory_groups.get(Global.ROUTE, None)
        self.routes = {}
        if route_group is not None:
            # print(">>> route map: " + str(route_group))
            for _k, route in route_group.inventory_items.items():
                # print(">>> item: " + str(route))
                route_map = GuiMessage()
                route_map.name = route.key
                route_map.node_id = route.node_id
                route_map.port_id = route.port_id
                route_map.text = route.command_topic
                route_map.block_id = route.block_id
                route_map.dcc_id = route.loco_id
                route_map.mode = route.reported
                self.routes[route.key] = route_map
                # print(">>> route: " + str(route))
                self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.ROUTE,
                                                cab=Global.CAB_ALL,
                                                msg_data=route_map))
        self.__send_group_message(Global.ROUTE, Global.REFRESH)

    def __process_inventory_states(self, inventory):
        """ process inventory states """
        # print(">>> states: " + str(states))
        for group_id, group in inventory.inventory_groups.items():
            # print(">>> group id:" +str(group_id))
            # print(">>> group: "+ str(group))
            for _inv_key, item in group.inventory_items.items():
                #print(">>> item id: " + str(item.port_id) + " : " + \
                #        str(item.reported) + " : "+str(item.loco_id))
                state_message = GuiMessage()
                state_message.command = group_id
                state_message.port_id = item.port_id
                state_message.node_id = item.node_id
                state_message.block_id = item.block_id
                state_message.dcc_id = item.loco_id
                state_message.mode = item.reported
                self.__send_message_to_tk(GuiMessageEnvelope(
                    msg_type=state_message.command, msg_data=state_message))

    def __send_throttle_pings(self):
        """ send 'pings' to dcc command server """
        self.log_info(Global.PUBLISH + ": " +
                      Global.THROTTLE + " " + Global.PING)
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_desired = Global.PING
        self.publish_request_message(
            topic=self.cab_pub_topic,
            message_io_data=body)

    def __process_publish_messages(self, msg_body):
        """ process publish type messages """
        msg_consummed = False
        if msg_body.command == Global.CONNECT:
            self.__publish_connect_request(msg_body)
            msg_consummed = True
        elif msg_body.command == Global.DISCONNECT:
            self.__publish_disconnect_request(msg_body)
            msg_consummed = True
        elif msg_body.command == Global.THROTTLE:
            msg_consummed = self.__process_publish_gui_messages(msg_body)
        elif msg_body.command == Global.SWITCH:
            if msg_body.port_id == Global.POWER:
                self.__publish_power_request(msg_body)
                msg_consummed = True
            else:
                self.__publish_switch_request(msg_body)
            msg_consummed = True
        elif msg_body.command == Global.ROUTE:
            self.__publish_route_request(msg_body)
            msg_consummed = True
        return msg_consummed

    def __process_publish_gui_messages(self, msg_body):
        """ process publish type messages """
        msg_consummed = False
        if msg_body.sub_command == Global.ACQUIRE:
            self.__publish_acquire_request(msg_body)
            msg_consummed = True
        elif msg_body.sub_command == Global.STEAL:
            self.__publish_steal_request(msg_body)
            msg_consummed = True
        elif msg_body.sub_command == Global.RELEASE:
            self.__publish_release_request(msg_body)
            msg_consummed = True
        elif msg_body.sub_command == Global.SPEED:
            self.__publish_speed_request(msg_body)
            msg_consummed = True
        elif msg_body.sub_command == Global.DIRECTION:
            self.__publish_direction_request(msg_body)
            msg_consummed = True
        elif msg_body.sub_command == Global.FUNCTION:
            self.__publish_function_request(msg_body)
            msg_consummed = True
        return msg_consummed

    def __publish_connect_request(self, _gui_message):
        """ publish a throttle connect command """
        self.log_info(Global.PUBLISH + ": " + Global.CONNECT)
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_desired = Global.CONNECT
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(
            topic=self.cab_pub_topic,
            message_io_data=body)

    def __publish_disconnect_request(self, _gui_message):
        """ publish a throttle connect command """
        self.log_info(Global.PUBLISH + ": " + Global.DISCONNECT)
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_desired = Global.DISCONNECT
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(
            topic=self.cab_pub_topic,
            message_io_data=body)

    def __publish_acquire_request(self, gui_message):
        """ publish a throttle acquire loco command """
        self.log_info(Global.PUBLISH + ": " + Global.ACQUIRE + ": "
                      + str(gui_message.cab_id) + ": "
                      + str(gui_message.dcc_id))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = gui_message.cab_id
        body.mqtt_loco_id = gui_message.dcc_id
        body.mqtt_desired = Global.ACQUIRE
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(
            topic=self.cab_pub_topic,
            message_io_data=body)

    def __publish_steal_request(self, gui_message):
        """ publish a throttle steal loco command """
        self.log_info(Global.PUBLISH + ": " + Global.STEAL + ": "
                      + str(gui_message.cab_id) + ": "
                      + str(gui_message.dcc_id))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = gui_message.cab_id
        body.mqtt_loco_id = gui_message.dcc_id
        body.mqtt_desired = Global.STEAL
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(
            topic=self.cab_pub_topic,
            message_io_data=body)

    def __publish_release_request(self, gui_message):
        """ publish a throttle release loco command """
        self.log_info(Global.PUBLISH + ": " + Global.RELEASE + ": "
                      + str(gui_message.cab_id) + ": "
                      + str(gui_message.dcc_id))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = gui_message.cab_id
        body.mqtt_loco_id = gui_message.dcc_id
        body.mqtt_desired = Global.RELEASE
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(
            topic=self.cab_pub_topic,
            message_io_data=body)

    def __publish_speed_request(self, gui_message):
        """ publish a throttle loco speed command """
        self.log_info(Global.PUBLISH + ": " + Global.SPEED + ": "
                      + str(gui_message.cab_id) + ": "
                      + str(gui_message.dcc_id) + ": "
                      + str(gui_message.speed))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = gui_message.cab_id
        body.mqtt_loco_id = gui_message.dcc_id
        body.mqtt_desired = {Global.SPEED: gui_message.speed}
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(
            topic=self.cab_pub_topic,
            message_io_data=body)

    def __publish_direction_request(self, gui_message):
        """ publish a throttle loco direction command """
        self.log_info(Global.PUBLISH + ": " + Global.DIRECTION + ": "
                      + str(gui_message.cab_id) + ": "
                      + str(gui_message.dcc_id) + ": "
                      + str(gui_message.direction))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = gui_message.cab_id
        body.mqtt_loco_id = gui_message.dcc_id
        body.mqtt_desired = {Global.DIRECTION: gui_message.direction}
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(
            topic=self.cab_pub_topic,
            message_io_data=body)

    def __publish_function_request(self, gui_message):
        """ publish a throttle loco function command """
        self.log_info(Global.PUBLISH + ": " + Global.FUNCTION + ": "
                      + str(gui_message.cab_id) + ": "
                      + str(gui_message.dcc_id) + ": "
                      + str(gui_message.function) + ": "
                      + str(gui_message.mode))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = gui_message.cab_id
        body.mqtt_loco_id = gui_message.dcc_id
        body.mqtt_desired = {Global.FUNCTION: gui_message.function,
                             Global.STATE: gui_message.mode}
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(
            topic=self.cab_pub_topic,
            message_io_data=body)

    def __publish_switch_request(self, gui_message):
        """ request switch change """
        desired = gui_message.mode
        self.log_info(Global.PUBLISH + ": " + Global.SWITCH + ": "
                      + str(gui_message.port_id) + ": " + str(desired))
        now = Utility.now_milliseconds()
        topic = gui_message.text  # command topic
        body = IoData()
        body.mqtt_message_root = Global.SWITCH
        body.mqtt_node_id = self.node_name
        body.mqtt_port_id = gui_message.port_id
        body.mqtt_desired = desired
        # response not needed, will monitor "dt" sensor message
        body.mqtt_respond_to = None
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(
            topic=topic,  # inventory command topic
            message_io_data=body)

    def __publish_route_request(self, gui_message):
        """ request route request """
        desired = gui_message.mode
        now = Utility.now_milliseconds()
        topic = gui_message.text  # command topic
        body = IoData()
        body.mqtt_message_root = Global.ROUTE
        body.mqtt_port_id = gui_message.port_id
        body.mqtt_desired = desired
        # response not needed, will monitor "dt" sensor message
        body.mqtt_respond_to = None
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(
            topic=topic,  # inventory command topic
            message_io_data=body)

    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse time options section of config file """
        cab_pub_topic = mqtt_config.publish_topics.get(Global.CAB,
                                                          Global.UNKNOWN) + "/req"
        fastclock_topic = mqtt_config.publish_topics.get(Global.FASTCLOCK,
                                                         Global.UNKNOWN) + "/req"
        respond_to_topic = mqtt_config.subscribe_topics.get(
            Global.SELF, Global.UNKNOWN)
        respond_to_topic = respond_to_topic.replace("/#", "/res")
        return (cab_pub_topic, fastclock_topic, respond_to_topic)

    def __send_message_to_tk(self, message):
        # forward message to gui display device process
        self.device_queue.put((Global.DEVICE_SEND, message))
