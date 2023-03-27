#!/usr/bin/python3
#
"""

I2cRfid.py - Thin wrapper around a low level I2C device driver.
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

sys.path.append('../../lib')

from utils.global_constants import Global
from structs.io_data import IoData

from i2c.drivers.i2c_base_driver import I2cBaseDriver
from i2c.devices.i2c_rfid_attiny64 import I2cRfidAttiny64



class I2cRfid(I2cBaseDriver):
    """ Class for an I2C connected rfid device"""

    def __init__(self, io_devices=None, i2c_bus=None, log_queue=None):
        """ Initialize """
        self.io_devices = io_devices
        super().__init__(name="rfid",
                         i2c_address=self.io_devices.io_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)
        self.device_driver = I2cRfidAttiny64(i2c_address=self.i2c_address,
                                             i2c_bus=self.i2c_bus,
                                             log_queue=self.log_queue)
        self.__initialize_device()

    def __initialize_device(self):
        """ initialize the device """
        pass

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def read_input(self):
        """ Read input from RFID device"""
        # read rfid tag from reader
        tag_list = self.device_driver.read_input()
        return_data = []
        for tag in tag_list:
            # print(">>> "+str(tag))
            tag_io_data = IoData()
            tag_io_data.mqtt_port_id = self.io_devices.mqtt_port_id
            tag_io_data.mqtt_reported = Global.DETECTED
            tag_io_data.mqtt_metadata = {Global.TYPE: Global.RFID,
                                         Global.IDENTITY: str(tag)}
            return_data.append(tag_io_data)
        return return_data

    def request_device_action(self, message):
        """ send data to i2c device; message is an io_data instance"""
        return (Global.ERROR, "unknown request: " + str(message.mqtt_desired),
                None, None)
