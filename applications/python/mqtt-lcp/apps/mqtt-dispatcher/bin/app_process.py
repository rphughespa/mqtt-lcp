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


from utils.global_constants import Global
from utils.global_synonyms import Synonyms
from utils.utility import Utility

from structs.sensor_states import SensorStates
from structs.panels import Panels
from structs.dashboard import Dashboard
from structs.inventory import Inventory
from structs.gui_message import GuiMessage
from structs.io_data import IoData


from processes.base_mqtt_process import BaseMqttProcess
from processes.base_process import SendAfterMessage

# from structs.roster import Roster
from components.tk_message import TkMessage

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
        self.sensor_states = SensorStates()
        self.throttle_ping_send_after_message = None
        self.traffic_control = False
        self.auto_signals = False

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        self.log_info("Init socket server")
        (self.dcc_command_pub_topic, self.fastclock_pub_topic,
         self.respond_to_topic) \
            = self.__parse_mqtt_options_config(self.mqtt_config)
        self.publish_roster_report_request(Global.ROSTER)
        self.__publish_tower_report_requests()
        self.publish_tower_report_request(Global.PANELS)
        power_message = GuiMessage
        power_message.command = Global.SWITCH
        power_message.port_id = Global.POWER
        power_message.mode = Global.REPORT
        self.__publish_power_request(power_message)
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
            if msg_type == Global.PUBLISH:
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

        self.__send_message_to_tk(TkMessage(msg_type=Global.ROSTER,
                                            cab=Global.ALL,
                                            msg_data=roster_map))

    def process_response_signals_message(self, msg_body=None):
        """ process signals response message """
        self.log_info(Global.RECEIVED+": "+Global.SIGNALS)
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
        return True

    def process_response_switches_message(self, msg_body=None):
        """ process switches response message """
        self.log_info(Global.RECEIVED+": "+Global.SWITCHES)
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
            self.__process_switch_inventory(inventory)
        return True

    def process_response_routes_message(self, msg_body=None):
        """ process routes response message """
        self.log_info(Global.RECEIVED+": "+Global.ROUTES)
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
            self.__process_route_inventory(inventory)
        return True


    def process_response_panels_message(self, msg_body=None):
        """ process panels message """
        self.log_info(Global.RECEIVED+": "+Global.PANELS)
        panels_map = None
        meta = msg_body.mqtt_metadata
        if meta is not None:
            panels_map = meta.get(Global.PANELS, None)
        if panels_map is None:
            # not a panels response, pass it to super instance
            self.log_error("No Panels found in tower response: " +
                           str(meta))
        else:
            # found panels
            panels = Panels({Global.PANELS: panels_map})
            self.__send_message_to_tk(TkMessage(msg_type=Global.PANELS,
                                                msg_data=panels))
        return True

    def process_response_states_message(self, msg_body=None):
        """ process sensor states message """
        self.log_info(Global.RECEIVED+": "+Global.SENSOR)
        states_map = None
        meta = msg_body.mqtt_metadata
        if meta is not None:
            # print(">>> sensor states: " + str(meta))
            states_map = meta.get(Global.SENSOR_STATES, None)
        if states_map is None:
            # not a states response
            self.log_error("No States found in tower response: " +
                           str(meta))
        else:
            # found states
            states = SensorStates(states_map)
            #print(">>> states: " + str(states))
            for group_id, group in states.sensor_state_groups.items():
                #print(">>> group id:" +str(group_id))
                #print(">>> group: "+ str(group))
                for _sensor_id, sensor in group.sensor_state_items.items():
                    #print(">>> item id: " + str(sensor_id))
                    #print(">>> sensor: " + str(sensor))
                    sensor_message = GuiMessage()
                    sensor_message.command = group_id
                    sensor_message.port_id = sensor.port_id
                    sensor_message.node_id = sensor.node_id
                    sensor_message.loco_id = sensor.loco_id
                    sensor_message.mode = sensor.reported
                    self.__send_message_to_tk(TkMessage(
                        msg_type=sensor_message.command, msg_data=sensor_message))
        return True


    def process_data_dashboard_message(self, msg_body=None):
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
            self.__send_message_to_tk(TkMessage(msg_type=Global.DASHBOARD,
                                                msg_data=dashboard))
        return True

    def process_data_signal_message(self, msg_body=None):
        """ process a signal message """
        # print(">>> data signal: " + str(msg_body))
        if msg_body.mqtt_message_root == Global.SIGNAL:
            dcc_id = msg_body.mqtt_loco_id
            if dcc_id is  None:
                # not a cab signal data message
                signal_message = GuiMessage()
                signal_message.command = Global.SIGNAL
                signal_message.port_id = msg_body.mqtt_port_id
                signal_message.node_id = msg_body.mqtt_node_id
                signal_message.mode = msg_body.mqtt_reported
                self.__send_message_to_tk(TkMessage(
                    msg_type=Global.SIGNAL, msg_data=signal_message))
                message = Global.SIGNAL + ": " \
                    + str(msg_body.mqtt_port_id) + ": " \
                    + str(msg_body.mqtt_reported)
                self.__send_message_to_tk(TkMessage(
                    msg_type=Global.MESSAGE, msg_data=message))
                self.log_info(Global.RECEIVED + ": " + Global.SIGNAL)
        return True

    def process_data_block_message(self, msg_body=None):
        """ process block messages """
        if msg_body.mqtt_message_root == Global.BLOCK:
            _mode = msg_body.mqtt_reported
            gui_message = GuiMessage()
            gui_message.command = Global.BLOCK
            gui_message.port_id = msg_body.mqtt_port_id
            gui_message.node_id = msg_body.mqtt_node_id
            gui_message.mode = msg_body.mqtt_reported
            gui_message.sub_command = Global.BLOCK
            tk_message = TkMessage()
            tk_message.msg_type = Global.BLOCK
            tk_message.msg_data = gui_message
            self.__send_message_to_tk(tk_message)
            self.log_info(Global.RECEIVED + ": "+Global.BLOCK + " ... " + str(gui_message.port_id))
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
            tk_message = TkMessage()
            tk_message.msg_type = Global.LOCATOR
            tk_message.msg_data = gui_message
            self.__send_message_to_tk(tk_message)
            self.log_info(Global.RECEIVED + ": "+Global.LOCATOR + " ... " + str(gui_message.dcc_id))
        return True

    def process_response_switch_message(self, msg_body=None):
        """ process a switch response """
        # ignore response
        return True

    def process_data_sensor_message(self, msg_body=None):
        """ process a switch message """
        #print(">>> data sensor")
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
                self.__send_message_to_tk(TkMessage(
                    msg_type=Global.POWER, msg_data=power_message))
                message = "Power: " + str(msg_body.mqtt_reported)
                self.__send_message_to_tk(TkMessage(
                    msg_type=Global.MESSAGE, msg_data=message))
                self.log_info(Global.RECEIVED + ": " + Global.POWER)
            elif msg_body.mqtt_port_id == Global.TRAFFIC:
                self.traffic_control = Synonyms.is_synonym_active(msg_body.mqtt_reported)
            elif msg_body.mqtt_port_id == Global.AUTO_SIGNALS:
                self.auto_signals = Synonyms.is_synonym_active(msg_body.mqtt_reported)
            else:
                # print(">>> switch data, not power")
                switch_message = GuiMessage()
                switch_message.command = Global.SWITCH
                switch_message.port_id = msg_body.mqtt_port_id
                switch_message.node_id = msg_body.mqtt_node_id
                switch_message.mode = msg_body.mqtt_reported
                self.__send_message_to_tk(TkMessage(
                    msg_type=Global.SWITCH, msg_data=switch_message))
                message = Global.SWITCH + ": " \
                    + str(msg_body.mqtt_port_id) + ": " \
                    + str(msg_body.mqtt_reported)
                self.__send_message_to_tk(TkMessage(
                    msg_type=Global.MESSAGE, msg_data=message))
                self.log_info(Global.RECEIVED + ": " + Global.SWITCH)
        return True

    def process_data_fastclock_message(self, msg_body=None):
        """ process a fastclock message"""
        self.log_info(Global.RECEIVED+": "+Global.FASTCLOCK)
        fastclock = None
        if msg_body.mqtt_message_root == Global.FASTCLOCK:
            if msg_body.mqtt_metadata is not None:
                if Global.FASTCLOCK in msg_body.mqtt_metadata:
                    fastclock = msg_body.mqtt_metadata[Global.FASTCLOCK]
        if fastclock is not None:
            self.__send_message_to_tk(
                TkMessage(msg_type=Global.FASTCLOCK, msg_data=fastclock))
        return True

    def process_response_fastclock_message(self, msg_body=None):
        """ fastclock response received """
        message = Global.FASTCLOCK + ": " + str(msg_body.mqtt_reported)
        self.__send_message_to_tk(TkMessage(
            msg_type=Global.MESSAGE, msg_data=message))
        return True

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
        self.publish_tower_report_request(Global.SWITCHES)
        self.publish_tower_report_request(Global.SIGNALS)
        self.publish_tower_report_request(Global.ROUTES)
        self.publish_tower_report_request(Global.STATES)


    def __process_switch_inventory(self, inventory):
        """ send switch inventory to screens """
        switch_group = inventory.inventory_groups.get(Global.SWITCH, None)
        self.switches = {}
        if switch_group is not None:
            # print(">>> switch map: " + str(switch_group))
            for switch in switch_group.inventory_items:
                # print(">>> item: " + str(switch))
                switch_map = GuiMessage()
                switch_map.name = switch.key
                switch_map.node_id = switch.node_id
                switch_map.port_id = switch.port_id
                switch_map.text = switch.command_topic
                switch_map.mode = Global.UNKNOWN
                self.switches[switch.key] = switch_map
                # print(">>> switch: " + str(switch_map))
                self.__send_message_to_tk(TkMessage(msg_type=Global.SWITCH,
                                            cab=Global.ALL,
                                            msg_data=switch_map))

    def __process_route_inventory(self, inventory):
        """ send soute inventory to screens """
        route_group = inventory.inventory_groups.get(Global.ROUTE, None)
        self.routes = {}
        if route_group is not None:
            # print(">>> route map: " + str(route_group))
            for route in route_group.inventory_items:
                # print(">>> item: " + str(route))
                route_map = GuiMessage()
                route_map.name = route.key
                route_map.node_id = route.node_id
                route_map.port_id = route.port_id
                route_map.text = route.command_topic
                route_map.mode = Global.UNKNOWN
                self.routes[route.key] = route_map
                # print(">>> route: " + str(route))
                self.__send_message_to_tk(TkMessage(msg_type=Global.ROUTE,
                                                cab=Global.ALL,
                                                msg_data=route_map))

    def __process_signal_inventory(self, inventory):
        """ send signal inventory to screens """
        signal_group = inventory.inventory_groups.get(Global.SIGNAL, None)
        self.signals = {}
        if signal_group is not None:
            # print(">>> signal map: " + str(signal_group))
            for signal in signal_group.inventory_items:
                # print(">>> item: " + str(signal))
                signal_map = GuiMessage()
                signal_map.name = signal.key
                signal_map.node_id = signal.node_id
                signal_map.port_id = signal.port_id
                signal_map.text = signal.command_topic
                signal_map.mode = Global.UNKNOWN
                self.signals[signal.key] = signal_map
                # print(">>> signal: " + str(signal))
                self.__send_message_to_tk(TkMessage(msg_type=Global.SIGNAL,
                                                cab=Global.ALL,
                                                msg_data=signal_map))

    def __process_publish_messages(self, msg_body):
        """ process publish type messages """
        msg_consummed = False
        if msg_body.command == Global.SWITCH:
            if msg_body.port_id == Global.POWER:
                self.__publish_power_request(msg_body)
                msg_consummed = True
            elif msg_body.port_id == Global.TRAFFIC:
                self.__publish_traffic_request(msg_body)
                msg_consummed = True
            elif msg_body.port_id == Global.AUTO_SIGNALS:
                self.__publish_auto_signals_request(msg_body)
                msg_consummed = True
            else:
                self.__publish_switch_request(msg_body)
                msg_consummed = True
        elif msg_body.command == Global.SIGNAL:
            self.__publish_signal_request(msg_body)
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

    def __publish_signal_request(self, gui_message):
        """ request signal change """
        desired = gui_message.mode
        self.log_info(Global.PUBLISH + ": " + Global.SIGNAL + ": "
                      + str(gui_message.port_id) + ": " + str(desired))
        now = Utility.now_milliseconds()
        topic = gui_message.text  # command topic
        body = IoData()
        body.mqtt_message_root = Global.SIGNAL
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

    def __publish_power_request(self, gui_message):
        """ request power from mqtt-dcc-command """
        desired = gui_message.mode
        self.log_info(Global.PUBLISH + ": " +
                      Global.POWER + ": " + str(desired))
        now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(Global.POWER,
                                                    Global.UNKNOWN) + "/req"
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

    def __publish_traffic_request(self, gui_message):
        """ request traffic from mqtt-tower """
        desired = gui_message.mode
        self.log_info(Global.PUBLISH + ": " +
                      Global.TRAFFIC + ": " + str(desired))
        now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(Global.TOWER,
                                                    Global.UNKNOWN) + "/req"
        body = IoData()
        body.mqtt_message_root = Global.SWITCH
        body.mqtt_node_id = self.node_name
        body.mqtt_port_id = Global.TRAFFIC
        body.mqtt_desired = desired
        # response not needed, will monitor "dt" sensor message
        body.mqtt_respond_to = self.respond_to_topic
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
                                                    Global.UNKNOWN) + "/req"
        body = IoData()
        body.mqtt_message_root = Global.SWITCH
        body.mqtt_node_id = self.node_name
        body.mqtt_port_id = Global.AUTO_SIGNALS
        body.mqtt_desired = desired
        # response not needed, will monitor "dt" sensor message
        body.mqtt_respond_to = self.respond_to_topic
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(
            topic=topic,
            message_io_data=body)

    def __publish_node_request(self, gui_message):
        """ request node shutdown or reboot """
        #desired = gui_message.mode
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
        body = IoData()
        body.mqtt_message_root = Global.FASTCLOCK
        body.mqtt_node_id = self.node_name
        body.mqtt_port_id = Global.FASTCLOCK
        body.mqtt_desired = desired
        body.mqtt_respond_to = self.mqtt_config.fixed_subscribe_topics.get(
            Global.SELF) + "/res"
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(
            topic=self.fastclock_pub_topic,
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
