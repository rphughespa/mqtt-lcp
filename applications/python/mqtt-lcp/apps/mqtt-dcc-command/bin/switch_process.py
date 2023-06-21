#!/usr/bin/python3
# swutch_process.py
"""

        SwitchProcess - process class for handling switchand sensor related operations
        in dcc command station


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

sys.path.append('../lib')

#import copy
#import time

from processes.base_process import BaseProcess

from utils.global_constants import Global

#from utils.utility import Utility

from structs.mqtt_config import MqttConfig
from structs.gui_message import GuiMessage
from structs.io_data import IoData



class SwitchProcess(BaseProcess):
    """ handle switch messages """
    def __init__(self, events=None, queues=None):
        super().__init__(name="switch",
                         events=events,
                         in_queue=queues[Global.SWITCH],
                         app_queue=queues[Global.APPLICATION],
                         log_queue=queues[Global.LOGGER])
        self.response_queue_name = Global.SWITCH + ":" + Global.RESPONSE
        self.response_queue = queues[self.response_queue_name]
        self.driver_queue = queues[Global.DRIVER]
        self.track_power = Global.UNKNOWN
        self.mqtt_config = None
        self.switch_pub_topic = None
        self.switch_pub_topic = None
        self.log_info("Starting")

    def initialize_process(self):
        """ iitialize this process """
        super().initialize_process()
        self.mqtt_config = MqttConfig(self.config, self.node_name,
                                      self.host_name, self.log_queue)

        (self.switch_pub_topic, self.switch_pub_topic) \
             = self.__parse_mqtt_options_config(self.mqtt_config)
        if self.io_config is not None:
            if self.io_config.io_device_map is not None:
                for _key, dev in self.io_config.io_device_map.items():
                    self.log_debug("IoDevice: " + str(dev))

    def process_message(self, new_message):
        """ process messages from async message queue """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            (msg_type, msg_body) = new_message
            if msg_type == Global.DRIVER_INPUT:
                # press driver message: " + str(msg_body))
                mtext = msg_body
                if isinstance(msg_body, dict) and \
                    msg_body.get(Global.TEXT, None) is not None:
                    mtext = msg_body[Global.TEXT]
                self.__process_driver_input(mtext)
                msg_consummed = True
            elif msg_type == Global.SWITCH:
                # switch request forwarded from application
                self.process_request_switch_message(msg_body)
                msg_consummed = True
        return msg_consummed

    def process_request_switch_message(self, msg_body=None):
        """ process for switch requests """
        #print(">>> track msg: " + str(msg_body))
        if msg_body.mqtt_port_id == Global.POWER:
            # request for track power
            self.__process_request_power_message(msg_body)
        else:
            self.__process_request_turnout_switch_message(msg_body)


    #
    # private functions
    #

    def __process_request_turnout_switch_message(self, msg_body):
        """ process a non-power switch message"""
        print(">>> request switch")
        reported = Global.ERROR
        message = Global.MSG_ERROR_BAD_PORT_ID
        data_reported = None
        config_key = \
            self.io_config.io_port_map.get(msg_body.mqtt_port_id, None)
        if config_key is not None:
            config_item = self.io_config.io_device_map.get(config_key, None)
            if config_item is not None:
                #print("inv item: " + str(config_item))
                addr = config_item.io_address
                sub_addr = config_item.io_sub_address
                desired = msg_body.mqtt_desired
                print(">>> desired: " + str(desired))
                if desired == Global.TOGGLE:
                    if config_item.mqtt_reported == Global.CLOSE:
                        desired = Global.OPEN
                    else:
                        desired = Global.CLOSE
                send_message = GuiMessage()
                send_message.command = Global.SWITCH
                send_message.port_id = addr
                send_message.sub_address = sub_addr
                send_message.mode = desired
                response = \
                    self.__driver_send_message_and_wait_response(send_message)
                # print(">>> switch response: " + str(response))
                if not isinstance(response, list):
                    response = [response]
                for resp in response:
                    #print(">>> switch response" + str(resp))
                    if isinstance(resp, GuiMessage) and \
                            resp.command == Global.SWITCH:
                        reported = resp.mode
                        data_reported = reported
                        message = None
                        #print(">>> publish response" + str(reported))
                        self.__publish_responses(msg_body, reported, message, data_reported)

    def __process_request_power_message(self, msg_body=None):
        """ forward message to driver process """
        power_desired = msg_body.mqtt_desired
        #print(">>> power: " + str(power_desired))
        reported = Global.ERROR
        data_reported = None
        message = Global.MSG_ERROR_BAD_DESIRED
        if power_desired in [Global.ON, Global.OFF, Global.REPORT]:
            send_message = GuiMessage()
            send_message.command = Global.POWER
            send_message.mode = power_desired
            response = \
                self.__driver_send_message_and_wait_response(send_message)
            #print(">>> power response 1: " + str(send_message) + "\n...resp:  " + str(response))
            if not isinstance(response, list):
                response = [response]
            #print(">>> power response 1a: " + str(send_message) + "\n... resp: " + str(response))
            for resp in response:
                if resp is not None:
                    #print(">>> power response 2" + str(resp.command) +" : "+str(resp.mode))
                    if resp.command == Global.POWER:
                        #print(">>> power response 3: " + str(resp.mode))
                        reported = resp.mode
                        data_reported = reported
                        message = None
                        #print(">>> power response 4: " + str(data_reported))
                        self.__publish_responses(msg_body, reported, message, data_reported)

    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse time options section of config file """
        switch_topic = mqtt_config.publish_topics.get(Global.SWITCH,
                                                      Global.UNKNOWN)
        switch_topic = mqtt_config.publish_topics.get(Global.SWITCH, Global.UNKNOWN)
        return (switch_topic, switch_topic)

    def __process_driver_input(self, msg_body):
        """ driver input receive, parse and process it """
        self.log_debug("New Driver Data: " + str(msg_body))
        # print(">>> driver in app: " + str(msg_body))
        if msg_body is not None:
            if not isinstance(msg_body, str):
                self.log_debug(" ... " + str(msg_body))
                if msg_body.command == Global.POWER:
                    self.__process_power_input(msg_body)
                elif msg_body.command == Global.BLOCK:
                    self.__process_block_input(msg_body)
                elif msg_body.command == Global.RAILCOM and \
                        msg_body.sub_command == Global.FACING:
                    self.__process_railcom_input(msg_body)

    def __process_power_input(self, msg_data):
        """ process power input message """
        body = IoData()
        body.mqtt_message_root = Global.SWITCH
        body.mqtt_port_id = Global.POWER
        body.mqtt_reported = msg_data.mode
        self.__publish_data_message(body)

    def __process_block_input(self, msg_data):
        """ process bock input message """
        body = IoData()
        body.mqtt_message_root = Global.BLOCK
        body.mqtt_port_id = msg_data.port_id  # add blobk lookup
        body.mqtt_reported = msg_data.mode
        self.__publish_data_message(body)

    def __process_railcom_input(self, msg_data):
        """ process railcom input message """
        body = IoData()
        body.mqtt_message_root = Global.LOCATOR
        body.mqtt_port_id = msg_data.port_id
        body.mqtt_reported = msg_data.mode
        body.mqtt_loco_id = msg_data.dcc_id
        body.mqtt_metadata = {
            Global.TYPE: Global.RAILCOM,
            Global.FACING: msg_data.direction
        }
        self.__publish_data_message(body)

    def __publish_data_message(self, msg_body):
        """ format and publish responses """
        # print(">>> pub data : " + str(msg_body))
        message = (Global.PUBLISH, { \
            Global.TYPE: Global.DATA,
            Global.TOPIC: self.switch_pub_topic,
            Global.BODY: msg_body
        })
        self.app_queue.put(message)


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

#    def __publish_message(self, _topic, _message):
#        pass

#    def __driver_send_message(self, send_message):
#        self.log_debug("sync send: " + str(send_message))
#        #print(">>> msg: " + str(send_message))
#        self.driver_queue.put((Global.DRIVER_SEND, \
#            send_message))

    def __driver_send_message_and_wait_response(self, send_message):
        """ send a message to driver and wait for a reply """
        response = {Global.TEXT: Global.ERROR}
        self.log_debug("sync send and respond: " + str(send_message))
        message_to_send = send_message
        message_to_send.response_queue = self.response_queue_name
        # print(">>> sync request: " + str(message_to_send))
        self.driver_queue.put(
            (Global.DRIVER_SEND_AND_RESPOND, message_to_send))
        response = None
        try:
            (Global.DRIVER_INPUT,
             response) = self.response_queue.get(True, 2.0)
        except Exception as _error:
            # ignore exception from timeout on get
            pass
        self.log_debug("sync response: " + str(response))
        # print(">>> sync response: " + str(response))
        return response
