#i2c_mux.py

"""

    I2CMux - helper class to process i2c devices connected to a mux

    Supports SparkFun Qwiic Mux Breakout - 8 Channel (TCA9548A)

    Adapted from SparkFun Arduino Code

The MIT License (MIT)

Copyright © 2020 richard p hughes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the “Software”), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import sys
# platforms for esp32 = esp32, for lobo esp32 = esp32_LoBo, for pi = linux
if sys.platform.startswith("esp32_LoBo"):
    from smbus2_go_lobo import SMBus
elif sys.platform.startswith("esp32"):
    from smbus2_esp32 import SMBus
else:
    from smbus2 import SMBus

from i2c_device import I2cDevice

class I2cMux(I2cDevice):
    """ Class to define and manipulate a mux device on an I2C bus"""

    def __init__(self, log_queue, i2c_address, mux_type=None, i2c_bus_number=1):
        """ Initialize """
        super().__init__(log_queue, i2c_address,
                         i2c_device_type="mux", i2c_bus_number=i2c_bus_number, mux_type=mux_type)

    def set_bit(self, int_type, offset):
        """ Set a bit in an integer"""
        mask = 1 << offset
        return int_type | mask

    def clear_bit(self, int_type, offset):
        """ Clear a bit in an integer"""
        mask = ~(1 << offset)
        return int_type & mask

    def enable_mux_port(self, port_number):
        """ Enable a mux port, exposes device on that port to the I2C bus. """
        self.log_queue.add_message("debug",
                "Enable Mux Port: "+str(self.i2c_bus_number)+" ..."+str(self.i2c_address)+" ... "+str(port_number))
        if port_number > 7:
            port_number = 7

        # Read the current mux settings
        try:
            with SMBus(self.i2c_bus_number) as bus:
                if sys.platform.startswith("esp32"):
                    # binn = bus.readfrom(self.i2c_address, 0)
                    binn = bus.readfrom(self.i2c_address, 1)
                    settings = int(binn[0])
                else:
                    binn = bus.read_byte_data(self.i2c_address, 0)
                    settings = int(binn)
                #print("enable mux read: "+str(settings))
                new_settings = self.set_bit(settings, port_number)
                #print("enable mux write: "+str(new_settings))
                # print(" ... enable: "+str(hex(settings))+".."+str(hex(new_settings)))
                if sys.platform.startswith("esp32"):
                    new_byte = bytes([new_settings])
                    #print("... enable mux write bytes: "+str(new_byte))
                    # bus.writeto_mem(self.i2c_address, 0, new_byte)
                    bus.writeto(self.i2c_address, new_byte)
                else:
                    bus.write_byte_data(self.i2c_address, 0, new_settings)
        except Exception as exc:
            self.log_queue.add_message("error", "Exception during mux port enable: " + str(exc))

    def disable_mux_port(self, port_number):
        """ Disable a mux port"""
        self.log_queue.add_message("debug",
                "Disable Mux Port: "+str(self.i2c_bus_number)+" ..."+str(self.i2c_address)+" ... "+str(port_number))
        if port_number > 7:
            port_number = 7
        # Read the current mux settings
        try:
            with SMBus(self.i2c_bus_number) as bus:
                if sys.platform.startswith("esp32"):
                    # binn = bus.readfrom(self.i2c_address, 0)
                    binn = bus.readfrom(self.i2c_address, 1)
                    settings = int(binn[0])
                else:
                    binn = bus.read_byte_data(self.i2c_address, 0)
                    settings = int(binn)
                # print("disable mux read: "+str(settings))
                new_settings = self.clear_bit(settings, port_number)
                #print("disable mux write: "+str(new_settings))
                # print("disable: "+str(hex(settings))+".."+str(hex(new_settings)))
                if sys.platform.startswith("esp32"):
                    new_byte = bytes([new_settings])
                    #print("... disable mux write bytes: "+str(new_byte))
                    # bus.writeto_mem(self.i2c_address, 0, new_byte)
                    bus.writeto(self.i2c_address, new_byte)
                else:
                    bus.write_byte_data(self.i2c_address, 0, new_settings)
        except Exception as exc:
            self.log_queue.add_message("error", "Exception during mux port disable: "+str(exc))
