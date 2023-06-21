#!/usr/bin/python3
# ic2_port_expander_mcp23017.py
"""

I2cPortExpanderMcp23017 - low level hardware driver fot a port expander connected to i2c
             using the mcp23017 circuit device


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

# from smbus2 import SMBus

#  I/O direction registers
REG_IODIR_A = 0x00
REG_IODIR_B = 0x01

# Input polarity port registers
REG_IPOL_A = 0x02
REG_IPOL_B = 0x03

# Interrupt-on-change pins
REG_GPINTEN_A = 0x04
REG_GPINTEN_B = 0x05

# Default value registers
REG_DEFVAL_A = 0x06
REG_DEFVAL_B = 0x07

# Interrupt-on-change control registers
REG_INTCON_A = 0x08
REG_INTCON_B = 0x09

# I/O expander configuration registers
REG_IOCON_A = 0x0A
REG_IOCON_B = 0x0B

# GPIO pull-up resistor registers
REG_GPPU_A = 0x0C
REG_GPPU_B = 0x0D

# Interrupt flag registers
REG_INTF_A = 0x0E
REG_INTF_B = 0x0F

# Interrupt captured value for port registers
REG_INTCAP_A = 0x10
REG_INTCAP_B = 0x11

# General purpose I/O port registers
REG_GPIO_A = 0x12
REG_GPIO_B = 0x13

# Output latch register 0
REG_OLAT_A = 0x14
REG_OLAT_B = 0x15

# Interrupt error
REG_INT_ERR = 0xFF

# @port_address 96

import sys

sys.path.append('../../../lib')

import time

# from global_constants import Globalquit

from utils.bit_utils import BitUtils
from i2c.devices.i2c_base_device import I2cBaseDevice


class I2cPortExpanderMcp23017(I2cBaseDevice):
    """ Class for an I2C connected mcp23017 port expander  device"""
    def __init__(self, i2c_address=None, i2c_bus=None, log_queue=None):
        """ Initialize """
        super().__init__(name="i2c_port_expander_mcp23017",
                         i2c_address=i2c_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)
        self.port_map = {}
        self.pin_active_low = {}
        self.last_gpio_a = 0x00
        self.last_gpio_b = 0x00
        self.changed_gpio_a = 0x00
        self.changed_gpio_b = 0x00
        self.has_inputs = False
        self.__initialize_device()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def read_input(self):
        """ Read input from port_expander device"""
        # do one read, gpio b just after gpio_a
        read_pins = []
        if self.has_inputs:
            changed_pins = self.__read_input_pins()
            read_pins += changed_pins
        if not read_pins:
            read_pins = None
        # else:
        #    print(">>> ... "+str(read_pins))
        return read_pins

    def init_output_pin(self, selected_pin, active_low=True):
        """ set a pin into output_mode """
        # pins must be 0-15
        iodir_reg = None
        gpio_reg = None

        reg_bit = None
        if 0 <= selected_pin <= 7:
            iodir_reg = REG_IODIR_A
            gpio_reg = REG_GPIO_A
            reg_bit = selected_pin
        elif 8 <= selected_pin <= 15:
            iodir_reg = REG_IODIR_B
            gpio_reg = REG_GPIO_B
            reg_bit = selected_pin - 8
        else:
            self.log_error("Port expander pins must be 0-15: {" +
                           str(selected_pin) + "}")
        self.pin_active_low[selected_pin] = active_low
        if iodir_reg is not None:
            # 1 = input, 0 = output
            self.__clear_a_register_bit(iodir_reg, reg_bit)
            if active_low:
                # turn on pin as init value
                self.__set_a_register_bit(gpio_reg, reg_bit)
            else:
                # turn off pin as init_value
                self.__clear_a_register_bit(gpio_reg, reg_bit)
            self.log_debug("Init Output Pin: " + " ... " + str() +
                           str(selected_pin))

    def init_input_pin(self, selected_pin, active_low=True):
        """ set a pin into output_mode """
        # pins must be 0-15
        iodir_reg = None
        gpio_reg = None
        gpinten_reg = None
        gppu_reg = None
        intcon_reg = None
        reg_bit = None
        if 0 <= selected_pin <= 7:
            iodir_reg = REG_IODIR_A
            gpio_reg = REG_GPIO_A
            gpinten_reg = REG_GPINTEN_A
            intcon_reg = REG_INTCON_A
            gppu_reg = REG_GPPU_A
            reg_bit = selected_pin
        elif 8 <= selected_pin <= 15:
            iodir_reg = REG_IODIR_B
            gpio_reg = REG_GPIO_B
            gpinten_reg = REG_GPINTEN_B
            intcon_reg = REG_INTCON_B
            gppu_reg = REG_GPPU_B
            reg_bit = selected_pin - 8
        else:
            self.log_error("Port expander pins must be 0-15: {" +
                           str(selected_pin) + "}")
        self.has_inputs = True
        self.pin_active_low[selected_pin] = active_low
        if iodir_reg is not None:
            # 1 = input, 0 = output
            # by default all pins already initialized as input
            # self.__clear_a_register_bit(iodir_reg, reg_bit)
            # set pullup on all input pins
            self.__set_a_register_bit(gppu_reg, reg_bit)
            if self.pin_active_low[selected_pin]:
                # turn on pin as init value
                self.__set_a_register_bit(gpio_reg, reg_bit)
            else:
                # turn off pin as init_value
                self.__clear_a_register_bit(gpio_reg, reg_bit)
            # set pin to trigger interrupt on change
            self.__set_a_register_bit(gpinten_reg, reg_bit)
            # set pin to interrupt when value changes
            self.__clear_a_register_bit(intcon_reg, reg_bit)
            self.log_debug("Init Interrupt Input Pin: " + " ... " + str() +
                           str(selected_pin))

    def set_output_pin(self, selected_pin, pin_on=False, pulse=0):
        """ set a output pin on or off """
        # pins must be 0-15
        gpio_reg = None
        reg_bit = None
        if 0 <= selected_pin <= 7:
            gpio_reg = REG_GPIO_A
            reg_bit = selected_pin
        elif 8 <= selected_pin <= 15:
            gpio_reg = REG_GPIO_B
            reg_bit = selected_pin - 8
        else:
            self.log_error("Port expander pins must be 0-15: {" +
                           str(selected_pin) + "}")
        # self.pin_active_low[selected_pin] = active_low
        pin_mode = pin_on
        if self.pin_active_low[selected_pin]:
            pin_mode = not pin_mode
        if gpio_reg is not None:
            if pin_mode:
                # turn on pin
                self.__set_a_register_bit(gpio_reg, reg_bit)
                if pulse != 0:
                    time.sleep(pulse / 1000)
                    self.__clear_a_register_bit(gpio_reg, reg_bit)
            else:
                # turn off pin
                self.__clear_a_register_bit(gpio_reg, reg_bit)
                if pulse != 0:
                    time.sleep(pulse / 1000)
                    self.__set_a_register_bit(gpio_reg, reg_bit)

    def read_input_pin(self, selected_pin):
        """ read a input pin on or off """
        # pins must be 0-15
        gpio_reg = None
        reg_bit = None
        if 0 <= selected_pin <= 7:
            gpio_reg = REG_GPIO_A
            reg_bit = selected_pin
        elif 8 <= selected_pin <= 15:
            gpio_reg = REG_GPIO_B
            reg_bit = selected_pin - 8
        else:
            self.log_error("Port expander pins must be 0-15: {" +
                           str(selected_pin) + "}")

        pin_setting = None
        if gpio_reg is not None:
            pin_setting = self.__isset_a_register_bit(gpio_reg, reg_bit)
            if self.pin_active_low[selected_pin]:
                pin_setting = not pin_setting
        return pin_setting

#
# private functions
#

    def __read_input_pins(self):
        """ read input pin values """
        fixed_pins = []
        changed_pins = []
        try:
            gpio_regs = self.i2c_bus.read_i2c_block_data(
                self.i2c_address, REG_GPIO_A, 1)
            # print(">>> " + str(gpio_regs))
            gpio_a = gpio_regs[0]
            gpio_regs = self.i2c_bus.read_i2c_block_data(
                self.i2c_address, REG_GPIO_B, 1)
            gpio_b = gpio_regs[0]
            self.changed_gpio_a = BitUtils.bits_different(
                gpio_a, self.last_gpio_a)
            self.last_gpio_a = gpio_a
            self.changed_gpio_b = BitUtils.bits_different(
                gpio_b, self.last_gpio_b)
            self.last_gpio_b = gpio_b
            changed_pins = self.__test_for_changes(changed_pins, 0,
                                                   self.changed_gpio_a,
                                                   self.last_gpio_a)
            changed_pins = self.__test_for_changes(changed_pins, 8,
                                                   self.changed_gpio_b,
                                                   self.last_gpio_b)
        except Exception as exc:
            self.log_error("Exception during mcp23107 read: " + str(exc))
        if changed_pins:
            for (pin, on_off) in changed_pins:
                pin_active_low = self.pin_active_low.get(pin, True)
                # print(">>> " + str(pin) + " ... " +
                #      str(on_off) + " ... " + str(pin_active_low))
                if pin_active_low:
                    fixed_pins.append((pin, not on_off))
                else:
                    fixed_pins.append((pin, on_off))
        return fixed_pins

    def __initialize_device(self):
        """ initialize the device """
        # initally mark all pins as active low
        for p in range(0, 16):
            self.pin_active_low[p] = True

        # read all registers
        all_regs = self.i2c_bus.read_i2c_block_data(self.i2c_address, 0x00, 22)
        self.log_debug("All Regs: " + str(self.i2c_address) + " ... " +
                       str(all_regs))

        # read io con registers
        io_con_a = self.i2c_bus.read_i2c_block_data(self.i2c_address,
                                                    REG_IOCON_A, 1)
        self.log_debug("IO CON A: " + str(io_con_a))
        io_con_b = self.i2c_bus.read_i2c_block_data(self.i2c_address,
                                                    REG_IOCON_B, 1)
        self.log_debug("IO CON B: " + str(io_con_b))

        # set all pins to input
        self.i2c_bus.write_i2c_block_data(self.i2c_address, REG_IODIR_A,
                                          [0xff])
        self.i2c_bus.write_i2c_block_data(self.i2c_address, REG_IODIR_B,
                                          [0xff])

        # Turn off interrupt triggers
        self.i2c_bus.write_i2c_block_data(self.i2c_address, REG_GPINTEN_A,
                                          [0x00])
        self.i2c_bus.write_i2c_block_data(self.i2c_address, REG_GPINTEN_B,
                                          [0x00])

        # Turn off pull up resistors
        self.i2c_bus.write_i2c_block_data(self.i2c_address, REG_GPPU_A, [0x00])
        self.i2c_bus.write_i2c_block_data(self.i2c_address, REG_GPPU_B, [0x00])

        # Turn off gpio resistors
        self.i2c_bus.write_i2c_block_data(self.i2c_address, REG_GPIO_A, [0x00])
        self.i2c_bus.write_i2c_block_data(self.i2c_address, REG_GPIO_B, [0x00])

        # READ ALL REGISTERS
        all_regs = self.i2c_bus.read_i2c_block_data(self.i2c_address, 0x00, 22)
        self.log_debug("All Regs: " + str(self.i2c_address) + " ... " +
                       str(all_regs))

    def __set_a_register_bit(self, selected_register, selected_bit):
        """ set a bit in a register """
        # bits are offsets 0-7
        current_register_value = self.i2c_bus.read_i2c_block_data(
            self.i2c_address, selected_register, 1)
        new_register_value = BitUtils.set_a_bit(current_register_value[0],
                                                selected_bit)
        # print(">>> "+str(selected_register) + " ... "+ \
        #   str(current_register_value[0])+" ... "+str(new_register_value))
        self.i2c_bus.write_i2c_block_data(self.i2c_address, selected_register,
                                          [new_register_value])

    def __clear_a_register_bit(self, selected_register, selected_bit):
        """ set a bit in a register """
        # bits are offsets 0-7
        current_register_value = self.i2c_bus.read_i2c_block_data(
            self.i2c_address, selected_register, 1)
        new_register_value = BitUtils.clear_a_bit(current_register_value[0],
                                                  selected_bit)
        # print(">>> "+str(selected_register) + " ... "+ \
        #   str(current_register_value[0])+" ... "+str(new_register_value))
        self.i2c_bus.write_i2c_block_data(self.i2c_address, selected_register,
                                          [new_register_value])

    def __isset_a_register_bit(self, selected_register, selected_bit):
        """ set a bit in a register """
        # bits are offsets 0-7
        current_register_value = self.i2c_bus.read_i2c_block_data(
            self.i2c_address, selected_register, 1)
        return BitUtils.is_bit_set(current_register_value[0], selected_bit)

    def __test_for_changes(self, changed_pins, pin_base, changed_gpio,
                           gpio_reg):
        """ if pin changed, append new value to changed_pin list """
        return_pins = changed_pins
        if changed_gpio != 0x00:
            for p in range(0, 8):
                pin = p + pin_base
                pin_changed = BitUtils.is_bit_set(changed_gpio, p)
                if pin_changed:
                    new_pin_value = BitUtils.is_bit_set(gpio_reg, p)
                    return_pins.append((pin, new_pin_value))
        return return_pins
