# ic2rotary

"""

i2c_rotary.py - helper class to process i2c rotary switch devices.
        Rotary value range from 0-128.
        Color of knob is changed from green to red depending on knob value.

    supports SparkFun Qwiic Twist - RGB Rotary Encoder Breakout

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
if sys.platform.startswith("esp32_LoBo"):
    from smbus2_go_lobo import SMBus
elif sys.platform.startswith("esp32"):
    from smbus2_esp32 import SMBus
else:
    from smbus2 import SMBus

from i2c_io_data import I2cIoData
from i2c_device import I2cDevice
from sparkfun_qwiictwist_smbus import Sparkfun_QwiicTwist

from global_constants import Global

class I2cRotary(I2cDevice):
    """ Class for an I2C connected Rotary device"""

    def __init__(self, log_queue, input_queue, i2c_address, mqtt_port=None, mqtt_type=None, itype="rotary", i2c_bus_number=1,
                 i2c_mux=None, i2c_sub_address=None):
        """ Initialize """
        super().__init__(log_queue, i2c_address, input_queue=input_queue,
                         i2c_device_type=itype, i2c_bus_number=i2c_bus_number,
                         i2c_mux=i2c_mux, i2c_sub_address=i2c_sub_address)
        self.mode = "input"
        self.mqtt_port = mqtt_port
        self.mqtt_type = mqtt_type
        self.twist = Sparkfun_QwiicTwist(i2c_bus_number)
        self.last_value = 0
        self.init_device()

    def init_device(self):
        # self.log_queue.add_message("debug", 'Read rotary from: ' + str(self.i2c_address))
        if self.i2c_mux is not None:
            self.i2c_mux.enable_mux_port(self.i2c_sub_address)
        self.twist.count = 0
        self.twist.connect_color(0, 0, 0)
        self.set_twist_color(self.twist, 0)
        if self.i2c_mux is not None:
            self.i2c_mux.disable_mux_port(self.i2c_sub_address)


    def read_input(self):
        """ Read input from Rotary device"""
        # self.log_queue.add_message("debug", 'Read rotary from: ' + str(self.i2c_address))
        if self.i2c_mux is not None:
            self.i2c_mux.enable_mux_port(self.i2c_sub_address)
        value, pressed = self.read_i2c_rotary_value()
        if value is not None and value != self.last_value:
            return_data = I2cIoData()
            return_data.i2c_type = "rotary"
            return_data.device_type = "rotary"
            return_data.mqtt_port = self.mqtt_port
            return_data.mqtt_type = self.mqtt_type
            return_data.reported = value
            self.log_queue.add_message("debug", 'Received from rotary [' + str(return_data.reported) + ']')
            self.input_queue.put(return_data)
            self.last_value = value
        if pressed:
            return_data = I2cIoData()
            return_data.i2c_type = "rotary"
            return_data.device_type = "rotary"
            return_data.port = self.mqtt_port
            return_data.type = self.mqtt_type
            return_data.reported = Global.PRESS
            self.log_queue.add_message("debug", 'Received from rotary ['
                    + str(return_data.reported) + ']')
            self.input_queue.put(return_data)
        if self.i2c_mux is not None:
            self.i2c_mux.disable_mux_port(self.i2c_sub_address)

    def read_i2c_rotary_value(self):
        """ Read a value"""
        pressed = False
        count = self.twist.count
        if count < 0:
            self.twist.count = 0
            count = 0
        elif count > 128:
            self.set_twist_color(self.twist, count)  # fix bug where knob color change above 128
            self.twist.count = 128
            count = 128
        if count != self.last_value:
            self.set_twist_color(self.twist, count)
        if self.twist.pressed:
            pressed = True
            self.log_queue.add_message("debug", "Read i2c: "+str(self.i2c_address)+" .. pressed ..")
        return count, pressed

    def gradulated_color(self, percent, start, end):
        if start == end:
            color = end
        else:
            color = int(((end - start) * percent)+ start)
            # print("P: "+str(percent)+", S: "+str(start)+", E: "+str(end)+", C: "+str(color))
            if end > start:
                if color < start:
                    color = start
                elif color > end:
                    color = end
            else:
                if color > start:
                    color = start
                elif color < end:
                    color = end
        return color


    def graduated_rgb(self, value, steps,
                    begin_red, begin_green, begin_blue,
                    end_red, end_green, end_blue):
        """ Graduated RGB colors """
        percent = value / steps
        red = self.gradulated_color(percent, begin_red, end_red)
        green = self.gradulated_color(percent, begin_green, end_green)
        blue = self.gradulated_color(percent, begin_blue, end_blue)
        return red, green, blue

    def set_twist_color(self, _twist, value):
        """ Set color of knob based on knob value """
        # assume value go from 0 to 255
        # full green at 48
        # full yellow at 88
        # full red at 128
        # in between, a blend
        if value < 1:
            # turn color off
            self.twist.set_color(0, 0, 0)
        elif value > 127:
            # full red
            self.twist.set_color(255, 0, 0)
        elif value == 2:
            # full green
            self.twist.set_color(0, 255, 0)
        elif value == 64:
            # full yellow
            self.twist.set_color(255, 255, 0)
        else:
            if value < 64:
                # 2 to 63
                # print("light green")
                red, green, blue = self.graduated_rgb(value-1, 62,
                        0, 255, 0,
                        255, 255, 0)
                # print("R: "+str(red)+", G: "+str(green)+", B: "+str(blue))
                self.twist.set_color(red, green, blue)
            else:
                # 65 to 127
                red, green, blue = self.graduated_rgb(value-85, 61,
                        255, 255, 0,
                        255, 0, 0)
                # print("R: "+str(red)+", G: "+str(green)+", B: "+str(blue))
                self.twist.set_color(red, green, blue)
