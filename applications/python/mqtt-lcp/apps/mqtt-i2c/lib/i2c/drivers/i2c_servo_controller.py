#!/usr/bin/python3
# # ic2_servo_controller.py
"""

    I2cServoController.py - helper class to process i2c servo controller devices

    This module moves the servo in "slow motion".  That is, the servo is repeatedly requested
    to rotate in small increments until the desired angle is achieved.  There is a small delay
    between movement requests.

    Since the request to move a servo may take a bit of time (several seconds)  the app publishes
    a data "busy" message when the movement begins.  The typical "thrown", "closed" type of
    message response are sent after the movements are completed.

    If a request is received to move a servo while the servo is already engaged is fullfilling
    a previoud request, the new request will rejected and a response of "busy" will be published.


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

sys.path.append('../../lib')

import copy
import time

from utils.global_constants import Global
from utils.global_synonyms import Synonyms
#from structs.io_data import IoData

from structs.io_device_data import IoDeviceData
from processes.base_process import SendAfterMessage

from i2c.drivers.i2c_base_driver import I2cBaseDriver
from i2c.devices.i2c_servo_pca9685 import I2cServoPca9685



class I2cServoController(I2cBaseDriver):
    """ Class for an I2C connected servo controller device"""
    def __init__(self, io_devices=None, i2c_bus=None, log_queue=None):
        """ Initialize """
        self.io_devices = io_devices
        super().__init__(name="servo controller",
                         i2c_address=self.io_devices.io_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)
        self.device_driver = I2cServoPca9685(
            i2c_address=self.io_devices.io_address,
            i2c_bus=i2c_bus,
            log_queue=log_queue)
        self.port_map = {}
        self.input_pin_map = {}
        self.input_pin_report_map = {}
        self.send_after_port_queue = {}  # ports that have active send after operations
        self.__initialize_device()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def read_input(self):
        """ read changed pins on port expander """
        return_data = None
        return return_data

    def request_device_action(self, message):
        """ send rquest to i2c device; message is an io_data instance"""
        #print(">>> servo request")
        return_reported = Global.ERROR
        return_message = "Unknown request: " + str(message.mqtt_desired)
        send_after = None
        if message.mqtt_message_root == Global.SWITCH:
            (return_reported, return_message, data_reported, send_after) = \
                self.__send_request_to_switch(message)
        return (return_reported, return_message, data_reported, send_after)

    def perform_other(self):
        """ perform periodic operations """
        pass

    #
    # private functions
    #

    def __initialize_device(self):
        """ initialize the device """
        if self.io_devices.io_sub_devices is not None:
            for (_key, sub_device) in self.io_devices.io_sub_devices.items():
                self.log_debug("sub dev: " + str(sub_device))
                self.__initialize_a_port(sub_device)

    def __initialize_a_port(self, sub_device):
        self.log_debug("port type: " + str(sub_device.io_device_type))
        if sub_device.io_device_type == Global.SWITCH:
            self.__initialize_a_switch(sub_device)
        else:
            self.log_warning(
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
        self.device_driver.initialize_channel(base_pin)
        self.device_driver.move_servo(base_pin, open_deg)
        time.sleep(0.250)
        self.device_driver.move_servo(base_pin, close_deg)
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
        respond_to = message.mqtt_respond_to
        port_id = message.mqtt_port_id
        data_reported = None
        return_reported = Global.ERROR
        return_message = "Unknown request: " + str(message.mqtt_desired)
        send_after_message = None
        sub_dev = self.port_map.get(message.mqtt_port_id, None)
        if message.mqtt_reported == Global.SERVO:
            send_after_message = self.__move_servo(message, sub_dev)
            if send_after_message is None:
                # movement is finsihed
                # remove port from map to stop
                if port_id in self.send_after_port_queue:
                    del self.send_after_port_queue[port_id]
                return_reported = Synonyms.desired_to_reported(
                    message.mqtt_desired)
                if sub_dev.send_sensor_message:
                    data_reported = return_reported
                sub_dev.state = return_reported
                self.port_map.update({message.mqtt_port_id: sub_dev})
                return_message = None
            else:
                data_reported = None
                return_reported = None
                return_message = None
        else:
            # start a new request
            if sub_dev is None:
                return_message = "Unknown Port ID: " + \
                str(message.mqtt_port_id)
            else:
                desired = message.mqtt_desired
                if desired == Global.TOGGLE:
                    if sub_dev.state == Global.OFF:
                        desired = Global.ON
                    else:
                        desired = Global.OFF
                if Synonyms.is_on(desired):
                    desired = Global.ON
                elif Synonyms.is_off(desired):
                    desired = Global.OFF
                if desired in (Global.ON, Global.OFF):
                    if port_id in self.send_after_port_queue:
                        # device is busy
                        return_reported = Global.BUSY
                        return_message = "Error: Device is Busy"
                    else:
                        self.send_after_port_queue[port_id] = port_id
                        data_reported = Global.BUSY
                        start_pos = sub_dev.close
                        end_pos = sub_dev.open
                        if desired == Global.OFF:
                            start_pos = sub_dev.open
                            end_pos = sub_dev.close
                        if message.mqtt_metadata is not None:
                            start_pos = message.mqtt_metadata.get("start_pos", start_pos)
                            end_pos = message.mqtt_metadata.get("end_pos", end_pos)
                        send_after_message = \
                                self.__build_send_after_message(message, start_pos, end_pos)
                        if sub_dev.send_sensor_message:
                            data_reported = Global.BUSY
                        return_reported = None
                        return_message = None
        return (return_reported, return_message, data_reported,
                send_after_message)

    def __move_servo(self,message, sub_dev):
        """ move a server to a desired position """
        # only move one increment at a time,
        # then do a  sendafter message
        # to be notified to do the next increment
        # repeat cycle until servo movement is done
        # this prevents one servo move from
        # blocking the i2c bus for long periods
        send_after_message = None
        start_pos = message.mqtt_metadata.get("start_pos", sub_dev.open)
        end_pos = message.mqtt_metadata.get("end_pos", sub_dev.close)
        incr = 2
        if end_pos < start_pos:
            incr = 0 - incr
        if abs(end_pos - start_pos) != 0:
            start_pos += incr
            if incr > 0 and start_pos > end_pos:
                start_pos = end_pos
            elif incr < 0 and start_pos < end_pos:
                start_pos = end_pos
            self.device_driver.move_servo(sub_dev.base_pin, start_pos)
            send_after_message = \
                    self.__build_send_after_message(message, start_pos, end_pos)
        return send_after_message

    def __build_send_after_message(self, message, start_pos, end_pos):
        """ build a send after message that will trigger
          the actual servo movements when received """
        servo_io_data = copy.deepcopy(message)
        servo_io_data.mqtt_reported = Global.SERVO
        servo_io_data.mqtt_metadata = {"start_pos": start_pos, "end_pos": end_pos}
        send_after_message = \
                SendAfterMessage(Global.IO_REQUEST, \
                servo_io_data, 50)  # delay in milisecs
        return send_after_message
