#!/usr/bin/python3
# i2c_mux_tca9548a.py
"""

    I2CMuxTca9548 - low level hardware driver for an
        I2C multiplexer based on the tca9548 circuit device

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

sys.path.append('../../../lib')

# from smbus2 import SMBus

# from global_constants import Global
from utils.bit_utils import BitUtils
from i2c.devices.i2c_base_device import I2cBaseDevice


class I2cMuxTca9548a(I2cBaseDevice):
    """ Class to define and manipulate a mux device on an I2C bus"""
    def __init__(self, i2c_address=None, i2c_bus=None, log_queue=None):
        super().__init__(name="i2c_mux_tca9548a",
                         i2c_address=i2c_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)
        self.__initialize_device()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def enable_mux_port(self, port_number):
        """ Enable a mux port, exposes device on that port to the I2C bus. """
        # port number must be 0-7
        self.log_debug("Enable Mux Port: " + str(self.i2c_address) + " ... " +
                       str(port_number))
        port_number = min(port_number, 7)

        # Read the current mux settings
        try:
            new_settings = BitUtils.set_a_bit(0x00, port_number)
            #print("enable mux write: "+str(new_settings))
            # print(" ... enable: "+str(hex(settings))+".."+str(hex(new_settings)))
            self.i2c_bus.write_i2c_block_data(self.i2c_address, 0,
                                              [new_settings])
        except Exception as exc:
            self.log_error("Exception during mux port enable: " + str(exc))

    def disable_all_mux_ports(self):
        """ Disable a mux port"""
        try:
            self.i2c_bus.write_i2c_block_data(self.i2c_address, 0, [0x00])
        except Exception as exc:
            # log as debug because failure here not that important
            self.log_debug("Exception during mux port disable: " + str(exc))

    def __initialize_device(self):
        """ initialize the device """
        self.disable_all_mux_ports()
