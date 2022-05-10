#!/usr/bin/python3
# app_process.py
"""


app_process - the application process for mqtt-throttle


The MIT License (MIT)

Copyright 2021 richard p hughes

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
from utils.global_constants import Global
# from utils.global_synonyms import Synonyms

# from structs.roster import Roster
from structs.io_data import IoData
from structs.throttle_message import ThrottleMessage
from structs.inventory import Inventory
from structs.warrants import Warrants
from structs.panels import Panels
from structs.sensor_states import SensorStates

from processes.base_process import SendAfterMessage
from processes.base_mqtt_process import BaseMqttProcess

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
        self.throttle_id = "pi-throttle"
        self.device_queue = queues[Global.DEVICE]
        self.dispatcher_pub_topic = None
        self.fastclock_pub_topic = None
        self.respond_to_topic = None
        self.socket_child_pairs = {}
        self.switches = []
        self.sensor_states = SensorStates()
        self.throttle_ping_send_after_message = None

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        self.log_info("Init socket server")
        (self.dispatcher_pub_topic, self.fastclock_pub_topic,
                self.respond_to_topic) \
                = self.__parse_mqtt_options_config(self.mqtt_config)
        self.publish_dispatcher_report_request(Global.ROSTER)
        self.publish_tower_report_request(Global.INVENTORY)
        self.publish_tower_report_request(Global.STATES)
        self.publish_tower_report_request(Global.PANELS)
        self.publish_tower_report_request(Global.WARRANTS)
        power_message = ThrottleMessage
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
            if msg_type == Global.THROTTLE + ":" + Global.PING:
                self.send_after(self.throttle_ping_send_after_message)
                self.__send_throttle_pings()
                msg_consummed = True
            elif msg_type == Global.PUBLISH:
                # print(">>> app publish: " + str(msg_body))
                if isinstance(msg_body, ThrottleMessage):
                    msg_consummed = self.__process_publish_messages(msg_body)

                #if msg_body[Global.TYPE] == Global.DATA:
                #    self.publish_data_message(msg_body[Global.TOPIC],
                #                              msg_body[Global.BODY])
                msg_consummed = True
                #elif msg_body[Global.TYPE] == Global.RESPONSE:
                #    # response: " + str(msg_body))
                #    self.publish_response_message(msg_body[Global.REPORTED], \
                #                    msg_body[Global.METADATA], msg_body[Global.BODY])
                #    msg_consummed = True
                #elif msg_body[Global.TYPE] == Global.REQUEST:
                #    self.publish_request_message(msg_body[Global.TOPIC],
                #                                 msg_body[Global.BODY])
                #    msg_consummed = True
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

    def process_request_registry_message(self, msg_body=None):
        """ process request registry message """
        report_desired = msg_body.get_desired_value_by_key(Global.REPORT)
        if report_desired == Global.INVENTORY:
            self.report_inventory(msg_body=msg_body)
        else:
            self.log_unexpected_message(msg_body=msg_body)

    def process_response_roster_message(self, msg_body=None):
        self.log_info(Global.RECEIVED+": "+Global.ROSTER)
        super().process_response_roster_message(msg_body)
        roster_map = {}
        # print(">>> roster: " + str(self.roster))
        for _key, loco in self.roster.locos.items():
            roster_item = ThrottleMessage()
            roster_item.name = loco.name
            roster_item.text = loco.description
            roster_item.dcc_id = loco.dcc_id
            roster_item.image = loco.image
            roster_map[roster_item.dcc_id] = roster_item

        self.__send_message_to_tk(TkMessage(msg_type=Global.ROSTER, \
                            cab=Global.ALL,
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
            self.log_error("No Inventory found in registry response: " +
                           str(meta))
        else:
            # found an inventory
            inventory = Inventory({Global.INVENTORY: inventory_map})
            switch_group = inventory.inventory_groups.get(Global.SWITCH, None)
            self.switches = {}
            if switch_group is not None:
                # print(">>> switch map: " + str(switch_group))
                for switch in switch_group.inventory_items:
                    # print(">>> item: " + str(switch))
                    switch_map = ThrottleMessage()
                    switch_map.name = switch.key
                    switch_map.node_id = switch.node_id
                    switch_map.port_id = switch.port_id
                    switch_map.text = switch.command_topic
                    switch_map.mode = Global.UNKNOWN
                    self.switches[switch.key] = switch_map
                    # print(">>> switch: " + str(switch))
                self.__send_message_to_tk(TkMessage(msg_type=Global.SWITCHES, \
                            cab=Global.ALL,
                            msg_data=self.switches))
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
            self.log_error("No Panels found in registry response: " +
                           str(meta))
        else:
            # found panels
            panels = Panels({Global.PANELS: panels_map})
            self.__send_message_to_tk(TkMessage(msg_type=Global.PANELS,
                            msg_data=panels))
        return True

    def process_response_warrants_message(self, msg_body=None):
        """ process warrants message """
        self.log_info(Global.RECEIVED+": "+Global.WARRANTS)
        warrants_map = None
        meta = msg_body.mqtt_metadata
        # print(">>> warrant meta: " + str(meta))
        if meta is not None:
            warrants_map = meta.get(Global.WARRANTS, None)
        if warrants_map is None:
            # not a warrants response
            self.log_error("No Warrants found in registry response: " +
                           str(meta))
        else:
            # found warrants
            warrants = Warrants({Global.WARRANTS: warrants_map})
            self.__send_message_to_tk(TkMessage(msg_type=Global.WARRANTS,
                            msg_data=warrants))
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
            self.log_error("No States found in registry response: " +
                           str(meta))
        else:
            # found states
            states = SensorStates(states_map)
            self.__send_message_to_tk(TkMessage(msg_type=Global.STATES,
                            msg_data=states))
        return True

    def process_data_signal_message(self, msg_body=None):
        """ process a signal message """
        # print(">>> data signal: " + str(msg_body))
        if (msg_body.mqtt_message_root == Global.SIGNAL):
            dcc_id = msg_body.mqtt_loco_id
            if dcc_id is not None:
                # got a cab signal data message
                mode = msg_body.mqtt_reported
                throttle_message = ThrottleMessage()
                throttle_message.command = Global.SIGNAL
                throttle_message.dcc_id = dcc_id
                throttle_message.mode = mode
                tk_message = TkMessage()
                tk_message.msg_type = Global.SIGNAL
                tk_message.msg_data = throttle_message
                self.__send_message_to_tk(tk_message)
                self.log_info( Global.RECEIVED + ": "+Global.SIGNAL)
        return True

    def process_response_switch_message(self, msg_body=None):
        """ process a switch response """
        # ignore response
        return True

    def process_response_fastclock_message(self, msg_body=None):
        """ fastclock response received """
        message = Global.FASTCLOCK+ ": " + str(msg_body.mqtt_reported)
        self.__send_message_to_tk(TkMessage(\
                msg_type=Global.MESSAGE, msg_data=message))
        return True

    def process_response_cab_message(self, msg_body=None):
        """ process response cab message """
        # print(">>> cab response: " + str(msg_body))
        msg_consummed = False
        if msg_body.mqtt_desired in [Global.CONNECT, Global.DISCONNECT]:
            message = "Throttle: " + str(msg_body.mqtt_reported)
            self.__send_message_to_tk(TkMessage(\
                msg_type=Global.MESSAGE, msg_data=message))
            self.log_info("rcv: " + message)
            msg_consummed = True
        elif msg_body.mqtt_desired in [Global.ACQUIRE]:
            if msg_body.mqtt_reported == Global.STEAL_NEEDED:
                self.__send_message_to_tk(TkMessage(\
                    msg_type=Global.STEAL_NEEDED,
                    cab=msg_body.mqtt_cab_id,
                    msg_data=msg_body.mqtt_loco_id))
            else:
                message = "Loco: " + str(msg_body.mqtt_cab_id) + ": " \
                    + str(msg_body.mqtt_loco_id) + ": " +str(msg_body.mqtt_reported)
                self.__send_message_to_tk(TkMessage(\
                    msg_type=Global.MESSAGE, msg_data=message))
                self.log_info("rcv: " + message)
            msg_consummed = True
        elif msg_body.mqtt_desired in [Global.STEAL]:
            message = "Loco: " + str(msg_body.mqtt_cab_id) + ": " \
                + str(msg_body.mqtt_loco_id) + ": " +str(msg_body.mqtt_reported)
            self.__send_message_to_tk(TkMessage(\
                msg_type=Global.MESSAGE, msg_data=message))
            self.log_info("rcv: " + message)
            msg_consummed = True
        elif msg_body.mqtt_desired == Global.RELEASE:
            message = "Loco: " + str(msg_body.mqtt_cab_id) + ": " \
                + str(msg_body.mqtt_loco_id) + ": " +str(msg_body.mqtt_reported)
            self.__send_message_to_tk(TkMessage(\
                msg_type=Global.MESSAGE, msg_data=message))
            self.log_info("rcv: " + message)
            msg_consummed = True
        elif isinstance(msg_body.mqtt_desired, dict):
            speed = msg_body.mqtt_desired.get(Global.SPEED, None)
            direction = msg_body.mqtt_desired.get(Global.DIRECTION, None)
            if speed is not None or direction is not None:
                throttle_message = ThrottleMessage()
                throttle_message.cab_id = msg_body.mqtt_cab_id
                throttle_message.loco_id = msg_body.mqtt_loco_id
                tk_message = TkMessage()
                tk_message.msg_type = Global.SPEED
                if speed is not None:
                    throttle_message.command =  Global.SPEED
                    throttle_message.speed = speed
                    tk_message.msg_type = Global.SPEED
                elif direction is not None:
                    throttle_message.command =  Global.DIRECTION
                    throttle_message.direction = direction
                    tk_message.type = Global.DIRECTION
                tk_message.msg_data = throttle_message
                tk_message.cab = msg_body.mqtt_cab_id
                self.__send_message_to_tk(tk_message)
                msg_consummed = True
            elif msg_body.mqtt_desired.get(Global.FUNCTION, None) is not None:
                message = Global.CAB + ": " + str(msg_body.mqtt_cab_id) + ": " \
                        + Global.LOCO + ": " + str(msg_body.mqtt_loco_id) + ": " \
                        + str(msg_body.mqtt_reported)
                self.__send_message_to_tk(TkMessage(\
                    msg_type=Global.MESSAGE, msg_data=message))
                self.log_info("rcv: " + message)
                msg_consummed = True
        return msg_consummed

    def process_data_sensor_message(self, msg_body=None):
        """ process a switch message """
        #print(">>> data sensor")
        return True

    def process_data_switch_message(self,msg_body=None):
        """ process a sensor message """
        #print(">>> switch data")
        if (msg_body.mqtt_message_root == Global.SWITCH):
            if (msg_body.mqtt_port_id == Global.POWER):
                power_message = ThrottleMessage()
                power_message.command = Global.SWITCH
                power_message.port_id = Global.POWER
                power_message.mode = msg_body.mqtt_reported
                self.__send_message_to_tk(TkMessage(\
                    msg_type=Global.POWER, msg_data=power_message))
                message = "Power: " + str(msg_body.mqtt_reported)
                self.__send_message_to_tk(TkMessage(\
                    msg_type=Global.MESSAGE, msg_data=message))
                self.log_info(Global.RECEIVED + ": " + Global.POWER)
            else:
                switch_message = ThrottleMessage()
                switch_message.command = Global.SWITCH
                switch_message.port_id = msg_body.mqtt_port_id
                switch_message.node_id = msg_body.mqtt_node_id
                switch_message.mode = msg_body.mqtt_reported
                self.__send_message_to_tk(TkMessage(\
                    msg_type=Global.SWITCH, msg_data=switch_message))
                message = Global.SWITCH + ": " \
                    + str(msg_body.mqtt_port_id) + ": " \
                    + str(msg_body.mqtt_reported)
                self.__send_message_to_tk(TkMessage(\
                    msg_type=Global.MESSAGE, msg_data=message))
                self.log_info(Global.RECEIVED + ": " + Global.SWITCH)
        return True

    def process_data_dashboard_message(self, msg_body=None):
        """ process dashboard data message """
        self.log_info(Global.RECEIVED+": "+Global.DASHBOARD)
        dashboard_map = None
        meta = msg_body.mqtt_metadata
        if meta is not None:
            dashboard_map = meta.get(Global.DASHBOARD, None)
        if dashboard_map is None:
            # not a dashboard message
            self.log_error("No Dashboard found in message: " +
                           str(meta))
        else:
            # found dashboard
            dashboard = Warrants({Global.DASHBOARD: dashboard_map})
            self.__send_message_to_tk(TkMessage(msg_type=Global.DASHBOARD,
                            msg_data=dashboard))
        self.log_info( Global.RECEIVED+": "+Global.DASHBOARD)
        return True

    def process_data_cab_message(self, msg_body=None):
        """ process data cab message """
        if msg_body.mqtt_reported == Global.STOLEN:
            message = "Loco: " + str(msg_body.mqtt_cab_id) + ": " \
                    + str(msg_body.mqtt_loco_id) + ": " +str(msg_body.mqtt_reported)
            self.__send_message_to_tk(TkMessage(\
                msg_type=Global.MESSAGE, msg_data=message))
            self.log_info("rcv: " + message)
            self.__send_message_to_tk(TkMessage(\
                    msg_type=Global.STOLEN,
                    cab=msg_body.mqtt_cab_id,
                    msg_data=msg_body.mqtt_loco_id))
        else:
            self.log_unexpected_message(msg_body=msg_body)
        return True

    def process_data_fastclock_message(self, msg_body=None):
        """ process a fastclock message"""
        self.log_info(Global.RECEIVED+": "+Global.FASTCLOCK)
        fastclock = None
        if msg_body.mqtt_message_root == Global.FASTCLOCK:
            if msg_body.mqtt_metadata is not None:
                if Global.FASTCLOCK in msg_body.mqtt_metadata:
                    fastclock =  msg_body.mqtt_metadata[Global.FASTCLOCK]
        if fastclock is not None:
            self.__send_message_to_tk(TkMessage(msg_type=Global.FASTCLOCK, msg_data=fastclock))
        return True

    #
    # private functions
    #

    def __send_throttle_pings(self):
        """ send 'pings' to dcc command server """
        self.log_info(Global.PUBLISH +": " + Global.THROTTLE + " " +Global.PING)
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_desired = Global.PING
        self.publish_request_message(\
                    topic=self.dispatcher_pub_topic,
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
            msg_consummed = self.__process_publish_throttle_messages(msg_body)
        elif msg_body.command == Global.SWITCH:
            if msg_body.port_id == Global.POWER:
                self.__publish_power_request(msg_body)
                msg_consummed = True
            else:
                self.__publish_switch_request(msg_body)
                msg_consummed = True
        elif msg_body.command == Global.SHUTDOWN:
            self.__publish_shutdown_request(msg_body)
            msg_consummed = True
        elif msg_body.command == Global.FASTCLOCK:
            self.__publish_fastclock_request(msg_body)
            msg_consummed = True
        return msg_consummed

    def __process_publish_throttle_messages(self, msg_body):
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


    def __publish_connect_request(self,_throttle_message):
        """ publish a throttle connect command """
        self.log_info(Global.PUBLISH +": " + Global.CONNECT)
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_desired = Global.CONNECT
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.dispatcher_pub_topic,
                    message_io_data=body)

    def __publish_disconnect_request(self, _throttle_message):
        """ publish a throttle connect command """
        self.log_info(Global.PUBLISH +": " + Global.DISCONNECT)
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_desired = Global.DISCONNECT
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.dispatcher_pub_topic,
                    message_io_data=body)

    def __publish_acquire_request(self, throttle_message):
        """ publish a throttle acquire loco command """
        self.log_info(Global.PUBLISH +": " + Global.ACQUIRE + ": " \
            + str(throttle_message.cab_id) + ": " \
            + str(throttle_message.dcc_id))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = throttle_message.cab_id
        body.mqtt_loco_id = throttle_message.dcc_id
        body.mqtt_desired = Global.ACQUIRE
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.dispatcher_pub_topic,
                    message_io_data=body)

    def __publish_steal_request(self, throttle_message):
        """ publish a throttle steal loco command """
        self.log_info(Global.PUBLISH +": " + Global.STEAL + ": " \
            + str(throttle_message.cab_id) + ": " \
            + str(throttle_message.dcc_id))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = throttle_message.cab_id
        body.mqtt_loco_id = throttle_message.dcc_id
        body.mqtt_desired = Global.STEAL
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.dispatcher_pub_topic,
                    message_io_data=body)

    def __publish_release_request(self, throttle_message):
        """ publish a throttle release loco command """
        self.log_info(Global.PUBLISH +": " + Global.RELEASE + ": " \
            + str(throttle_message.cab_id) + ": " \
            + str(throttle_message.dcc_id))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = throttle_message.cab_id
        body.mqtt_loco_id = throttle_message.dcc_id
        body.mqtt_desired = Global.RELEASE
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.dispatcher_pub_topic,
                    message_io_data=body)

    def __publish_speed_request(self, throttle_message):
        """ publish a throttle loco speed command """
        self.log_info(Global.PUBLISH +": " + Global.SPEED + ": " \
            + str(throttle_message.cab_id) + ": " \
            + str(throttle_message.dcc_id) + ": " \
            + str(throttle_message.speed))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = throttle_message.cab_id
        body.mqtt_loco_id = throttle_message.dcc_id
        body.mqtt_desired = {Global.SPEED: throttle_message.speed}
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.dispatcher_pub_topic,
                    message_io_data=body)

    def __publish_direction_request(self, throttle_message):
        """ publish a throttle loco direction command """
        self.log_info(Global.PUBLISH +": " + Global.DIRECTION + ": " \
            + str(throttle_message.cab_id) + ": " \
            + str(throttle_message.dcc_id) + ": " \
            + str(throttle_message.direction))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = throttle_message.cab_id
        body.mqtt_loco_id = throttle_message.dcc_id
        body.mqtt_desired = {Global.DIRECTION: throttle_message.direction}
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.dispatcher_pub_topic,
                    message_io_data=body)

    def __publish_function_request(self, throttle_message):
        """ publish a throttle loco function command """
        self.log_info(Global.PUBLISH +": " + Global.FUNCTION + ": " \
                + str(throttle_message.cab_id) + ": " \
                + str(throttle_message.dcc_id) + ": " \
                + str(throttle_message.function) + ": "\
                + str(throttle_message.mode))
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.throttle_id
        body.mqtt_cab_id = throttle_message.cab_id
        body.mqtt_loco_id = throttle_message.dcc_id
        body.mqtt_desired = {Global.FUNCTION: throttle_message.function, \
                Global.STATE: throttle_message.mode}
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.dispatcher_pub_topic,
                    message_io_data=body)

    def __publish_switch_request(self, throttle_message):
        """ request switch change """
        desired = throttle_message.mode
        self.log_info(Global.PUBLISH +": " + Global.SWITCH + ": " \
                + str(throttle_message.port_id) + ": " + str(desired))
        now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(Global.POWER,
                                                    Global.UNKNOWN) + "/req"
        body = IoData()
        body.mqtt_message_root = Global.SWITCH
        body.mqtt_node_id = self.node_name
        body.mqtt_port_id = throttle_message.port_id
        body.mqtt_desired = desired
        # response not needed, will monitor "dt" sensor message
        body.mqtt_respond_to = None
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(\
                    topic=topic,  # inventory command topic
                    message_io_data=body)

    def __publish_power_request(self, throttle_message):
        """ request power from mqtt-dcc-command """
        desired = throttle_message.mode
        self.log_info(Global.PUBLISH +": " + Global.POWER + ": " + str(desired))
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
        self.publish_request_message(\
                    topic=topic,
                    message_io_data=body)

    def __publish_shutdown_request(self, _throttle_message):
        """ request all nodes shutdown """
        #desired = throttle_message.mode
        self.log_info(Global.PUBLISH +": " + Global.SHUTDOWN)
        now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(Global.BROADCAST,
                                                    Global.UNKNOWN) + "/req"
        body = IoData()
        body.mqtt_message_root = Global.NODE
        body.mqtt_desired = Global.SHUTDOWN
        # response not needed, will monitor "dt" sensor message
        body.mqtt_respond_to = None
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(\
                    topic=topic,
                    message_io_data=body)

    def __publish_fastclock_request(self, throttle_message):
        """ request fastclock from mqtt-dcc-command """
        desired = throttle_message.mode
        self.log_info(Global.PUBLISH +": " + Global.FASTCLOCK + ": " + str(desired))
        now = Utility.now_milliseconds()
        body = IoData()
        body.mqtt_message_root = Global.FASTCLOCK
        body.mqtt_node_id = self.node_name
        body.mqtt_desired = {Global.FASTCLOCK: desired}
        body.mqtt_respond_to = self.mqtt_config.fixed_subscribe_topics.get(
            Global.SELF) + "/res"
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_request_message(\
                    topic=self.fastclock_pub_topic,
                    message_io_data=body)

    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse time options section of config file """
        dispatcher_topic = mqtt_config.publish_topics.get(Global.DISPATCHER,
                                                       Global.UNKNOWN) + "/req"
        fastclock_topic = mqtt_config.publish_topics.get(Global.FASTCLOCK,
                                                       Global.UNKNOWN) + "/req"
        respond_to_topic = mqtt_config.subscribe_topics.get(
            Global.SELF, Global.UNKNOWN)
        respond_to_topic = respond_to_topic.replace("/#", "/res")
        return (dispatcher_topic, fastclock_topic, respond_to_topic)

    def __send_message_to_tk(self, message):
        # forward message to gui display device process
        self.device_queue.put((Global.DEVICE_SEND, message))
