#!/usr/bin/python3
# cab_process.py
"""

        CabProcess - process class for handling cab related operations in dcc command station


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
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys
# from turtle import end_fill

sys.path.append('../lib')

#import time
import copy


from utils.utility import Utility
from utils.global_synonyms import Synonyms
from utils.global_constants import Global
from structs.gui_message import GuiMessage
from structs.mqtt_config import MqttConfig
from structs.io_data import IoData
from processes.base_process import BaseProcess

from command_throttle import CommandThrottle



# from structs.io_data import IoData


class CabProcess(BaseProcess):
    """ handle cab messages """

    def __init__(self, events=None, queues=None):
        super().__init__(name="cab",
                         events=events,
                         in_queue=queues[Global.CAB],
                         app_queue=queues[Global.APPLICATION],
                         log_queue=queues[Global.LOGGER])
        self.response_queue_name = Global.CAB + ":" + Global.RESPONSE
        self.driver_queue = queues[Global.DRIVER]
        self.response_queue = queues[self.response_queue_name]
        self.roster = None
        self.throttles = {}
        self.throttle_timeout = 0
        self.driver = None
        self.mqtt_config = None
        self.switch_pub_topic = None
        self.cab_pub_topic = None
        self.default_speedsteps = 128
        self.log_info("Starting")

    def initialize_process(self):
        """ iitialize this process """
        super().initialize_process()
        self.mqtt_config = MqttConfig(self.config, self.node_name,
                                      self.host_name, self.log_queue)
        # set queue  for type of command device we are talking to

        self.throttle_timeout = \
            self.__parse_config(self.config)
        (self.switch_pub_topic, self.cab_pub_topic) \
            = self.__parse_mqtt_options_config(self.mqtt_config)

    # def shutdown_process(self):
    #    """ process shutdown is in progress """
    #    super().shutdown_process()

    def process_message(self, new_message):
        """ process messages from async message queue """
        consummed = super().process_message(new_message)
        if not consummed:
            (operation, msg_body) = new_message
            # print(">>> message: " + str(operation) + " ... " + str(msg_body))
            if operation == Global.DRIVER_INPUT:
                if msg_body.command == Global.THROTTLE and \
                        msg_body.sub_command == Global.ACQUIRE and \
                        msg_body.reported == Global.STOLEN:
                    self.__report_loco_stolen(msg_body)
                    consummed = True
                elif msg_body.command == Global.THROTTLE and \
                        msg_body.sub_command == Global.RELEASE:
                    # print(">>> release loco. ." + str(msg_body))
                    self.__driver_send_message_and_wait_response(msg_body)
                    consummed = True
            elif operation == Global.CAB:
                # cab request forwarded from application
                self.process_request_cab_message(msg_body)
                consummed = True
            elif operation == Global.ROSTER:
                # roster reveived
                self.roster = msg_body
                consummed = True
        return consummed

    def process_request_cab_message(self, msg_body=None):
        """ process a cab request message """
        self.log_info("Cab Request: " + str(msg_body.mqtt_desired) + " ... " +
                      str(msg_body.mqtt_node_id) + " ... " +
                      str(msg_body.mqtt_throttle_id) + " ... " +
                      str(msg_body.mqtt_cab_id) + " ... " +
                      str(msg_body.mqtt_loco_id))
        desired = msg_body.mqtt_desired
        reported = Global.ERROR
        message = None
        data_reported = None
        if desired == Global.CONNECT:
            (reported, message, data_reported) = \
                self.__process_cab_connect_request(msg_body)
        elif desired == Global.DISCONNECT:
            (reported, message, data_reported) = \
                self.__process_cab_disconnect_request(msg_body)
        elif desired in [Global.ACQUIRE, Global.STEAL]:
            (reported, message, data_reported) = \
                self.__process_cab_acquire_request(msg_body)
        elif desired == Global.RELEASE:
            (reported, message, data_reported) = \
                self.__process_cab_release_request(msg_body)
        elif desired == Global.SET_LEAD:
            (reported, message, data_reported) = \
                self.__process_cab_set_lead_request(msg_body)
        elif isinstance(desired, dict):
            if Global.SPEED in desired:
                (reported, message, data_reported) = \
                    self.__process_cab_speed_request(msg_body)
            elif Global.DIRECTION in desired:
                (reported, message, data_reported) = \
                    self.__process_cab_direction_request(msg_body)
            elif Global.REPORT in desired:
                (reported, message, data_reported) = \
                    self.__process_cab_report_request(msg_body)
            elif Global.FUNCTION in desired:
                (reported, message, data_reported) = \
                    self.__process_cab_function_request(msg_body)

        else:
            reported = Global.ERROR
            message = "Unknown CAB reuquest: {" + str(desired) + "}"
        self.__publish_responses(msg_body, reported, message, data_reported)

    def process_data_cab_message(self, msg_body=None):
        """ process a cab data message """
        desired = msg_body.mqtt_desired
        if desired == Global.PING:
            # throttle keep alive ping
            throttle_id = msg_body.mqtt_throttle_id
            node_id = msg_body.mqtt_node_id
            throttle_key = CommandThrottle.make_key(node_id, throttle_id)
            throttle = self.throttles.get(throttle_key, None)
            if throttle is not None:
                throttle.last_timestamp = Utility.now_milliseconds()

    #
    # private functions
    #

    def __parse_config(self, _config):
        """ parse options from config dict """
        throttle_timeout = 60
        if Global.OPTIONS in self.config[Global.CONFIG]:
            if Global.TIME in self.config[Global.CONFIG][Global.OPTIONS]:
                throttle_time_param = Global.THROTTLE + "-" + Global.TIMEOUT
                if throttle_time_param in self.config[Global.CONFIG][
                        Global.OPTIONS][Global.TIME]:
                    throttle_timeout = self.config[Global.CONFIG][
                        Global.OPTIONS][Global.TIME][throttle_time_param]
                    self.log_debug("THrottle Timeout: " +
                                   str(self.throttle_timeout))
        return throttle_timeout

    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse time options section of config file """
        switch_topic = mqtt_config.publish_topics.get(Global.SWITCH,
                                                      Global.UNKNOWN)
        cab_topic = mqtt_config.publish_topics.get(Global.CAB, Global.UNKNOWN)
        return (switch_topic, cab_topic)

    def __process_cab_connect_request(self, msg_body):
        """ connect a new throttle """
        reported = Global.ERROR
        message = None
        data_reported = None
        driver_message = self.__parse_mqtt_data(msg_body)
        throttle_key = CommandThrottle.make_key(
            driver_message.node_id, driver_message.throttle_id)
        if throttle_key in self.throttles:
            # already connected, clear out old connection
            self.__process_cab_disconnect_request(msg_body)
        driver_message.command = Global.THROTTLE
        driver_message.sub_command = Global.CONNECT
        connect_response_message =  \
            self.__driver_send_message_and_wait_response(driver_message)
        if connect_response_message.reported == Global.CONNECTED:
            new_throttle = CommandThrottle(
                driver_message.node_id, driver_message.throttle_id)
            new_throttle.last_timestamp = Utility.now_milliseconds()
            new_throttle.connect_message = copy.deepcopy(msg_body)
            self.throttles[new_throttle.key()] = new_throttle
            reported = Global.CONNECT
        return (reported, message, data_reported)

    def __process_cab_disconnect_request(self, msg_body):
        """ dicsonnect an existing throttle """
        reported = Global.ERROR
        message = None
        data_reported = None
        driver_message = self.__parse_mqtt_data(msg_body)
        throttle_key = CommandThrottle.make_key(
            driver_message.node_id, driver_message.throttle_id)
        throttle = self.throttles.get(throttle_key, None)
        if throttle is None:
            message = "Error: throttle unknown"
        else:
            driver_message.command = Global.THROTTLE
            driver_message.sub_command = Global.DISCONNECT
            _driver_response_message =  \
                self.__driver_send_message_and_wait_response(driver_message)
            # delete the throttle and its cabs and locos
            del self.throttles[throttle_key]
            reported = Global.DISCONNECT
        return (reported, message, data_reported)

    def __process_cab_acquire_request(self, msg_body):
        """ acquire a loco """
        steal = False
        if msg_body.mqtt_desired == Global.STEAL:
            steal = True
        reported = Global.ERROR
        message = None
        data_reported = None
        driver_message = self.__parse_mqtt_data(msg_body)
        throttle_key = CommandThrottle.make_key(
            driver_message.node_id, driver_message.throttle_id)
        throttle = self.throttles.get(throttle_key, None)
        if throttle is None:
            self.log_error(
                "Throttle not known, cannot acquire loco: " + str(throttle_key))
            message = "Error: Throttle not known"
        else:
            throttle.last_timestamp = Utility.now_milliseconds()
            driver_message.command = Global.THROTTLE
            if steal:
                driver_message.sub_command = Global.STEAL
            else:
                driver_message.sub_command = Global.ACQUIRE
            driver_response_message =  \
                self.__driver_send_message_and_wait_response(driver_message)
            if not isinstance(driver_response_message, list):
                driver_response_message = [driver_response_message]
            for resp in driver_response_message:
                # print(">>> resp: " + str(resp))
                if resp is not None:
                    if resp.reported == Global.FULL:
                        message = "Error: Slot table is full, loco not acquired"
                        reported = Global.ERROR
                    elif resp.reported == Global.STEAL_NEEDED:
                        reported = Global.STEAL_NEEDED
                        message = "Error: loco is use by another throttle, loco not acquired, steal if necessary"
                    else:
                        message = None
                        reported = Global.ACQUIRED
        if reported == Global.ACQUIRED:
            # loco was acquired, initialize it
            driver_message = self.__parse_mqtt_data(msg_body)
            driver_message.command = Global.THROTTLE
            driver_message.sub_command = Global.SPEED
            driver_message.speed = 0
            driver_message.direction = Global.FORWARD
            _driver_response =  \
                self.__driver_send_message_and_wait_response(driver_message)
            self.__publish_loco_direction_changed(msg_body.mqtt_loco_id, Global.FORWARD)
        return (reported, message, data_reported)

    def __process_cab_set_lead_request(self, msg_body):
        """ set the lead loco in a consist """
        reported = Global.ERROR
        message = None
        data_reported = None
        driver_message = self.__parse_mqtt_data(msg_body)
        driver_message.command = Global.THROTTLE
        driver_message.sub_command = Global.SET_LEAD
        driver_response =  \
            self.__driver_send_message_and_wait_response(driver_message)
        if not isinstance(driver_response, list):
            driver_response = [driver_response]
        for resp in driver_response:
            if resp is not None:
                reported = resp.reported
        return (reported, message, data_reported)

    def __process_cab_release_request(self, msg_body):
        """ release a loco """
        self.log_debug("Loco Release: " + str(msg_body.mqtt_loco_id))
        reported = Global.ERROR
        message = None
        data_reported = None
        driver_message = self.__parse_mqtt_data(msg_body)
        driver_message.command = Global.THROTTLE
        driver_message.sub_command = Global.RELEASE
        driver_response =  \
            self.__driver_send_message_and_wait_response(driver_message)
        if not isinstance(driver_response, list):
            driver_response = [driver_response]
        for resp in driver_response:
            if resp is not None:
                reported = resp.reported
        return (reported, message, data_reported)


    def __process_cab_speed_request(self, msg_body):
        """ set loco speed """
        self.log_warning("Cab Speed: " + str(msg_body.mqtt_cab_id)+\
            " " + str(msg_body.mqtt_desired))
        reported = None
        message = None
        data_reported = None
        driver_message = self.__parse_mqtt_data(msg_body)
        driver_message.command = Global.THROTTLE
        driver_message.sub_command = Global.SPEED
        speed = msg_body.mqtt_desired[Global.SPEED]
        if speed > 0:
            # convert speed percent to speedsteps
            speed = round((speed / 100) * self.default_speedsteps)
        driver_message.speed = speed
        driver_response =  \
            self.__driver_send_message_and_wait_response(driver_message)
        # print(">>> speed response:" + str(driver_response))
        if not isinstance(driver_response, list):
            driver_response = [driver_response]
        for resp in driver_response:
            if resp is None or resp.reported == Global.ERROR:
                reported = Global.ERROR
            else:
                reported = msg_body.mqtt_desired
        return (reported, message, data_reported)

    def __process_cab_direction_request(self, msg_body):
        """ set loco direction """
        self.log_debug("Cab Direction: " + str(msg_body.mqtt_loco_id))
        reported = None
        message = None
        data_reported = None
        driver_message = self.__parse_mqtt_data(msg_body)
        driver_message.command = Global.THROTTLE
        driver_message.sub_command = Global.DIRECTION
        driver_message.direction = msg_body.mqtt_desired[Global.DIRECTION]
        driver_response =  \
            self.__driver_send_message_and_wait_response(driver_message)
        if not isinstance(driver_response, list):
            driver_response = [driver_response]
        for resp in driver_response:
            if resp is not None:
                if resp.reported == Global.ERROR:
                    reported = Global.ERROR
                else:
                    reported = msg_body.mqtt_desired
        if reported != Global.ERROR:
            self.__publish_loco_direction_changed(msg_body.mqtt_loco_id, driver_message.direction)
        return (reported, message, data_reported)

    def __process_cab_function_request(self, msg_body):
        self.log_debug("Cab Function: " + str(msg_body.mqtt_cab_id))
        reported = None
        message = None
        data_reported = None
        throttle_id = msg_body.mqtt_throttle_id
        node_id = msg_body.mqtt_node_id
        desired = msg_body.mqtt_desired
        new_function = None
        new_function_state = None
        (throttle, t_message) = self.__find_throttle(node_id, throttle_id)
        if t_message is None:
            throttle.last_timestamp = Utility.now_milliseconds()
        #print(">>> message: " + str(message))
        #print(">>> loco list: " + str(loco_list))
        #print(">>> function: " + str(desired))
        if message is None:
            if isinstance(desired, dict):
                temp_function = desired.get(Global.FUNCTION, None)
                if isinstance(temp_function, int) and \
                        -1 <= temp_function <= 29:
                    new_function = temp_function
                #print(">>> function f: " + str(new_function))
                temp_function_state = desired.get(Global.STATE, None)
                if Synonyms.is_synonym_activate(temp_function_state):
                    new_function_state = Global.ON
                elif Synonyms.is_synonym_deactivate(temp_function_state):
                    new_function_state = Global.OFF
                #print(">>> function s: " + str(new_function_state))

        if new_function is None or new_function_state is None:
            message = "Error: Invalid function: [" + str(desired) + "]"

        #print(">>> message2: " + str(message))
        #print(">>> message2: " + str(new_function))
        #print(">>> message2: " + str(new_function_state))
        if message is None:
            driver_message = GuiMessage()
            driver_message.command = Global.THROTTLE
            driver_message.sub_command = Global.FUNCTION
            driver_message.node_id = msg_body.mqtt_node_id
            driver_message.throttle_id = msg_body.mqtt_throttle_id
            driver_message.cab_id = msg_body.mqtt_cab_id
            driver_message.dcc_id = msg_body.mqtt_loco_id
            driver_message.function = new_function
            driver_message.mode = new_function_state
            _dcc_response =  \
                self.__driver_send_message_and_wait_response(driver_message)

        if message is not None:
            reported = Global.ERROR
        else:
            reported = desired
        return (reported, message, data_reported)

    def __process_cab_report_request(self, msg_body):
        """ get loco status """
        # self.log_warning("Cab Report: " + str(msg_body.mqtt_cab_id)+\
        #    " " + str(msg_body.mqtt_desired))
        reported = None
        message = None
        data_reported = None
        driver_message = self.__parse_mqtt_data(msg_body)
        driver_message.command = Global.THROTTLE
        driver_message.sub_command = Global.REPORT
        driver_message.mode = msg_body.mqtt_desired[Global.REPORT]
        driver_response =  \
            self.__driver_send_message_and_wait_response(driver_message)
        if not isinstance(driver_response, list):
            driver_response = [driver_response]
        for resp in driver_response:
            if resp.reported == Global.ERROR:
                reported = Global.ERROR
            else:
                if resp.mode == Global.SPEED:
                    reported = {Global.SPEED: resp.speed}
                else:
                    reported = {Global.DIRECTION: resp.direction}#
        return (reported, message, data_reported)

    def __report_loco_stolen(self, gui_message):
        """ a loco has been stolen, notify throttle """
        self.log_warning("Warning: Loco Stolen: " +
                         str(gui_message.cab_id) + " " + str(gui_message.dcc_id))
        (throttle, _message) = self.__find_throttle(
            gui_message.node_id, gui_message.throttle_id)
        if throttle is not None:
            response_message = copy.deepcopy(throttle.connect_message)
            response_message.mqtt_desired = Global.RELEASE
            response_message.mqtt_cab_id = gui_message.cab_id
            response_message.mqtt_loco_id = gui_message.dcc_id
            self.__publish_responses(response_message, Global.RELEASED,
                                     None, None)

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

    def __publish_loco_direction_changed(self, loco_id, direction):
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_loco_id = loco_id
        body.mqtt_reported = {Global.DIRECTION: direction}
        self.app_queue.put((Global.PUBLISH, {
            Global.TYPE: Global.DATA,
            Global.TOPIC: self.cab_pub_topic,
            Global.BODY: body}))


