#!/usr/bin/python3
# # ic2_port_expander_relay16_qwiic.py
"""

I2cPortExpanderRelay - low level hardware driver fot a port expander connected to i2c
            using the a relay 16 qwiic circuit device.   Pin number range from 1 - 16


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

sys.path.append('../../../lib')

import time

# from global_constants import Global

from utils.bit_utils import BitUtils
from i2c.devices.i2c_base_device import I2cBaseDevice


class I2cPortExpanderRelay16Qwiic(I2cBaseDevice):
    """ Class for an I2C connected relay controller device"""
    def __init__(self, i2c_address=None, i2c_bus=None, log_queue=None):
        """ Initialize """
        super().__init__(name="i2c_port_expander_relay16_qwiic",
                         i2c_address=i2c_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)
        self.reg_a = 0x00  # pins 0-7
        self.reg_b = 0x00  # pins 8-15
        self.__initialize_device()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def read_input(self):
        """ Read input from relay_controller device"""
        return []

    def init_output_pin(self, _out_pin, active_low=True):
        """ initailize an output pin """
        pass

    def set_output_pin(self, set_pin, set_mode, set_pulse):
        """ turn on/off relays """
        # print(">>> output pins:" + str(set_pin) + " ... " + str(set_mode))
        if set_mode:
            self.__set_a_pin(set_pin)
            self.__update_device_pins(self.reg_a, self.reg_b)
            if set_pulse != 0:
                time.sleep(set_pulse / 1000)
                self.__clear_a_pin(set_pin)
                self.__update_device_pins(self.reg_a, self.reg_b)
        else:
            self.__clear_a_pin(set_pin)
            self.__update_device_pins(self.reg_a, self.reg_b)
            if set_pulse != 0:
                time.sleep(set_pulse / 1000)
                self.__set_a_pin(set_pin)
                self.__update_device_pins(self.reg_a, self.reg_b)

    def __initialize_device(self):
        """ initialize the device """
        self.__clear_all_pins()
        ## special test code ##
        # self.__test_relay_board()

    def __clear_all_pins(self):
        """ turn off all relays """
        self.reg_a = 0x00
        self.reg_b = 0x00
        self.__update_device_pins(self.reg_a, self.reg_b)

    def __set_a_pin(self, selected_pin):
        """ turn on a relay """
        # pin on relay are 1-16, not 0-15
        # print(">>> ... pin set: "+str(selected_pin))
        if not 0 <= selected_pin <= 15:
            self.log_error("Invalid Relay Number, must be 1 -16: " +
                           str(selected_pin))
        else:
            if 0 <= selected_pin <= 7:
                self.reg_a = BitUtils.set_a_bit(self.reg_a, selected_pin)
            else:
                self.reg_b = BitUtils.set_a_bit(self.reg_b, selected_pin - 8)

    def __clear_a_pin(self, selected_pin):
        """ turn on a relay """
        # print(">>>  ... pin clear: "+str(selected_pin))
        if not 0 <= selected_pin <= 15:
            self.log_error("Invalid Relay Number, must be 1 -16: " +
                           str(selected_pin))
        else:
            if 0 <= selected_pin <= 7:
                self.reg_a = BitUtils.clear_a_bit(self.reg_a, selected_pin)
            else:
                self.reg_b = BitUtils.clear_a_bit(self.reg_b, selected_pin - 8)

    def __update_device_pins(self, reg_a, reg_b):
        """ send new register controller board """
        # note: bits reeversed on write; on=off, off=on
        # self.i2c_bus.write_i2c_block_data(self.i2c_address, 0x00,
        #                                  [~(reg_a), ~(reg_b)])
        byte1 = ~(reg_a)
        byte2 = ~(reg_b)
        # print(">>> bytes: " + str(hex(byte1)) + " ... " + str(hex(byte2)))
        self.i2c_bus.write_i2c_block_data(self.i2c_address, byte1, [byte2])
