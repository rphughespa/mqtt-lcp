#!/usr/bin/python3
# # ic2_port_expander_relay.py
"""

    I2cPortExpanderRelay.py - helper class to process i2c port expander relay devices
            This class contains the hardware specific funtionality to turn pins on/off.
            The base class, I2cPortExpanderBase, contains the business logic
            which determines which pins to turn/off for a given request.

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

import sys, time, gc

from global_constants import Global
from global_synonyms import Synonyms
from io_data import IoData
from bit_utils import BitUtils

from io_device_data import IoDeviceData

from i2c_port_expander_base import I2cPortExpanderBase
# from ise_relay_16 import relay16

class I2cPortExpanderRelay(I2cPortExpanderBase):
    """ Class for an I2C connected port expander device"""

    def __init__(self, i2c_bus=None, io_device=None, node_name=None, pub_topics=None,logger=None):
        """ Initialize """
        super().__init__(io_device=io_device, node_name=node_name, pub_topics=pub_topics,logger=logger)
        self.name="port expander_relay"
        self.logger = logger
        self.i2c_address = self.io_device.io_address
        self.i2c_bus = i2c_bus
        self.reg_a = 0x00  # pins 0-7
        self.reg_b = 0x00  # pins 8-15

    def initialize(self):
        """ initialize class """
        print("Initialize Relay Port Expander")
        print("i2c: "+str(self.i2c_bus.scan()))
        self.initialize_device()
        super().initialize()

   
    def send_pin_changes(self, selected_pins):
        """ send pin changes to the device """
        # some pins groups may have mutually exclusive pins
        # set the "off" pins first
        # print(">>> set pins: "+str(selected_pins))
        for (set_pin, set_mode, set_pulse) in selected_pins:
            if not set_mode:
                #print(">>> "+str(set_pin)+" ... "+str(set_mode))
                self.set_output_pin(set_pin, set_mode, set_pulse)
        # set the "on" pins next
        for (set_pin, set_mode, set_pulse) in selected_pins:
            if set_mode:
                #print(">>> "+str(set_pin)+" ... "+str(set_mode))
                self.set_output_pin(set_pin, set_mode, set_pulse)

    def read_input(self):
        """ Read input from relay_controller device"""
        return None

    def init_input_pin(self, _out_pin, active_low=True):
        """ initailize an input pin """
        pass

    def init_output_pin(self, _out_pin, active_low=True):
        """ initailize an output pin """
        pass

    def set_output_pin(self, set_pin, set_mode, set_pulse):
        """ turn on/off relays """
        # print(">>> output pins:" + str(set_pin) + " ... " + str(set_mode))
        if set_mode:
            self.set_a_pin(set_pin)
            self.update_device_pins(self.reg_a, self.reg_b)
            if set_pulse != 0:
                time.sleep(set_pulse / 1000)
                self.clear_a_pin(set_pin)
                self.update_device_pins(self.reg_a, self.reg_b)
        else:
            self.clear_a_pin(set_pin)
            self.update_device_pins(self.reg_a, self.reg_b)
            if set_pulse != 0:
                time.sleep(set_pulse / 1000)
                self.set_a_pin(set_pin)
                self.update_device_pins(self.reg_a, self.reg_b)
#
#
    def initialize_device(self):
        """ initialize the device """
        self.clear_all_pins()
        ## special test code ##
        # self.test_relay_board()

    def clear_all_pins(self):
        """ turn off all relays """
        self.reg_a = 0x00
        self.reg_b = 0x00
        self.update_device_pins(self.reg_a, self.reg_b)

    def set_a_pin(self, selected_pin):
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

    def clear_a_pin(self, selected_pin):
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

    def update_device_pins(self, reg_a, reg_b):
        """ send new register controller board """
        # note: bits reeversed on write; on=off, off=on
        # self.i2c_bus.write_i2c_block_data(self.i2c_address, 0x00,
        #                                  [~(reg_a), ~(reg_b)])
        byte1 = ~(reg_a)
        byte2 = ~(reg_b)
        # print(">>> bytes: " + str(hex(byte1)) + " ... " + str(hex(byte2)))
        #self.i2c_bus.write_i2c_block_data(self.i2c_address, byte1, [byte2])
        # print(">>> i2c: "+str(self.i2c_bus.scan()))
        self.i2c_bus.writeto_mem(self.i2c_address, 0x00, bytearray([byte2, byte1]))