#    def __find_cab(self, node_id, throttle_id, cab_id):
#        """ find a cab in a throttle """
#        #print(">>> find cab: " + str(node_id) + " ..." + str(throttle_id) + \
#        #        " ... " + str(cab_id))
#        cab = None
#        throttle = None
#        message = None
#        (throttle, message) = self.__find_throttle(node_id, throttle_id)
#        if message is None:
#            cab = throttle.cabs.get(cab_id, None)
#            if cab is None:
#                message = "Error: Cab is not known: " + str(cab_id) + "}"
#
#        #print(">>> ... cab: " + str(cab) + " ... " + str(message))
#        return (throttle, cab, message)

    def __find_throttle(self, node_id, throttle_id):
        """ find a throttle """
        #print(">>> find throttle: " + str(node_id) + " ..." + str(throttle_id))
        message = None
        throttle_key = CommandThrottle.make_key(node_id, throttle_id)
        throttle = self.throttles.get(throttle_key, None)
        if throttle is None:
            message = "Error: Throttle not known: {" + str(throttle_key) + "}"
        #print(">>> ... throttle: " + str(throttle) + " ... " + str(message))
        return (throttle, message)

#    def __get_loco_direction(self, loco):
#        direction = Global.FORWARD
#        if not loco.current_direction_is_forward:
#            direction = Global.REVERSE
#        return direction

