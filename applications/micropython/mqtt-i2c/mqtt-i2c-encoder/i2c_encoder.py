#!/usr/bin/python3
# # ic2_encoder.py
"""

I2cEncoder.py - Thin wrapper around a low level I2C device driver.
            Adds some business logic for using the device in conjunction wirh MQTT based applications.



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

from global_constants import Global
from io_data import IoData
from utility import Utility

from i2c_encoder_pel12t import I2cEncoderPel12t


ROTATE_CW = "cw"  # rotate clockwise
ROTATE_CCW = "ccw"  # rotate counter clockwise


class I2cEncoder():
    """ Class for an I2C connected encoder device"""
    def __init__(self,
                 name="encoder",
                 io_device=None,
                 node_name=None,
                 pub_topics=None,
                 i2c_bus=None,
                 logger=None,
                 rotation=ROTATE_CW,
                 min_counter=0,
                 max_counter=100,
                 auto_color=True):
        """ Initialize """
        self.io_device = io_device
        self.name = name
        self.pub_topics = pub_topics
        self.sensor_topic = self.pub_topics.get(Global.SENSOR, Global.UNKNOWN) + \
                            "/" + str(self.io_device.mqtt_port_id)
        self.node_name = node_name
        self.logger = logger
        self.port_map = {}
        self.i2c_address = io_device.io_address
        self.i2c_bus = i2c_bus
        if i2c_bus is None:
            self.logger.log_line("I2C Bus not open: ")
        if not isinstance(self.i2c_address, int):
            self.logger.log_line("I2C Address not integer: " + str(self.i2c_address))
        self.device_driver = I2cEncoderPel12t(i2c_address=self.i2c_address,
                                              i2c_bus=self.i2c_bus,
                                              logger=self.logger)
        self.counter_value = 0  # current value of knob
        self.rotation = rotation  # direction of rotation
        # change color of know from green to red based on counter
        self.auto_color = auto_color
        self.min_counter_value = min_counter  # min value the counter can be set
        self.max_counter_value = max_counter  # max value the counter cen be set
        self.__initialize_device()


    def perform_periodic_operation(self):
        messages = None
        (return_counter, clicked) = self.__read_input()
        if return_counter is not None:
            if messages is None:
                messages = []
            self.logger.log_line(str(self.io_device.mqtt_port_id)+": "+str(return_counter))
            body = IoData()
            body.mqtt_port_id = self.io_device.mqtt_port_id
            body.mqtt_reported = return_counter
            body.mqtt_metadata = {Global.TYPE: Global.ENCODER}
            body.mqtt_message_root = Global.SENSOR
            body.mqtt_node_id = self.node_name
            body.mqtt_version = "1.0"
            body.mqtt_timestamp = Utility.now_milliseconds()
            messages.append((self.sensor_topic, body))
        if clicked is not None:
            if messages is None:
                messages = []
            self.logger.log_line(str(self.io_device.mqtt_port_id)+": Clicked")
            body = IoData()
            body.mqtt_port_id = self.io_device.mqtt_port_id
            body.mqtt_reported = Global.CLICKED
            body.mqtt_metadata = {Global.TYPE: Global.ENCODER}
            body.mqtt_message_root = Global.SENSOR
            body.mqtt_node_id = self.node_name
            body.mqtt_version = "1.0"
            body.mqtt_timestamp = Utility.now_milliseconds()
            messages.append((self.sensor_topic, body))
        return messages

    def process_response_message(self, msg_body):
        """ received a response """
        pass

    def process_request_message(self, new_message):
        """ a request message has been received """
        response = None
        self.logger.log_line("Req: " + str(new_message.mqtt_desired) + " ... " + new_message.mqtt_port_id)
        sub_device = self.port_map.get(new_message.mqtt_port_id, None)
        data_reported = None
        return_reported = Global.ERROR
        metadata = None
        if sub_device is not None:
            if response is None:
                response = []
            if new_message.mqtt_desired == Global.RESET:
                self.counter_value = 0
                return_reported = self.counter_value
                data_reported = return_reported
            elif isinstance(new_message.mqtt_desired, int):
                self.counter_value = int(new_message.mqtt_desired)
                return_reported = self.counter_value
                data_reported = return_reported
            else:
                return_reported = Global.ERROR
                metadata = {Global.MESSAGE: "Unknown request: " + str(new_message.mqtt_desired)}
            if self.auto_color:
                self.device_driver.set_encoder_green_thru_red_color(
                    self.counter_value)
            self.logger.log_line("... resp: "+str(return_reported))
            response.append((return_reported, metadata, data_reported, new_message))
        return response

#
# private functions
#
    def __initialize_device(self):
        """ initialize the device """
        self.is_initialized = True
        i2c_bus_devices = self.i2c_bus.scan()
        self.port_map.update({self.io_device.mqtt_port_id: self.io_device})
        self.logger.log_line("I2C Devices: " + str(i2c_bus_devices))

    def __read_input(self):
        """ read data from the device """
        return_counter = None
        (counter_difference, clicked) = self.device_driver.read_input()
        if counter_difference is not None:
            if self.rotation == ROTATE_CCW:
                counter_difference = 0 - counter_difference
            new_counter = self.counter_value + counter_difference
            if new_counter > self.max_counter_value:
                new_counter = self.max_counter_value
            elif new_counter < self.min_counter_value:
                new_counter = self.min_counter_value
            if new_counter != self.counter_value:
                self.counter_value = new_counter
                return_counter = self.counter_value
                if self.auto_color:
                    self.device_driver.set_encoder_green_thru_red_color(
                        self.counter_value)
        return (return_counter, clicked)


