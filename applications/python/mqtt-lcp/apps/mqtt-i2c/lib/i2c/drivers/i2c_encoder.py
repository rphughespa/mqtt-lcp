#!/usr/bin/python3
# # ic2_encoder.py
"""

I2cEncoder.py - Thin wrapper around a low level I2C device driver.
            Adds some business logic for using the device in c
            onjunction wirh MQTT based applications.



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

from utils.global_constants import Global
from structs.io_data import IoData

from i2c.drivers.i2c_base_driver import I2cBaseDriver
from i2c.devices.i2c_encoder_pel12t import I2cEncoderPel12t


ROTATE_CW = "cw"  # rotate clockwise
ROTATE_CCW = "ccw"  # rotate counter clockwise


class I2cEncoder(I2cBaseDriver):
    """ Class for an I2C connected encoder device"""
    def __init__(self,
                 io_devices=None,
                 i2c_bus=None,
                 log_queue=None,
                 rotation=ROTATE_CW,
                 min_counter=0,
                 max_counter=100,
                 auto_color=True):
        """ Initialize """
        self.io_devices = io_devices
        super().__init__(name="encoder",
                         i2c_address=self.io_devices.io_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)
        self.device_driver = I2cEncoderPel12t(i2c_address=self.i2c_address,
                                              i2c_bus=self.i2c_bus,
                                              log_queue=self.log_queue)
        self.counter_value = 0  # current value of knob
        self.rotation = rotation  # direction of rotation
        # change color of know from green to red based on counter
        self.auto_color = auto_color
        self.min_counter_value = min_counter  # min value the counter can be set
        self.max_counter_value = max_counter  # max value the counter cen be set
        self.__initialize_device()

    def __initialize_device(self):
        """ initialize the device """
        pass

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def read_input(self):
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
        return_counter_io_data = None
        return_clicked_io_data = None
        if return_counter is not None:
            return_counter_io_data = IoData()
            return_counter_io_data.mqtt_port_id = self.io_devices.mqtt_port_id
            return_counter_io_data.mqtt_reported = str(return_counter)
            return_counter_io_data.mqtt_metadata = \
                    {Global.TYPE: Global.ENCODER}
        if clicked is not None:
            return_clicked_io_data = IoData()
            return_clicked_io_data.mqtt_port_id = self.io_devices.mqtt_port_id
            return_clicked_io_data.mqtt_reported = Global.CLICKED
            return_clicked_io_data.mqtt_metadata = \
                {Global.TYPE: Global.ENCODER}
        return (return_counter_io_data, return_clicked_io_data)

    def request_device_action(self, message):
        """ send data to i2c device; message is an io_data instance"""
        return_reported = Global.ERROR
        return_message = "Unknown request: " + str(message.mqtt_desired)
        if message.mqtt_desired == Global.RESET:
            self.counter_value = 0
            if self.auto_color:
                self.device_driver.set_encoder_green_thru_red_color(
                    self.counter_value)
            return_reported = Global.RESET
            return_message = None
        return (return_reported, return_message, {
            Global.DATA: str(self.counter_value)
        }, None)
