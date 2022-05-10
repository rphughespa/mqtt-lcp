#!/usr/bin/python3
# # ic2_mux.py
"""

I2cMux - helper class to process i2c mux devices


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

sys.path.append('../../lib/')

from utils.global_constants import Global

from i2c.drivers.i2c_base_driver import I2cBaseDriver
from i2c.devices.i2c_mux_tca9548a import I2cMuxTca9548a


class I2cMux(I2cBaseDriver):
    """ Class for an I2C connected mux device"""
    def __init__(self, i2c_address=None, i2c_bus=None, log_queue=None):
        """ Initialize """
        super().__init__(name="mux",
                         i2c_address=i2c_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)
        self.device_driver = I2cMuxTca9548a(i2c_address=self.i2c_address,
                                            i2c_bus=i2c_bus,
                                            log_queue=self.log_queue)
        self.__initialize_device()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def __initialize_device(self):
        """ initialize the device """
        pass

    def enable_mux_port(self, port_number):
        """ enable a port on thr mux """
        self.device_driver.enable_mux_port(port_number)

    def disable_all_mux_ports(self):
        """ enable a port on thr mux """
        self.device_driver.disable_all_mux_ports()

    def request_device_action(self, message):
        """ send data to i2c device; message is an io_data instance"""
        return (Global.ERROR, "unknown request: " + str(message.mqtt_desired),
                None, None)
