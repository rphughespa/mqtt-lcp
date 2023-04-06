#!/usr/bin/python3
# # rp2040_port_expander.py
"""



    Rp2040PortExpander.py - helper class to process i2c mcp23017 port expander devices
            This class contains the hardware specific funtionality to turn pins on/off.
            The base class, I2cPortExpanderBase, contains the business logic
            which determines which pins to turn/off for a given request.
            Defaults to active low.



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

import micropython, sys, time, gc
from machine import Pin, PWM

from global_constants import Global
from global_synonyms import Synonyms

from io_data import IoData

from io_device_data import IoDeviceData

from port_expander_base import PortExpanderBase


PIN_TYPE_INPUT = "input"
PIN_TYPE_OUTPUT = "output"
PIN_TYPE_PWM = "pwm"

class GpIoPin():
    """ class for definition of a gpio pin """
    def __init__(self, pin_number, pin_type=PIN_TYPE_OUTPUT, pin_value=0):
        self.pin_number = pin_number
        self.pin_type = pin_type
        self.pin_value = pin_value
        self.gpio_pin = None

        if pin_number not in range(16):
            print("GpIoPin: Error, Pin number not 0-15: "+str(pin_number))
        else:
            if pin_type not in [PIN_TYPE_INPUT, PIN_TYPE_OUTPUT, PIN_TYPE_PWM]:
                print("GpIoPin: Error, Invalid pin type: " +str(pin_type))
            else:
                if self.pin_type == PIN_TYPE_INPUT:
                    # input
                    self.gpio_pin = Pin(self.pin_number, Pin.IN, Pin.PULL_UP)
                    self.gpio_pin.value(self.pin_value)
                elif self.pin_type == PIN_TYPE_PWM:
                    # pwm
                    self.gpio_pin = PWM(Pin(self.pin_number))
                    self.gpio_pin.freq(1000)
                    self.gpio_pin.duty_cycle_u16(0)
                else:
                    # output
                    self.gpio_pin = Pin(self.pin_number, Pin.OUT)
                    self.gpio_pin.value(self.pin_value)

    def set_pin_value(self, new_pin_value):
        """ set the value of a pin """
        # print(">>> pin set: "+str(self.pin_number) + " : "+str(new_pin_value))
        if self.pin_type in [PIN_TYPE_INPUT, PIN_TYPE_OUTPUT]:
            if new_pin_value in [0, False, Global.OFF]:
                self.gpio_pin.value(1)
                self.pin_value = new_pin_value
            elif new_pin_value in [1, True, Global.ON]:
                self.gpio_pin.value(0)
                self.pin_value = new_pin_value
            else:
                print("GpIoPin: Error, Invalid pin value: " +str(new_pin_value))
        else:
            # pwm
            if new_pin_value not in range(256):
                print("GpIoPin: Error, Invalid pwm value, not 0-255: Pin:" + \
                      str(self.pin_number)+", Value: "+str(new_pin_value))
            else:
                # convert 0-255 to 0-65535
                new_value = int((new_pin_value / 255) * 65535)
                self.gpio_pin.set_duty_cycle(new_value)
                self.pin_value = new_pin_value

class Rp2040PortExpander(PortExpanderBase):
    """ Class for an I2C connected port expander device"""

    def __init__(self, i2c_bus=None, io_device=None, node_name=None, pub_topics=None, logger=None):
        """ Initialize """
        super().__init__(io_device=io_device, node_name=node_name, pub_topics=pub_topics,logger=logger)
        self.name="port expander_relay"
        self.logger = logger
        self.has_inputs = False
        self.pins = []

    def read_input(self):
        """ Read input from port_expander device"""

        changed_pins = self.__read_input_pins()
        if len(changed_pins) < 1:
           changed_pins = None
        return changed_pins

    def send_pin_changes(self, selected_pins):
        """ send pin changes to the device """
        # some pins groups may have mutually exclusive pins
        # set the "off" pins first
        # print(">>> set pins: "+str(selected_pins))
        for (set_pin, set_mode, set_pulse) in selected_pins:
            if set_mode in [0, False, Global.OFF]:
                #print(">>> "+str(set_pin)+" ... "+str(set_mode))
                self.set_output_pin(set_pin, False, set_pulse)
        # set the "on" pins next
        for (set_pin, set_mode, set_pulse) in selected_pins:
            if set_mode in [1, True, Global.ON]:
                #print(">>> "+str(set_pin)+" ... "+str(set_mode))
                self.set_output_pin(set_pin, True, set_pulse)

    def initialize(self):
        """ initialize class """
        print("Initialize Port Expander")
        self.initialize_device()
        super().initialize()


    def initialize_device(self):
        """ initialize the device """
        for p in range(16):
            self.pins.append(None)
        self.clear_all_pins()
        #print(">>> pins: "+str(self.pins))

    def init_input_pin(self, selected_pin, active_low=True):
        """ set a pin into input_mode """
        # pins must be 0-15
        if selected_pin not in range(16):
            self.log_error("RP2040: Port GPIO pins must be 0-15: {" +
                           str(selected_pin) + "}")
        else:
            self.has_inputs = True
            pin = GpIoPin(selected_pin, PIN_TYPE_INPUT)
            pin.set_pin_value(Global.OFF)
            self.pins[selected_pin] = pin

    def init_output_pin(self, selected_pin, active_low=True):
        """ set a pin into output_mode """
        #print(">>> pins len: "+str(len(self.pins)))
        if selected_pin not in range(16):
            self.log_error("RP2040: Port GPIO pins must be 0-15: {" +
                           str(selected_pin) + "}")
        else:
            pin = GpIoPin(selected_pin, PIN_TYPE_OUTPUT)
            pin.set_pin_value(Global.OFF)
            self.pins[selected_pin] = pin

    def set_output_pin(self, selected_pin, pin_value=False, pulse=0):
        """ set a output pin on or off """
        if selected_pin not in range(16):
            self.log_error("RP2040: Port GPIO pins must be 0-15: {" +
                           str(selected_pin) + "}")
        else:
            if self.pins[selected_pin] is not None:
                if self.pins[selected_pin].pin_type != PIN_TYPE_INPUT:
                    self.pins[selected_pin].set_pin_value(pin_value)
                    if pulse != 0:
                        time.sleep(pulse / 1000)
                        self.pins[selected_pin].set_pin_value(Global.OFF)

    def clear_all_pins(self):
        """ turn off all pins """
        for pin in self.pins:
            if pin is not None:
                if pin.pin_type != PIN_TYPE_INPUT:
                    self.pins[pin.set_pin_value(Global.OFF)]

#
#   private functions
#

    def __read_input_pins(self):
        """ read input pin values """
        changed_pins = []
        for pin in self.pins:
            if pin is not None:
                if pin.pin_type == PIN_TYPE_INPUT:
                    new_value = pin.gpio_pin.value()
                    if new_value != pin.pin_value:
                        pin.pin_value = new_value
                        state = Global.OFF
                        if new_value == 0:
                            # active low
                            state = Global.ON
                        changed_pins.append((pin.pin_number, state))
        return changed_pins
