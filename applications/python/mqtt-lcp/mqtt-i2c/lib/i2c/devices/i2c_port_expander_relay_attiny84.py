#!/usr/bin/python3
# # ic2_port_expander_relay_attiny84.py
"""

I2cPortExpanderRelayAttiny84 - low level hardware driver for a port expander connected to i2c
            that drives relays using an ATtinny84 driver
            Pin number range from 1 - 4


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

# from utils.bit_utils import BitUtils
from i2c.devices.i2c_base_device import I2cBaseDevice

DUAL_QUAD_TOGGLE_BASE   = 0x00
STATUS_BASE             = 0x04
TURN_ALL_OFF            = 0x0A
TURN_ALL_ON             = 0x0B
SINGLE_OFF              = 0x00
SINGLE_ON               = 0x01

# Define the value of an "Off" relay
STATUS_OFF      = 0

QUAD_RELAY_DEFUALT_ADDR      = 0x6D
QUAD_RELAY_JUMPER_CLOSE_ADDR = 0x6C



class I2cPortExpanderRelayAttiny84(I2cBaseDevice):
    """ Class for an I2C connected relay controller device"""
    def __init__(self, i2c_address=None, i2c_bus=None, log_queue=None):
        """ Initialize """
        super().__init__(name="i2c_port_expander_attiny84",
                         i2c_address=i2c_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)

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
        # print(">>> output pins: " + str(self.i2c_address) + " ... " + \
        #     str(set_pin) + " ... " + str(set_mode))
        if set_mode:
            self.__set_a_pin(set_pin)
            if set_pulse != 0:
                time.sleep(set_pulse / 1000)
                self.__clear_a_pin(set_pin)
        else:
            self.__clear_a_pin(set_pin)
            if set_pulse != 0:
                time.sleep(set_pulse / 1000)
                self.__set_a_pin(set_pin)

    def __initialize_device(self):
        """ initialize the device """
        self.__clear_all_pins()
        ## special test code ##
        # self.__test_relay_board()

    def __clear_all_pins(self):
        """ turn off all relays """
        # self.i2c_bus._i2c.writeCommand(self.address, TURN_ALL_OFF)
        #self.i2c_bus.write_i2c_byte_data(self.i2c_address, TURN_ALL_OFF, 1)
        for pin in range(1,5):
            # print(">>> pin: " + str(pin))
            # self.__set_a_pin(pin)
            self.i2c_bus.write_byte(self.i2c_address, DUAL_QUAD_TOGGLE_BASE + pin)
            time.sleep(0.500)
            # self.__clear_a_pin(pin)
            self.i2c_bus.write_byte(self.i2c_address, DUAL_QUAD_TOGGLE_BASE + pin)

    def __set_a_pin(self, selected_pin):
        """ turn on a relay """
        # pin on relay are 1-4
        if not 1 <= selected_pin <= 4:
            self.log_error("Invalid Relay Number, must be 1 - 4: " +
                           str(selected_pin))
        else:
            pin_reg = STATUS_BASE + selected_pin
            # temp = self._i2c.readByte(self.address, STATUS_BASE + selected)
            status = self.i2c_bus.read_byte(self.i2c_address, pin_reg)
            # print(">>> stat: " + str(selected_pin) + " ... " + \
            #        str(pin_reg) + \
            #        " ... " + str(STATUS_OFF) + " ... " + str(status))
            if status == STATUS_OFF:
                #return self._i2c.writeCommand(self.address, DUAL_QUAD_TOGGLE_BASE + selected_pin)
                self.i2c_bus.write_byte(self.i2c_address, DUAL_QUAD_TOGGLE_BASE + selected_pin)

    def __clear_a_pin(self, selected_pin):
        """ turn on a relay """
        # pin on relay are 1-4
        if not 1 <= selected_pin <= 4:
            self.log_error("Invalid Relay Number, must be 1 - 4: " +
                           str(selected_pin))
        else:
            status = self.i2c_bus.read_byte(self.i2c_address, STATUS_BASE + selected_pin)
            # print(">>> stat: " + str(selected_pin) + " ... " + \
            #         str(STATUS_BASE + selected_pin) + \
            #         " ... " + str(STATUS_OFF) + " ... " + str(status))
            if status != STATUS_OFF:
                #return self._i2c.writeCommand(self.address, DUAL_QUAD_TOGGLE_BASE + selected_pin)
                self.i2c_bus.write_byte(self.i2c_address, DUAL_QUAD_TOGGLE_BASE + selected_pin)

#    def __send_command(self, command):
#        """ send a command """
#        rett = self.__read_command(command)
#        return rett

#    def __read_command(self, command):
#        """ read a command """
#        self.i2c_bus.write_byte(self.i2c_address, command)
