#!/usr/bin/python3
# app_process.py
"""


app_process - the application process for mqtt_i2c

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
import time
import sys

sys.path.append('../lib')

from processes.base_mqtt_process import BaseMqttProcess
from utils.utility import Utility
from utils.global_constants import Global



# from roster_data import LocoData
# from roster_data import RosterData
#from io_data import IoData


class AppProcess(BaseMqttProcess):
    """ Class that waits for an event to occur """

    def __init__(self, events=None, queues=None):
        super().__init__(name="app",
                         events=events,
                         in_queue=queues[Global.APPLICATION],
                         mqtt_queue=queues[Global.MQTT],
                         log_queue=queues[Global.LOGGER])
        self.i2c_queue = queues[Global.I2C]
        self.loco_rfid_map = {}
        self.locator_pub_topic = None
        self.sensor_pub_topic = None
        self.switch_pub_topic = None
        self.log_info("Starting")

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        self.locator_pub_topic = \
            self.mqtt_config.publish_topics.get(Global.LOCATOR, Global.UNKNOWN)
        self.sensor_pub_topic = \
            self.mqtt_config.publish_topics.get(Global.SENSOR, Global.UNKNOWN)
        self.switch_pub_topic = \
            self.mqtt_config.publish_topics.get(Global.SWITCH, Global.UNKNOWN)
        self.publish_dispatcher_report_request(Global.ROSTER)

    def process_request_sensor_message(self, msg_body=None):
        """ process a sensor request """
        self.i2c_queue.put((Global.IO_REQUEST, msg_body))

    def process_request_switch_message(self, msg_body=None):
        """ process a switch request """
        self.i2c_queue.put((Global.IO_REQUEST, msg_body))

    def process_request_signal_message(self, msg_body=None):
        """ process a signal request """
        self.i2c_queue.put((Global.IO_REQUEST, msg_body))

    def process_message(self, new_message):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            msg_consummed = True
            self.log_debug(str(new_message))
            (msg_type, msg_body) = new_message
            if msg_type == Global.RESPONSE:
                self.__process_response(msg_body)
            elif msg_type == Global.RFID:
                self.__process_rfid_tag_read(msg_body)
            elif msg_type == Global.ENCODER:
                self.__process_encoder_read(msg_body)
            elif msg_type == Global.PORT_EXPANDER:
                self.__process_port_expander_read(msg_body)
            else:
                self.log_warning("Unrecognized message type: " + str(msg_type))
        return msg_consummed

    def process_other(self):
        """ perform other none message relared tasks """
        super().process_other()
        _now = time.mktime(time.localtime())
        # self._poll_input_devices()
        # if now > self.exit_time:
        #    print("crashing app_process")
        #    raise ValueError("app_process - time expired")

    def process_response_roster_message(self, msg_body=None):
        """ received registry roster response message """
        #print(">>> registry roster")
        super().process_response_roster_message(msg_body)
        #print(">>> roster: " + str(self.roster))
        #print(">>> roster locos: "+str(type(self.roster.locos)))
        for key, loco in self.roster.locos.items():
            if loco.rfid_id is not None:
                self.loco_rfid_map.update({str(loco.rfid_id): key})
                self.log_info("Loco RFID: " + str(loco.rfid_id) + " : " +
                              str(key))

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

    def __process_rfid_tag_read(self, msg_body):
        """ received a read from a rfid tag reader, send to mqtt"""
        tag_io_data = msg_body[Global.DATA]
        tag_id = tag_io_data.mqtt_metadata[Global.IDENTITY]
        tag_io_data.mqtt_message_root = Global.LOCATOR
        tag_io_data.mqtt_node_id = self.node_name
        tag_io_data.mqtt_version = "1,0"
        loco_id = self.loco_rfid_map.get(tag_id, "???")
        tag_io_data.mqtt_loco_id = loco_id
        tag_io_data.mqtt_timestamp = Utility.now_milliseconds()
        self.log_info("RFID Tag Read Published: " +
                      str(tag_io_data.mqtt_port_id) + " ... " +
                      str(tag_io_data.mqtt_reported))
        self.publish_message(self.locator_pub_topic, tag_io_data)

    def __process_encoder_read(self, msg_body):
        """ received a read fro an encoder, send to mqtt """
        encoder_io_data = msg_body[Global.DATA]
        encoder_io_data.mqtt_message_root = Global.SENSOR
        encoder_io_data.mqtt_node_id = self.node_name
        encoder_io_data.mqtt_version = "1,0"
        encoder_io_data.mqtt_timestamp = Utility.now_milliseconds()
        self.log_info("Encoder Read Published: " +
                      str(encoder_io_data.mqtt_port_id) + " ... " +
                      str(encoder_io_data.mqtt_reported))
        self.publish_message(self.sensor_pub_topic, encoder_io_data)

    def __process_port_expander_read(self, msg_body):
        """ received a read from an port expander, send to mqtt """
        port_expander_io_data = msg_body[Global.DATA]
        port_expander_io_data.mqtt_message_root = Global.SENSOR
        port_expander_io_data.mqtt_node_id = self.node_name
        port_expander_io_data.mqtt_version = "1,0"
        port_expander_io_data.mqtt_timestamp = Utility.now_milliseconds()
        self.log_info("Port Expander Read Published: " +
                      str(port_expander_io_data.mqtt_port_id) + " ... " +
                      str(port_expander_io_data.mqtt_reported))
        self.publish_message(self.sensor_pub_topic, port_expander_io_data)

    def __process_response(self, msg_body):
        """ received a response from i2c_process, send it on to mqtt"""
        response_io_data = msg_body[Global.RESPONSE]
        if response_io_data is not None:
            respond_to = msg_body[Global.RESPOND_TO]
            response_io_data.mqtt_node_id = self.node_name
            response_io_data.mqtt_version = "1,0"
            response_io_data.mqtt_timestamp = Utility.now_milliseconds()
            self.log_info("Response Published: " +
                          str(response_io_data.mqtt_port_id) + " ... " +
                          str(response_io_data.mqtt_reported))
            self.publish_message(respond_to, response_io_data)
        data_io_data = msg_body[Global.DATA]
        if data_io_data is not None:
            msg_root = data_io_data
            data_topic = self.sensor_pub_topic
            if msg_root == Global.LOCATOR:
                data_topic = self.locator_pub_topic
            data_io_data.mqtt_node_id = self.node_name
            data_io_data.mqtt_version = "1,0"
            data_io_data.mqtt_timestamp = Utility.now_milliseconds()
            self.log_info("Data Published: " + str(data_io_data.mqtt_port_id) +
                          " ... " + str(data_io_data.mqtt_reported))
            self.publish_message(data_topic, data_io_data)
