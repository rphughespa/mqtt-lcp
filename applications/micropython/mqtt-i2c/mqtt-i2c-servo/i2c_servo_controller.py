
# # ic2_servo_controller.py
"""

    I2cServoController.py - helper class to process i2c servo controller devices


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
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys

import time

sys.path.append('./lib')

from global_constants import Global
from global_synonyms import Synonyms

from io_device_data import IoDeviceData
from adafruit_servos import Servos


class I2cServoController():
    """ Class for an I2C connected servo controller device"""
    def __init__(self, i2c_bus=None, io_device=None, node_name=None, pub_topics=None, logger=None):
        """ Initialize """
        self.name = "servo controller"
        self.io_device = io_device
        self.pub_topics = pub_topics
        self.i2c_address = self.io_device.io_address
        self.i2c_bus = i2c_bus
        if i2c_bus is None:
            print("I2C Bus not open: ")
        self.logger = logger
        self.device_driver = Servos(self.i2c_bus, address = self.i2c_address)
        self.port_map = {}
        self.input_pin_map = {}
        self.input_pin_report_map = {}
        self.send_after_port_queue = {}  # ports that have active send after operations

    def initialize(self):
        """ init the controller """
        self.__initialize_device()

    def perform_periodic_operation(self):
        """ perform operations that are not related to received messages """
        pass

    def process_response_message(self, new_message):
        """ a response message has been received """
        pass

    def process_request_message(self, new_message):
        """ a request message has been received """
        response = None
        self.logger.log_line("Req: " + str(new_message.mqtt_desired) + " ... " + new_message.mqtt_port_id)
        sub_device = self.port_map.get(new_message.mqtt_port_id, None)
        if sub_device is not None:
            if response is None:
                response = []
            (return_reported, metadata, data_reported) = self.request_device_action(new_message)
            self.logger.log_line("... resp: "+str(return_reported))
            response.append((return_reported, metadata, data_reported, new_message))
        return response

    def process_data_message(self, new_message):
        """ process data message """
        pass

    def read_input(self):
        """ read changed pins on port expander """
        return_data = None
        return return_data

    def request_device_action(self, message):
        """ send rquest to i2c device; message is an io_data instance"""
        return_reported = Global.ERROR
        _return_message = "Unknown request: " + str(message.mqtt_desired)
        if message.mqtt_message_root == Global.SWITCH:
            (return_reported, _return_message, data_reported) = \
                self.__send_request_to_switch(message)
        return (return_reported, None, data_reported)

    def perform_other(self):
        """ perform periodic operations """
        pass

    #
    # private functions
    #

    def __initialize_device(self):
        """ initialize the device """
        if self.io_device.io_sub_devices is not None:
            for (_key, sub_device) in self.io_device.io_sub_devices.items():
                # self.logger.log_line("sub dev: " + str(sub_device.io_sub_address))
                self.__initialize_a_port(sub_device)

    def __initialize_a_port(self, sub_device):
        self.logger.log_line("Port Type: " + str(sub_device.io_device_type))
        if sub_device.io_device_type == Global.SWITCH:
            self.__initialize_a_switch(sub_device)
        else:
            self.logger.log_line(
                "Port Exander Config Error, Unknown device type: " +
                str(sub_device.io_device_type))

    def __initialize_a_switch(self, io_device):
        """ initilaize the output pins for a switch """
        base_pin = io_device.io_sub_address
        open_deg = 90
        close_deg = 0
        number_of_pins = 1  # use only 1 pin for the switch: an on/off toggle
        if isinstance(io_device.io_metadata, dict):
            open_deg = io_device.io_metadata.get(Global.OPEN, 90)
            close_deg = io_device.io_metadata.get(Global.CLOSE, 0)
        # self.device_driver.initialize_channel(base_pin)
        self.device_driver.position(base_pin, open_deg)
        time.sleep_ms(300)
        self.device_driver.position(base_pin, close_deg)
        sub_dev = IoDeviceData()
        sub_dev.dev_type = Global.SWITCH
        sub_dev.base_pin = base_pin
        sub_dev.number_of_pins = number_of_pins
        sub_dev.send_sensor_message = io_device.mqtt_send_sensor_message
        sub_dev.open = open_deg
        sub_dev.close = close_deg
        sub_dev.state = Global.OFF
        self.port_map.update({io_device.mqtt_port_id: sub_dev})

    def __send_request_to_switch(self, message):
        """ send the request to the switch"""
        data_reported = None
        return_reported = Global.ERROR
        return_message = "Unknown request: " + str(message.mqtt_desired)
        #send_after_message = None
        sub_dev = self.port_map.get(message.mqtt_port_id, None)
        if sub_dev is None:
            return_message = "Unknown Port ID: " + \
            str(message.mqtt_port_id)
        else:
            desired = message.mqtt_desired
            if desired == Global.THROW:
                if sub_dev.state == Global.OFF:
                    desired = Global.ON
                else:
                    desired = Global.OFF
            if Synonyms.is_synonym_activate(message.mqtt_desired):
                desired = Global.ON
            elif Synonyms.is_synonym_deactivate(desired):
                desired = Global.OFF
            if desired in (Global.ON, Global.OFF):
                start_pos = sub_dev.close
                end_pos = sub_dev.open
                if desired == Global.OFF:
                    start_pos = sub_dev.open
                    end_pos = sub_dev.close
                if message.mqtt_metadata is not None:
                    start_pos = message.mqtt_metadata.get("start_pos", start_pos)
                    end_pos = message.mqtt_metadata.get("end_pos", end_pos)
                self.__position(message, sub_dev.base_pin, start_pos, end_pos)
                return_reported = Synonyms.desired_to_reported(
                    message.mqtt_desired)
                sub_dev.state = return_reported
                # self.logger.log_line(">>> " + str(message.mqtt_port_id) + \
                # " ... " + str(sub_dev.state) + " ... " + str(len(self.port_map)))
                self.port_map[message.mqtt_port_id] = sub_dev
                return_message = None
        if return_reported != Global.ERROR and sub_dev.send_sensor_message:
            data_reported = return_reported
        if message.mqtt_respond_to is None:
            return_reported = None
            data_reported = None
        return (return_reported, return_message, data_reported)

    def __position(self, _message, base_pin, start_pos, end_pos):
        """ move a server to a desired position """
        # only move one increment at a time,
        # then do a  sendafter message
        # to be notified to do the next increment
        # repeat cycle until servo move is done
        # this prevents one servo move from
        # blocking the i2c bus for long periods
        _send_after_message = None
        incr = 2
        if end_pos < start_pos:
            incr = -1
        if abs(end_pos - start_pos) != 0:
            start_pos += incr
            if incr > 0 and start_pos > end_pos:
                start_pos = end_pos
            elif incr < 0 and start_pos < end_pos:
                start_pos = end_pos
            self.device_driver.position(base_pin, start_pos)
            while end_pos != start_pos:
                time.sleep_ms(30)
                start_pos += incr
                self.device_driver.position(base_pin, start_pos)
