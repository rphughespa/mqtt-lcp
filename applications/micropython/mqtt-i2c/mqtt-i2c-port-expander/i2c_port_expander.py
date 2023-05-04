
# # ic2_port_expander.py
"""



    I2cPortExpander.py - helper class to process i2c mcp23017 port expander devices
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


import sys
import time
import gc
import micropython

sys.path.append('./lib')

from global_constants import Global
from global_synonyms import Synonyms

from io_data import IoData

from io_device_data import IoDeviceData
from port_expander_base import PortExpanderBase

import mcp23017



#mcp.pin(3, mode=0) # set pin as output
#mcp.pin(1, mode=1, polarity=1) # swet pin as input
# mcp = mcp23017.MCP23017(i2c_bus, 39)

class I2cPortExpander(PortExpanderBase):
    """ Class for an I2C connected port expander device"""

    def __init__(self, i2c_bus=None, io_device=None, node_name=None, pub_topics=None, logger=None):
        """ Initialize """
        super().__init__(io_device=io_device, node_name=node_name, pub_topics=pub_topics,logger=logger)
        self.name="port expander_relay"
        self.logger = logger
        self.i2c_address = self.io_device.io_address
        self.i2c_bus = i2c_bus
        self.mcp = mcp23017.MCP23017(self.i2c_bus, self.i2c_address)
        self.pin_active_low = {}
        self.pin_last_values = {}
        self.has_inputs = False


    def read_input(self):
        """ Read input from port_expander device"""

        changed_pins = self.__read_input_pins()
        if len(changed_pins) < 1:
            changed_pins = None
        return changed_pins

    def initialize(self):
        """ initialize class """
        print("Initialize Port Expander")
        print("i2c: "+str(self.i2c_bus.scan()))
        self.initialize_device()
        super().initialize()

    def init_input_pin(self, selected_pin, active_low=True):
        """ set a pin into input_mode """
        # pins must be 0-15

        if selected_pin < 0 or selected_pin > 15:
            self.logger.log_error("Port expander pins must be 0-15: {" +
                           str(selected_pin) + "}")
        self.has_inputs = True
        self.pin_active_low[selected_pin] = active_low
        #print(">>> input pin: "+str(selected_pin))
        self.mcp.pin(selected_pin, mode=1, pullup=1)
        self.pin_last_values[selected_pin] = self.mcp.pin(selected_pin)
        #print(">>> last values:" +str(self.pin_last_values))

    def set_output_pin(self, selected_pin, pin_on=False, pulse=0):
        """ set a output pin on or off """
        #print(">>> set output pin: "+str(selected_pin))

        # self.pin_active_low[selected_pin] = active_low
        pin_mode = pin_on
        if self.pin_active_low[selected_pin]:
            pin_mode = not pin_mode
        self.mcp.pin(selected_pin, value=pin_mode)
        if pulse != 0:
            time.sleep(pulse / 1000)
            pin_mode = not pin_mode
            self.mcp.pin(selected_pin, value=pin_mode)

    def init_output_pin(self, selected_pin, active_low=True):
        """ set a pin into output_mode """
        #print(">>> init output: "+str(selected_pin))
        if selected_pin < 0 or selected_pin > 15:
            self.logger.log_error("Port expander pins must be 0-15: {" +
                           str(selected_pin) + "}")
        self.pin_active_low[selected_pin] = active_low
        pin_mode = False
        if active_low:
            # turn on pin as init value
            pin_mode = not pin_mode
        self.mcp.pin(selected_pin, mode=0, value=pin_mode)

    def send_pin_changes(self, selected_pins):
        """ send pin changes to the device """
        # some pins groups may have mutually exclusive pins
        # set the "off" pins first
        for (set_pin, set_mode, set_pulse) in selected_pins:
            if set_mode in [0, False, Global.OFF]:
                #print(">>> "+str(set_pin)+" ... "+str(set_mode))
                self.set_output_pin(set_pin, False, set_pulse)
        # set the "on" pins next
        for (set_pin, set_mode, set_pulse) in selected_pins:
            if set_mode in [1, True, Global.ON]:
                #print(">>> "+str(set_pin)+" ... "+str(set_mode))
                self.set_output_pin(set_pin, True, set_pulse)

    def initialize_device(self):
        """ initialize the device """
        self.clear_all_pins()


    def clear_all_pins(self):
        """ turn off all relays """
        for p in range(0, 16):
            self.pin_active_low[p] = True


#
#   private functions
#

    def __read_input_pins(self):
        """ read input pin values """
        changed_pins = []
        for selected_pin, last_value in self.pin_last_values.items():
            #print(">>> read: "+str(selected_pin)+" ... "+str(last_value))
            pin_mode = self.mcp.pin(selected_pin)
            #print(">>> ... "+str(pin_mode))
            if self.pin_active_low[selected_pin]:
                pin_mode = not pin_mode
                if pin_mode != last_value:
                    # print(">>> pin changed: "+str(selected_pin)+" ... "+str(pin_mode))
                    self.pin_last_values.update({selected_pin: pin_mode})
                    state = Global.OFF
                    if pin_mode:
                        state = Global.ON
                    changed_pins.append((selected_pin, state))
        return changed_pins
