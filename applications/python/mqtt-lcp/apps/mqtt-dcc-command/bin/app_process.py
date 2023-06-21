#!/usr/bin/python3
# app_process.py
"""


AppProcess - the application process for mqtt_dcc_comand

The app process received mqtt requests  Forward CAB requests to the cab_process.
SWITCH messages handled in this process. All responses are send to mqtt by this process.


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

sys.path.append('../lib')

import time

from structs.io_data import IoData
#from structs.gui_message import GuiMessage

from utils.global_constants import Global
from utils.global_synonyms import Synonyms
#from utils.utility import Utility

from processes.base_mqtt_process import BaseMqttProcess


class AppProcess(BaseMqttProcess):
    """ Class that waits for an event to occur """
    def __init__(self, events=None, queues=None):

        super().__init__(name="app",
                         events=events,
                         in_queue=queues[Global.APPLICATION],
                         mqtt_queue=queues[Global.MQTT],
                         log_queue=queues[Global.LOGGER])
        self.response_queue_name = Global.APPLICATION + ":" + Global.RESPONSE
        self.response_queue = queues[self.response_queue_name]
        self.switch_queue = queues[Global.SWITCH]
        self.roster_queue = queues[Global.ROSTER]
        self.cab_queue = queues[Global.CAB]
        self.block_map = None
        self.railcom_map = None
        self.log_info("Starting")

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        if self.io_config is not None:
            if self.io_config.io_device_map is not None:
                self.block_map = {}
                self.railcom_map = {}
                for key, dev in self.io_config.io_device_map.items():
                    self.log_debug("IoDevice: " + str(dev))
                    if dev.io_device_type == Global.SENSOR:
                        sensor_type = None
                        if isinstance(dev.io_metadata, dict):
                            sensor_type = dev.io_metadata.get(
                                Global.TYPE, None)
                        if sensor_type == Global.BLOCK:
                            self.block_map[dev.io_address] = key
                        if sensor_type == Global.RAILCOM:
                            self.railcom_map[dev.io_address] = key
                self.log_debug("Block Map: " + str(self.block_map))
                self.log_debug("Railcom Map: " + str(self.railcom_map))
        time.sleep(1)

    def shutdown_process(self):
        """ shutdown the process """
        self.events[Global.SHUTDOWN].set()
        super().shutdown_process()

    def process_request_switch_message(self, msg_body=None):
        """ process for switch requests """
        self.switch_queue.put((Global.SWITCH, msg_body))

    def process_request_cab_message(self, msg_body=None):
        """ forward message to child cab process """
        # print(">>> cab msg: " + str(msg_body))
        self.cab_queue.put((Global.CAB, msg_body))

    def process_message(self, new_message):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            (msg_type, msg_body) = new_message
            if msg_type == Global.DRIVER_INPUT:
                self.__process_driver_input(new_message)
                msg_consummed = True
            elif msg_type == Global.DEVICE_INPUT_BLOCK_DATA:
                self.__process_block_message(msg_body)
                msg_consummed = True
            elif msg_type == Global.DEVICE_INPUT_RAILCOM_DATA:
                self.__process_railcom_message(msg_body)
                msg_consummed = True
            elif msg_type == Global.PUBLISH:
                if msg_body[Global.TYPE] == Global.DATA:
                    #print(">>> data: " + str(msg_body))
                    self.publish_data_message(msg_body[Global.TOPIC],
                                              msg_body[Global.BODY])
                    msg_consummed = True
                elif msg_body[Global.TYPE] == Global.RESPONSE:
                    # print(">>> response: " + str(msg_body))
                    self.publish_response_message(\
                                    reported=msg_body[Global.REPORTED],
                                    metadata=msg_body[Global.METADATA],
                                    data_reported=msg_body[Global.DATA],
                                    message_io_data=msg_body[Global.BODY])
                    msg_consummed = True
                elif msg_body[Global.TYPE] == Global.REQUEST:
                    self.publish_request_message(msg_body[Global.TOPIC],
                                                 msg_body[Global.BODY])
                    msg_consummed = True
            elif msg_type == Global.DEVICE_INPUT:
                # just forward device messages to switch process
                self.switch_queue.put(new_message)
            else:
                self.log_warning("Unrecognized message type: " + str(msg_type)+ \
                    "\n" + str(msg_body))
        return msg_consummed



    def process_other(self):
        """ perform other none message relared tasks """
        super().process_other()
        pass

    def process_request_roster_message(self, msg_body=None):
        """ process request dcc_command message """
        self.log_info("Roster Request: " + str(msg_body.mqtt_port_id))
        if msg_body.mqtt_port_id in \
                [Global.ROSTER, Global.RFID]:
            self.roster_queue.put((Global.REQUEST, msg_body))
        else:
            self.log_unexpected_message(msg_body=msg_body)
            metadata = {Global.ERROR, "Unknown report requested"}
            reported = Global.ERROR
            self.in_queue.put((Global.PUBLISH, {Global.TYPE: Global.RESPONSE, \
                Global.REPORTED: reported, Global.METADATA: metadata,
                Global.BODY: msg_body}))


    #
    # private functions
    #
    def __process_driver_input(self, new_message):
        """ driver input receive, parse and process it """
        self.log_debug("New Driver Data: " + str(new_message))
        # print(">>> driver in app: " + str(msg_body))
        (_msg_type, msg_body) = new_message
        # print(">>> type: " + str(type(msg_body)))
        if msg_body is not None and \
                not isinstance(msg_body, dict) and \
                not  isinstance(msg_body, str):
            # self.log_info(" ... " + str(msg_body))
            # print(">>> send to cab...")
            if msg_body.command == Global.THROTTLE:
                #print(">>> send to cab...")
                self.cab_queue.put(new_message)
            else:
                self.switch_queue.put(new_message)
        else:
            self.switch_queue.put(new_message)

    def __process_railcom_message(self, io_message):
        """ format a RAILCOM message """
        data = io_message['data']
        block = data.port_id
        port_id = str(block)
        key = self.railcom_map.get(block, None)
        if key is not None:
            dev = self.io_config.io_device_map.get(key, None)
            if dev is not None:
                port_id = dev.mqtt_port_id
        topic = self.mqtt_config.publish_topics.get(Global.LOCATOR, None)
        if topic is not None:
            topic += "/" + port_id
        body = IoData()
        body.mqtt_message_root = Global.LOCATOR
        body.mqtt_port_id = port_id
        body.mqtt_loco_id = data.dcc_id
        body.mqtt_reported = data.mode
        body.mqtt_metadata = {
            Global.TYPE: Global.RAILCOM,
            Global.FACING: data.direction
        }
        super().publish_data_message(topic, body)

    def __process_block_message(self, io_message):
        """ format a BLOCK message """
        data = io_message['data']
        block = data.port_id
        port_id = str(block)
        key = self.block_map.get(block, None)
        if key is not None:
            dev = self.io_config.io_device_map.get(key, None)
            if dev is not None:
                port_id = dev.mqtt_port_id
        reported = Global.UNKNOWN
        if Synonyms.is_on(data.mode):
            reported = Global.OCCUPIED
        elif Synonyms.is_off(data.mode):
            reported = Global.CLEAR
        topic = self.mqtt_config.publish_topics.get(Global.BLOCK, None)
        if topic is not None:
            topic += "/" + port_id
        body = IoData()
        body.mqtt_message_root = Global.BLOCK
        body.mqtt_port_id = port_id
        body.mqtt_reported = reported
        super().publish_data_message(topic, body)