#    def __timeout_throttles(self):
#        """ disconnect any throttle that have timed out """
#        now = Utility.now_milliseconds()
#        expired_timestamp = now - (self.throttle_timeout * 1000)
#        expired_throttles = []
#        for _throttle_key, throttle in self.throttles.items():
#            if throttle.last_timestamp < expired_timestamp:
#                expired_throttles.append(throttle)
#        for exp_throttle in expired_throttles:
#            self.log_warning("Warning: Throttle timed out: {" +
#                             str(exp_throttle.connect_message.mqtt_node_id) +
#                             "}")
#            self.__process_cab_disconnect_request(
#                exp_throttle.connect_message.mqtt_node_id)
#            self.__publish_responses(exp_throttle.connect_message,
#                                     Global.DISCONNECTED,
#                                     "Error: Throttle timed out", None)

#    def __estop_locos(self, loco_list):
#        """ perform emergency stop on a list of locos """
#        for loco in loco_list:
#            # (slot_id,
#            # _slot_loco) = self.slot_manager.find_loco_slot(loco.dcc_id)
#            driver_message = GuiMessage()
#            driver_message.command = Global.THROTTLE
#            driver_message.sub_command = Global.SPEED
#            driver_message.slot_id = loco.slot
#            driver_message.dcc_id = loco.dcc_id
#            driver_message.speed = -1
#            driver_message.direction = loco.get_corrected_direction()
#            _dcc_response =  \
#                self.__driver_send_message_and_wait_response(driver_message)
#            loco.current_speed = 0
#        # wait for loco to come to a stop
#        time.sleep(1)

