#!/usr/bin/python3
# appe_process.py
"""


app_process - the application process for mqtt-railcom


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
import copy

from utils.global_constants import Global
from utils.global_synonyms import Synonyms

from structs.io_data import IoData
# from structs.gui_message import GuiMessage
from processes.base_process import SendAfterMessage
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
        self.response_queue_name = Global.TURNTABLE + ":" + Global.RESPONSE
        self.response_queue = queues[self.response_queue_name]
        self.turntable_is_busy = False
        self.current_request = None
        self.last_port_request= None
        self.block_map = None
        self.railcom_map = None
        self.switch_topic = None
        self.turntable_busy_send_after_message = None

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

        self.switch_topic = self.mqtt_config.publish_topics.get(Global.SWITCH, None)
        # call check busy every second
        self.turntable_busy_send_after_message = \
                SendAfterMessage(Global.TURNTABLE + ":" + Global.BUSY, None, 1000)
                 # call check busy every 5 seconds
        self.__publish_all_tracks_inactive_messages()

    def process_message(self, new_message=None):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            # print(">>> new message: " + str(new_message))
            (msg_type, msg_body) = new_message
            # print("())() "+str(log_message))
            if msg_type == Global.TURNTABLE + ":" + Global.BUSY:
                self.__check_turntable_busy()
                msg_consummed = True
            if msg_type == Global.DEVICE_INPUT:
                self.__process_serial_message_message(msg_body)
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


    def process_request_switch_message(self, msg_body=None):
        """ process for switch requests """
        msg_consummed = False
        if self.turntable_is_busy:
            self.__send_busy_response(msg_body)
            msg_consummed = True
        else:
            command = self.__generate_turntable_command_by_port_id(msg_body)
            if command is not None:
                self.serial_queue.put((Global.DEVICE_SEND, command))
                self.turntable_is_busy = True
                self.current_request = msg_body
                if self.last_port_request is not None:
                    self.__publish_data_message(msg_body, reported=msg_body.mqtt_desired)
                else:
                    self.__publish_data_message(msg_body, reported=Global.UNKNOWN)
                self.send_after(self.turntable_busy_send_after_message)
                msg_consummed = True
        return msg_consummed
    #
    # private functions
    #

    def __process_serial_message_message(self, io_message):
        msg_text = io_message
        if isinstance(io_message, dict):
            msg_text = io_message[Global.TEXT]
        if msg_text.startswith("#INFO"):
            self.__parse_turntable_info_response(msg_text)

    def __check_turntable_busy(self):
        """ check is turntable is busy """
        if self.turntable_is_busy:
            send_message = {Global.TEXT:"!INFO", \
                    Global.RESPONSE_QUEUE: self.response_queue_name}
            self.serial_queue.put(
                (Global.DEVICE_SEND, send_message))
            self.send_after(self.turntable_busy_send_after_message)

    def __send_busy_response(self, msg_body):
        """ send a turntable is busy response """
        self.__publish_response(msg_body, Global.BUSY, "Turntable is Busy", None)

    def __parse_turntable_info_response(self, info_message):
        """ parse the info message from the turntable """
        splits = info_message.split()
        if len(splits) > 1:
            speed = splits[1]
            if speed == "0":
                # turntable is not moving
                self.turntable_is_busy = False
                if self.current_request is not None:
                    reported = self.current_request.mqtt_desired
                    #if self.last_port_request is not None:
                    #    reported = Global.CLOSED
                    self.__publish_response(self.current_request, reported, \
                            None, reported)
                self.current_request = None

    def __publish_data_message(self, msg_body, reported=Global.UNKNOWN):
        """ publish a busy data message """
        if self.switch_topic is not None and msg_body is not None:
            data_msg_body = copy.deepcopy(msg_body)
            data_msg_body.mqtt_reported = reported
            data_msg_body.mqtt_desired = None
            data_msg_body.mqtt_respond_to = None
            self.publish_data_message(self.switch_topic, data_msg_body)

    def __publish_response(self, msg_body, reported, message, data_reported):
        """ send response back to requestor """
        metadata = None
        if message is not None:
            metadata = {Global.ERROR: message}
        self.publish_response_message(\
                reported=reported,
                metadata=metadata,
                data_reported=data_reported,
                message_io_data=msg_body)

    def __generate_turntable_command_by_port_id(self, msg_body):
        """ generate the command by the port-id """
        command = None
        config_key = \
            self.io_config.io_port_map.get(msg_body.mqtt_port_id, None)
        if config_key is not None:
            config_item = self.io_config.io_device_map.get(config_key, None)
            if config_item is not None:
                # print("inv item: " + str(config_item))
                track = config_item.io_address
                desired = msg_body.mqtt_desired
                self.log_info("Rotate: "+str(desired)+" to "+str(track))
                if msg_body.mqtt_port_id == Global.HOME:
                    command = "!HOME"
                elif desired == Global.HEAD:
                    command = "!TRACK " + str(track) + " H"
                elif desired == Global.TAIL:
                    command = "!TRACK " + str(track) + " T"
                if self.last_port_request is not None:
                    self.__publish_data_message(self.last_port_request, reported=Global.UNKNOWN)
                self.last_port_request = msg_body
        return command

    def __publish_all_tracks_inactive_messages(self):
        """ notify all subscribes that no track is active """
        for _key,item in self.io_config.io_device_map.items():
            data_msg_body = IoData()
            data_msg_body.mqtt_message_root = Global.SWITCH
            data_msg_body.mqtt_port_id = item.mqtt_port_id
            data_msg_body.mqtt_reported = Global.UNKNOWN
            data_msg_body.mqtt_desired = None
            data_msg_body.mqtt_respond_to = None
            self.publish_data_message(self.switch_topic, data_msg_body)
