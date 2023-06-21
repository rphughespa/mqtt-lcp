#!/usr/bin/python3
# app_process.py
"""


app_process - the application process for mqtt-dispatcher


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


from utils.utility import Utility
from utils.global_synonyms import Synonyms
from utils.global_constants import Global

from structs.io_data import IoData
from structs.gui_message import GuiMessage
from structs.gui_message import GuiMessageEnvelope
from structs.inventory import Inventory
from structs.dashboard import Dashboard
from structs.panels import Panels

from processes.base_process import SendAfterMessage
from processes.base_mqtt_process import BaseMqttProcess



# from structs.roster import Roster


class AppProcess(BaseMqttProcess):
    """ Class that waits for an event to occur """

    def __init__(self, events=None, queues=None):
        super().__init__(name="app",
                         events=events,
                         in_queue=queues[Global.APPLICATION],
                         mqtt_queue=queues[Global.MQTT],
                         log_queue=queues[Global.LOGGER])
        self.log_info("Starting")
        self.throttle_id = "dispatcher"
        self.device_queue = queues[Global.DEVICE]
        self.dcc_command_pub_topic = None
        self.tower_pub_topic = None
        self.fastclock_pub_topic = None
        self.respond_to_topic = None
        self.socket_child_pairs = {}
        self.switches = {}
        self.signals = {}
        self.routes = {}
        self.sensors = {}
        self.throttle_ping_send_after_message = None
        self.dashboard_request_send_after_message = None


    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        self.log_info("Init socket server")
        (self.dcc_command_pub_topic, self.fastclock_pub_topic,
         self.respond_to_topic) \
            = self.__parse_mqtt_options_config(self.mqtt_config)
        self.publish_roster_report_request(Global.ROSTER)
        self.__publish_tower_report_requests()
        power_message = GuiMessage
        power_message.command = Global.SWITCH
        power_message.port_id = Global.POWER
        power_message.mode = Global.REPORT
        self.__publish_power_request(power_message)
        self.throttle_ping_send_after_message = \
            SendAfterMessage(Global.THROTTLE + ":" + Global.PING, None,
                             5000)  # call throttle_ping method every 5 seconds
        self.send_after(self.throttle_ping_send_after_message)
        self.dashboard_request_send_after_message = \
            SendAfterMessage(Global.DASHBOARD, None, 120000)  # request dasjboard every 2 minutes
        self.send_after(self.dashboard_request_send_after_message)

    def process_message(self, new_message=None):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            # print(">>> new message: " + str(new_message))
            (msg_type, msg_body) = new_message
            # print("())() "+str(log_message))
            if msg_type == Global.DASHBOARD:
                self.publish_tower_report_request(Global.DASHBOARD)
                self.send_after(self.dashboard_request_send_after_message)
                msg_consummed = True
            elif msg_type == Global.PUBLISH:
                # print(">>> app publish: " + str(msg_body))
                if isinstance(msg_body, GuiMessage):
                    msg_consummed = self.__process_publish_messages(msg_body)
                msg_consummed = True
            if not msg_consummed:
                self.log_warning("Unknown Message Type Received: " +
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

    def process_response_roster_message(self, msg_body=None):
        """ process response roster message """
        self.log_info(Global.RECEIVED+": "+Global.ROSTER)
        super().process_response_roster_report_message(msg_body)
        roster_map = {}
        # print(">>> roster: " + str(self.roster))
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

    def process_response_panels_message(self, msg_body=None):
        """ process panels message """
        self.log_info(Global.RECEIVED+": "+Global.PANEL)
        panels_map = None
        meta = msg_body.mqtt_metadata
        if meta is not None:
            panels_map = meta.get(Global.PANEL, None)
        if panels_map is None:
            # not a panels response, pass it to super instance
            self.log_error("No Panels found in tower response: " +
                           str(meta))
        else:
            # found panels
            panels = Panels({Global.PANELS: panels_map})
            self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.PANELS,
                                                msg_data=panels))
        time.sleep(1)  # delay a bit to make sure states is received last
        self.publish_tower_report_request(Global.INVENTORY)
        return True

    def process_response_dashboard_message(self, msg_body=None):
        """ dashboard data message received """
        self.log_info(Global.RECEIVED+": "+Global.DASHBOARD)
        dashboard_map = None
        meta = msg_body.mqtt_metadata
        # print(">>> dashboard meta: " + str(meta))
        if meta is not None:
            dashboard_map = meta.get(Global.DASHBOARD, None)
        if dashboard_map is None:
            # not a dashboard response
            self.log_error("No Dastbaord items found in data message: " +
                           str(meta))
        else:
            # found dashboard
            dashboard = Dashboard({Global.DASHBOARD: dashboard_map})
            self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.DASHBOARD,
                                                msg_data=dashboard))
        return True

    def process_data_signal_message(self, msg_body=None):
        """ process a signal message """
        # print(">>> data signal: " + str(msg_body))
        if msg_body.mqtt_message_root == Global.SIGNAL:
            dcc_id = msg_body.mqtt_loco_id
            if dcc_id is None:
                # not a cab signal data message
                signal_message = GuiMessage()
                signal_message.command = Global.SIGNAL
                signal_message.port_id = msg_body.mqtt_port_id
                signal_message.node_id = msg_body.mqtt_node_id
                signal_message.mode = msg_body.mqtt_reported
                self.__send_message_to_tk(GuiMessageEnvelope(
                    msg_type=Global.SIGNAL, msg_data=signal_message))
                message = Global.SIGNAL + ": " \
                    + str(msg_body.mqtt_port_id) + ": " \
                    + str(msg_body.mqtt_reported)
                self.__send_message_to_tk(GuiMessageEnvelope(
                    msg_type=Global.MESSAGE, msg_data=message))
                self.__send_group_message(Global.SIGNAL, Global.REFRESH)
                self.log_info(Global.RECEIVED + ": " + Global.SIGNAL+" : "+\
                              str(signal_message.port_id)+" : "+str(signal_message.mode))

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


    def process_data_block_message(self, msg_body=None):
        """ process block messages """
        if msg_body.mqtt_message_root == Global.BLOCK:
            _mode = msg_body.mqtt_reported
            gui_message = GuiMessage()
            gui_message.command = Global.BLOCK
            gui_message.block_id = msg_body.mqtt_block_id
            gui_message.mode = msg_body.mqtt_reported
            gui_message.sub_command = Global.BLOCK
            gui_message_envelope = GuiMessageEnvelope()
            gui_message_envelope.msg_type = Global.BLOCK
            gui_message_envelope.msg_data = gui_message
            self.__send_message_to_tk(gui_message_envelope)
            self.log_info(Global.RECEIVED + ": " + Global.BLOCK+" : "+\
                              str(gui_message.port_id)+" : "+str(gui_message.mode))
            self.__send_group_message(Global.BLOCK, Global.REFRESH)
        return True

    def process_data_locator_message(self, msg_body=None):
        """ process locator messages """
        if msg_body.mqtt_message_root == Global.LOCATOR:
            _mode = msg_body.mqtt_reported
            gui_message = GuiMessage()
            gui_message.command = Global.LOCATOR
            gui_message.dcc_id = msg_body.mqtt_loco_id
            gui_message.block_id = msg_body.mqtt_block_id
            gui_message.mode = msg_body.mqtt_reported
            gui_message.sub_command = Global.RAILCOM
            if msg_body.mqtt_metadata is not None:
                mtype = msg_body.mqtt_metadata.get(Global.TYPE, None)
                gui_message.sub_command = mtype
            gui_message_envelope = GuiMessageEnvelope()
            gui_message_envelope.msg_type = Global.LOCATOR
            gui_message_envelope.msg_data = gui_message
            self.__send_message_to_tk(gui_message_envelope)
            self.log_info(Global.RECEIVED + ": " + Global.LOCATOR+" : "+\
                            str(gui_message.dcc_id)+" : "+str(gui_message.block_id) +" : "+\
                            str(gui_message.mode))
            self.__send_group_message(Global.LOCATOR, Global.REFRESH)
        return True

    def process_response_switch_message(self, msg_body=None):
        """ process a switch response """
        # ignore response
        return True

    def process_data_sensor_message(self, msg_body=None):
        """ process a switch message """
        # print(">>> data sensor")
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

    def process_data_switch_message(self, msg_body=None):
        """ process a sensor message """
        # print(">>> switch data")
        if msg_body.mqtt_message_root == Global.SWITCH:
            if msg_body.mqtt_port_id == Global.POWER:
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
                self.log_info(Global.RECEIVED + ": " + Global.SWITCH+" : "+\
                              str(switch_message.port_id)+" : "+str(switch_message.mode))
            self.__send_group_message(Global.SWITCH, Global.REFRESH)
        return True

    def process_data_cab_signal_message(self, msg_body=None):
        """ a cab signal has been received"""
        # ignore cab signals
        rett = True
        return rett

    def process_data_tower_message(self, msg_body=None):
        """ a data message received from tower """
        rett = False
        self.log_info("Tower Data Rcvd: " + str(msg_body.mqtt_desired) + " : " +\
                        str(msg_body.mqtt_reported) + " : "+ \
                        str(msg_body.mqtt_port_id))
        if msg_body.mqtt_port_id == Global.INVENTORY:
            rett = self.__process_data_tower_inventory_message(msg_body)
        elif msg_body.mqtt_port_id == Global.DASHBOARD:
            rett = self.__process_data_tower_dashboard_message(msg_body)
        elif msg_body.mqtt_port_id == Global.TRAFFIC or \
                msg_body.mqtt_port_id == Global.AUTO_SIGNALS:
            self.__forward_tower_data(msg_body)
            rett = True
        return rett

    def process_response_fastclock_message(self, msg_body=None):
        """ fastclock response received """
        message = Global.FASTCLOCK + ": " + str(msg_body.mqtt_reported)
        self.__send_message_to_tk(GuiMessageEnvelope(
            msg_type=Global.MESSAGE, msg_data=message))
        return True

    #
    # private functions
    #

    def __forward_tower_data(self, msg_body):
        """ forward tower data mesage to screens """
        state_message = GuiMessage()
        state_message.command = Global.TOWER
        state_message.port_id = msg_body.mqtt_port_id
        state_message.node_id = msg_body.mqtt_node_id
        state_message.mode = msg_body.mqtt_reported
        self.__send_message_to_tk(GuiMessageEnvelope(
            msg_type=state_message.command, msg_data=state_message))

    def __process_inventory_initialize(self):
        """ send message to screen to init their inventory"""
        msg_map = GuiMessage()
        msg_map.name = Global.INVENTORY
        msg_map.mode = Global.CLEAR
        # print(">>> switch: " + str(switch_map))
        self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.INVENTORY,
                                            cab=Global.CAB_ALL,
                                            msg_data=msg_map))

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

    def __publish_tower_report_requests(self):
        """ request inventory reports from tower """
        self.publish_tower_report_request(Global.PANEL)
        self.publish_tower_report_request(Global.DASHBOARD)

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
                switch_map.mode = Global.UNKNOWN
                self.switches[switch.key] = switch_map
                # print(">>> switch: " + str(switch_map))
                self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.SWITCH,
                                                    cab=Global.CAB_ALL,
                                                    msg_data=switch_map))
        self.__send_group_message(Global.SWITCH, Global.REFRESH)

    def __process_route_inventory(self, inventory):
        """ send route inventory to screens """
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
                route_map.mode = Global.UNKNOWN
                self.routes[route.key] = route_map
                # print(">>> route: " + str(route))
                self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.ROUTE,
                                                    cab=Global.CAB_ALL,
                                                    msg_data=route_map))
        self.__send_group_message(Global.ROUTE, Global.REFRESH)

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
                signal_map.mode = Global.UNKNOWN
                # print(">>> signal: " + str(signal))
                # print(">>> signal map: " + str(signal_map))
                self.signals[signal.key] = signal_map
                self.__send_message_to_tk(GuiMessageEnvelope(msg_type=Global.SIGNAL,
                                                    cab=Global.CAB_ALL,
                                                    msg_data=signal_map))
        self.__send_group_message(Global.SIGNAL, Global.REFRESH)

    def __process_publish_messages(self, msg_body):
        """ process publish type messages """
        msg_consummed = False
        if msg_body.command == Global.SWITCH:
            if msg_body.port_id == Global.POWER:
                self.__publish_power_request(msg_body)
                msg_consummed = True
            else:
                self.__publish_switch_request(msg_body)
                msg_consummed = True
        elif msg_body.command == Global.TOWER:
            if msg_body.port_id == Global.TRAFFIC:
                self.__publish_traffic_request(msg_body)
                msg_consummed = True
            elif msg_body.port_id == Global.AUTO_SIGNALS:
                self.__publish_auto_signals_request(msg_body)
                msg_consummed = True
        elif msg_body.command == Global.SIGNAL:
            self.__publish_signal_request(msg_body)
            msg_consummed = True
        elif msg_body.command == Global.ROUTE:
            self.__publish_route_request(msg_body)
            msg_consummed = True
        elif msg_body.command == Global.NODE:
            self.__publish_node_request(msg_body)
            msg_consummed = True
        elif msg_body.command == Global.FASTCLOCK:
            self.__publish_fastclock_request(msg_body)
            msg_consummed = True
        return msg_consummed


    def __publish_switch_request(self, gui_message):
        """ request switch change """
        desired = gui_message.mode
        now = Utility.now_milliseconds()
        topic = gui_message.text  # command topic
        body = IoData()
        body.mqtt_message_root = Global.SWITCH
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

    def __publish_signal_request(self, gui_message):
        """ request signal change """
        desired = gui_message.mode
        now = Utility.now_milliseconds()
        topic = gui_message.text  # command topic
        body = IoData()
        body.mqtt_message_root = Global.SIGNAL
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

    def __publish_power_request(self, gui_message):
        """ request power from mqtt-dcc-command """
        print(">>> power on/off: "+str(gui_message.mode))
        desired = gui_message.mode
        self.log_info(Global.PUBLISH + ": " +
                      Global.POWER + ": " + str(desired))
        now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(Global.POWER,
                                                    Global.UNKNOWN) + "/" + Global.POWER + "/req"
        body = IoData()
        body.mqtt_message_root = Global.SWITCH
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

    def __publish_traffic_request(self, gui_message):
        """ request traffic from mqtt-tower """
        now = Utility.now_milliseconds()
        desired = gui_message.mode
        topic = self.mqtt_config.publish_topics.get(Global.TOWER,
                                                    Global.UNKNOWN)
        topic = topic + "/" + Global.TRAFFIC +"/req"
        body = IoData()
        body.mqtt_message_root = Global.TOWER
        body.mqtt_port_id = Global.TRAFFIC
        body.mqtt_desired = desired
        # response not needed, will monitor "dt" sensor message
        body.mqtt_respond_to = None
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(
            topic=topic,
            message_io_data=body)

    def __publish_auto_signals_request(self, gui_message):
        """ request auto signal from mqtt-tower """
        desired = gui_message.mode
        self.log_info(Global.PUBLISH + ": " +
                      Global.SIGNAL + ": " + str(desired))
        now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(Global.TOWER,
                                                    Global.UNKNOWN)
        topic = topic + "/" + Global.AUTO_SIGNALS +"/req"
        body = IoData()
        body.mqtt_message_root = Global.TOWER
        body.mqtt_port_id = Global.AUTO_SIGNALS
        body.mqtt_desired = desired
        # response not needed, will monitor "dt" sensor message
        body.mqtt_respond_to = None
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(
            topic=topic,
            message_io_data=body)

    def __publish_node_request(self, gui_message):
        """ request node shutdown or reboot """
        # desired = gui_message.mode
        self.log_info(Global.PUBLISH + ": " + Global.NODE +
                      ": " + gui_message.mode)
        now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(Global.BROADCAST,
                                                    Global.UNKNOWN) + "/req"
        body = IoData()
        body.mqtt_message_root = Global.NODE
        body.mqtt_desired = gui_message.mode
        # responds not needed
        body.mqtt_respond_to = None
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(
            topic=topic,
            message_io_data=body)

    def __publish_fastclock_request(self, gui_message):
        """ request fastclock from mqtt-dcc-command """
        desired = gui_message.mode
        self.log_info(Global.PUBLISH + ": " +
                      Global.FASTCLOCK + ": " + str(desired))
        now = Utility.now_milliseconds()
        pub_topic = self.fastclock_pub_topic
        body = IoData()
        body.mqtt_message_root = Global.TOWER
        body.mqtt_port_id = Global.FASTCLOCK
        body.mqtt_desired = desired
        if desired == Global.RESET:
            body.mqtt_metadata = ({Global.FASTCLOCK: {Global.TIME: gui_message.value}})
        body.mqtt_respond_to = self.mqtt_config.fixed_subscribe_topics.get(
            Global.SELF) + "/res"
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(
            topic=pub_topic,
            message_io_data=body)

    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse time options section of config file """
        dcc_command_topic = mqtt_config.publish_topics.get(Global.DCC_COMMAND,
                                                           Global.UNKNOWN) + "/req"
        fastclock_topic = mqtt_config.publish_topics.get(Global.FASTCLOCK,
                                                         Global.UNKNOWN) + "/req"
        respond_to_topic = mqtt_config.subscribe_topics.get(
            Global.SELF, Global.UNKNOWN)
        respond_to_topic = respond_to_topic.replace("/#", "/res")
        return (dcc_command_topic, fastclock_topic, respond_to_topic)

    def __send_message_to_tk(self, message):
        # forward message to gui display device process
        self.device_queue.put((Global.DEVICE_SEND, message))

    def __process_data_tower_inventory_message(self, msg_body=None):
        """ process data tower inventory message """
        self.log_info("Tower Data Received: "+str(msg_body.mqtt_port_id) +
                      " ... "+str(msg_body.mqtt_reported))
        if msg_body.mqtt_port_id == Global.INVENTORY and \
                msg_body.mqtt_reported == Global.CHANGED:
            # inventory has changed, request the inventory
            self.__publish_tower_report_requests()
        else:
            self.log_unexpected_message(msg_body=msg_body)
        return True

    def __process_data_tower_dashboard_message(self, msg_body=None):
        """ process data tower dashboard message """
        self.log_info("Tower Data Received: "+str(msg_body.mqtt_port_id) +
                      " ... "+str(msg_body.mqtt_reported))
        if msg_body.mqtt_port_id == Global.DASHBOARD and \
                msg_body.mqtt_reported == Global.CHANGED:
            # dashboard has changed, request the dashbioard
            self.publish_tower_report_request(Global.DASHBOARD)
        else:
            self.log_unexpected_message(msg_body=msg_body)
        return True