#    def __publish_message(self, _topic, _message):
#        pass

#    def __driver_send_message(self, send_message):
#        self.log_info("sync send: " + str(send_message))
#        #print(">>> msg: " + str(send_message))
#        self.driver_queue.put((Global.DRIVER_SEND,
#                               send_message))

    def __driver_send_message_and_wait_response(self, send_message):
        """ put a message in driver queue, wait for a reply """
        # assumes message is a GuiMessage class
        response = {Global.TEXT: Global.ERROR}
        self.log_debug("sync send and respond: " + str(send_message))
        send_message.response_queue = self.response_queue_name
        self.driver_queue.put(
            (Global.DRIVER_SEND_AND_RESPOND, send_message))
        # timeout = 2000 + Utility.now_milliseconds()  # timeout after 2 seconds
        # print(">>> sync send: "+ str(send_message))
        response = None
        try:
            (Global.DRIVER_RESPONSE,
             response) = self.response_queue.get(True, 2.0)
        except Exception as _error:
            # ignore exception from timeout on get
            pass
        self.log_debug("sync response: " + str(response))
        #  print(">>> sync response: " + str(response))
        return response

    def __parse_mqtt_data(self, mqtt_data):
        """ create a throttle message from a mqtt data message body """
        gui_message = GuiMessage()
        gui_message.node_id = mqtt_data.mqtt_node_id
        gui_message.throttle_id = mqtt_data.mqtt_throttle_id
        gui_message.cab_id = mqtt_data.mqtt_cab_id
        gui_message.dcc_id = mqtt_data.mqtt_loco_id
        gui_message.respond_to = mqtt_data.mqtt_respond_to
        if mqtt_data.mqtt_metadata is not None:
            facing = mqtt_data.mqtt_metadata.get(Global.FACING, None)
            if facing is not None:
                gui_message.mode = facing
        return gui_message
