#!/usr/bin/python3
# appe_process.py
"""


app_process - the application process for mqtt-railcom


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

sys.path.append('../lib')

import time

from utils.global_constants import Global
from utils.global_synonyms import Synonyms

from structs.io_data import IoData
from processes.base_mqtt_process import BaseMqttProcess


class AppProcess(BaseMqttProcess):
    """ Class that waits for an event to occur """
    def __init__(self, events=None, queues=None):
        super().__init__(name="app",
                         events=events,
                         in_queue=queues[Global.APPLICATION],
                         mqtt_queue=queues[Global.MQTT],
                         log_queue=queues[Global.LOGGER])
        self.log_info("Starting")
        self.serial_queue = queues[Global.DEVICE]
        self.block_map = None
        self.railcom_map = None

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

    def process_message(self, new_message=None):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            # print(">>> new message: " + str(new_message))
            (msg_type, msg_body) = new_message
            # print("())() "+str(log_message))
            if msg_type == Global.DEVICE_INPUT:
                self.__process_serial_message_message(msg_body)
                msg_consummed = True
            elif msg_type == Global.DEVICE_INPUT_BLOCK_DATA:
                self.__process_serial_block_message(msg_body)
                msg_consummed = True
            elif msg_type == Global.DEVICE_INPUT_RAILCOM_DATA:
                self.__process_serial_railcom_message(msg_body)
                msg_consummed = True
            elif msg_type == Global.PUBLISH:
                if msg_body[Global.TYPE] == Global.DATA:
                    self.publish_data_message(msg_body[Global.TOPIC],
                                              msg_body[Global.BODY])
                    msg_consummed = True
                elif msg_body[Global.TYPE] == Global.RESPONSE:
                    # response: " + str(msg_body))
                    self.publish_response_message(msg_body[Global.REPORTED], \
                                    msg_body[Global.METADATA], msg_body[Global.BODY])
                    msg_consummed = True
                elif msg_body[Global.TYPE] == Global.REQUEST:
                    self.publish_request_message(msg_body[Global.TOPIC],
                                                 msg_body[Global.BODY])
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

    def process_request_registry_message(self, msg_body=None):
        """ process request registry message """
        report_desired = msg_body.get_desired_value_by_key(Global.REPORT)
        if report_desired == Global.INVENTORY:
            self.report_inventory(msg_body=msg_body)
        else:
            self.log_unexpected_message(msg_body=msg_body)

    #
    # private functions
    #

    def __process_serial_message_message(self, io_message):
        text = io_message["text"]
        print("Serial Message Received:" + str(text))

    def __process_serial_railcom_message(self, io_message):
        """ format a RAILCOM message """
        data = io_message['data']
        block = data['block']
        port_id = "railcom:" + str(block)
        key = self.railcom_map.get(block, None)
        if key is not None:
            dev = self.io_config.io_device_map.get(key, None)
            if dev is not None:
                port_id = dev.mqtt_port_id
        body = IoData()
        body.mqtt_message_root = Global.LOCATOR
        body.mqtt_port_id = port_id
        body.mqtt_loco_id = data['loco']
        body.mqtt_reported = data['state']
        body.mqtt_metadata = {
            Global.TYPE: Global.RAILCOM,
            Global.FACING: data['facing']
        }
        super().publish_sensor_data_message(body)

    def __process_serial_block_message(self, io_message):
        """ format a BLOCK message """
        data = io_message['data']
        block = data['block']
        port_id = "block:" + str(block)
        key = self.block_map.get(block, None)
        if key is not None:
            dev = self.io_config.io_device_map.get(key, None)
            if dev is not None:
                port_id = dev.mqtt_port_id
        reported = {Global.BLOCK: Global.UNKNOWN}
        if Synonyms.in_synonym_activate(data['state']):
            reported = Global.OCCUPIED
        elif Synonyms.in_synonym_deactivate(data['state']):
            reported = Global.CLEAR
        body = IoData()
        body.mqtt_message_root = Global.BLOCK
        body.mqtt_port_id = port_id
        body.mqtt_reported = reported
        super().publish_sensor_data_message(body)
