#!/usr/bin/python3
# # ic2_encoder_pel12t.py
"""

iI2cEncoderPel12t - low level hardware driver fot a rotary encoder connected to i2c using the pel12t circuit device

The knob can be rotated continuosly clockwise or counter clockwise with 24 clicks (detents) in a 360 degree rotation.
THe knob can also be pressed to generate a "click" of "button pressed" event.
Lastly, the shaft of the knob has a RGB led below it that can add color to the shaft.

Sold by Sparkfun as their Qwiic Twist - RGB Rotary Encoder Breakout


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

sys.path.append('../../../libs')

import math

# from smbus2 import SMBus

# from global_constants import Global
from i2c.devices.i2c_base_device import I2cBaseDevice

_BUTTON_CLICKED = 0x04
_BUTTON_PRESSED = 0x02
_MAX_DIFFERENCE_COUNTER_VALUE = 32
_MAX_POSITIVE_COUNTER_DIFF_VALUE = 127
_REG_STATUS = 0x01
_REG_DIFFERENCE_LSB = 0x07
_REG_LED_BRIGHT_RED = 0x0D
_REG_LED_BRIGHT_GREEN = 0x0E
_REG_LED_BRIGHT_BLUE = 0x0F
_REG_LED_CONNECT_RED_LSB = 0x10
_REG_LED_CONNECT_RED_MSB = 0x11
_REG_LED_CONNECT_GREEN_LSB = 0x12
_REG_LED_CONNECT_GREEN_MSB = 0x13
_REG_LED_CONNECT_BLUE_LSB = 0x14
_REG_LED_CONNECT_BLUE_MSB = 0x15


class I2cEncoderPel12t(I2cBaseDevice):
    """ Class for an I2C connected encoder device"""
    def __init__(self, i2c_address=None, i2c_bus=None, log_queue=None):
        """ Initialize """
        super().__init__(name="i2c_encoder_pel12t",
                         i2c_address=i2c_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)
        self.__initialize_device()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def read_input(self):
        """ Read input from encoder device"""
        (counter, clicked) = self.__read_from_device()
        return (counter, clicked)

    def __initialize_device(self):
        """ initialize the device """
        # read and ignore response to reset counters
        # print(">>> init encoder")
        self.__read_from_device()
        # turn off auto color change when knob is rotated
        self.__set_connect_color(0, 0, 0)
        # turn off red, green, blue color
        self.set_encoder_color(0, 0, 0)

    def __read_from_device(self):
        """ read movement and button """
        self.log_debug("Read from Encoder: " + str(self.i2c_address))
        return_counter_difference = None
        return_clicked = None
        counter_difference = self.__read_encoder_counter_difference_and_reset(
            self.i2c_bus)
        (clicked,
         _pressed) = self.__read_encoder_button_and_reset(self.i2c_bus)
        if counter_difference != 0:
            return_counter_difference = counter_difference
        if clicked:
            return_clicked = clicked
        # ignoring "pressed", don't need it because a "click" will be recorded when button released
        return (return_counter_difference, return_clicked)

    def __read_encoder_counter_difference_and_reset(self, bus):
        # only deal with counter lsb, ignore msb
        diff = 0
        try:
            diff = bus.read_i2c_block_data(self.i2c_address,
                                           _REG_DIFFERENCE_LSB, 1)
            # zero out lsb and msb bytes
            bus.write_i2c_block_data(self.i2c_address, _REG_DIFFERENCE_LSB,
                                     [0x00, 0x00])
        except Exception as exc:
            if "[Errno 121]" not in str(exc):
                self.log_debug("Exception during encode read io: " +
                               str(self.i2c_address) + ", " + str(exc))
        # check to see if went reverse
        diff_counter = 0
        if isinstance(diff, list):
            diff_counter = diff[0]
        # check to see if went reverse
        if abs(diff_counter) > _MAX_POSITIVE_COUNTER_DIFF_VALUE:
            # convert ccw rotation past zero into negative numbers
            diff_counter = diff_counter - 256
        if abs(diff_counter) > _MAX_DIFFERENCE_COUNTER_VALUE:
            # ignore spurious read on hardware
            diff_counter = 0
        return diff_counter

    def __read_encoder_button_and_reset(self, bus):
        """ check to see if encoder button has been clicked """
        # get button values
        button_value = 0
        button_int = 0
        try:
            button_value = bus.read_i2c_block_data(self.i2c_address,
                                                   _REG_STATUS, 1)
            # reset button values
            bus.write_i2c_block_data(self.i2c_address, _REG_STATUS,
                                     [0x00, 0x00])
        except Exception as exc:
            if "[Errno 121]" not in str(exc):
                self.log_debug("Exception during encode read io: " +
                               str(self.i2c_address) + ", " + str(exc))
        # print(">>> "+str(button_value))
        if isinstance(button_value, list):
            button_int = button_value[0]
        #else:
        #print(">>> button value type: " + str(type(button_value)))
        #print(">>> button value: " + str(button_value))

        button_clicked = False
        if (button_int & _BUTTON_CLICKED) != 0:
            button_clicked = True
        button_pressed = False
        if (button_int & _BUTTON_PRESSED) != 0:
            button_pressed = True
        return (button_clicked, button_pressed)

    def set_encoder_green_thru_red_color(self, value):
        """ set encode color on a range from green (1) to red(100) """
        # Set color of encoder based on encoder value
        # assumes value go from 0 to 100
        # off at 0
        # full green at 1
        # full yellow at 50
        # full red at 100
        # in between, a blend

        rgb_colors = (0, 0, 0)
        if value == 0:
            rgb_colors = (0, 0, 0)
        elif value == 1:
            # full green
            rgb_colors = (0, 255, 0)
        elif value > 99:
            # fill red
            rgb_colors = (255, 0, 0)
        elif value == 50:
            # full yellow
            rgb_colors = (255, 255, 0)
        else:
            # calc the color blend
            if value < 50:
                # 1 to 49
                rgb_colors = self.__graduated_rgb(value, 49, 0, 255, 0, 255,
                                                  255, 0)
            else:
                # 51 to 100
                rgb_colors = self.__graduated_rgb(value - 50, 48, 255, 255, 0,
                                                  255, 0, 0)
        (red_value, green_value, blue_value) = rgb_colors
        self.set_encoder_color(red_value, green_value, blue_value)

    def set_encoder_color(self, red_value, green_value, blue_value):
        """
            set the color of the encoder by setting red, green, blue brightnesses
            values are 0-255. 0 turns off the color
        """
        # print(">>> set color: " + str(red_value)+" ... " +
        #      str(green_value)+" ... "+str(blue_value))
        try:
            if 0 <= red_value <= 255:
                self.i2c_bus.write_i2c_block_data(self.i2c_address,
                                                  _REG_LED_BRIGHT_RED,
                                                  [red_value])

            if 0 <= green_value <= 255:
                self.i2c_bus.write_i2c_block_data(self.i2c_address,
                                                  _REG_LED_BRIGHT_GREEN,
                                                  [green_value])

            if 0 <= blue_value <= 255:
                self.i2c_bus.write_i2c_block_data(self.i2c_address,
                                                  _REG_LED_BRIGHT_BLUE,
                                                  [blue_value])
        except Exception as exc:
            if "[Errno 121]" not in str(exc):
                self.log_debug("Exception during encoder read: " +
                               str(self.i2c_address) + ", " + str(exc))

    def __set_connect_color(self, red_value, green_value, blue_value):
        """
            set the connect color of the encoder by setting red, green, blue brightnesses
            values are 0-255. 0 turns off the color. The connect colors are the amount the color
            changes automatically on each detent of the encoder rotation.
        """

        # print(">>> init color: " + str(red_value)+" ... " +
        #      str(green_value)+" ... "+str(blue_value))
        try:
            if 0 <= red_value <= 255:
                self.i2c_bus.write_i2c_block_data(self.i2c_address,
                                                  _REG_LED_CONNECT_RED_LSB,
                                                  [red_value, 0x00])
            if 0 <= green_value <= 255:
                self.i2c_bus.write_i2c_block_data(self.i2c_address,
                                                  _REG_LED_CONNECT_GREEN_LSB,
                                                  [green_value], 0x00)
            if 0 <= blue_value <= 255:
                self.i2c_bus.write_i2c_block_data(self.i2c_address,
                                                  _REG_LED_CONNECT_BLUE_LSB,
                                                  [blue_value, 0x00])
        except Exception as exc:
            if "[Errno 121]" not in str(exc):
                self.log_debug("Exception during color connect: " +
                               str(self.i2c_address) + ", " + str(exc))

    def __graduated_rgb(self, value, steps, begin_red, begin_green, begin_blue,
                        end_red, end_green, end_blue):
        # calulate rgb color values based on a sliding scale between a start brightness and an ending brightness
        # Graduated RGB colors
        percent = value / steps
        red_value = self.__gradulated_color(percent, begin_red, end_red)
        green_value = self.__gradulated_color(percent, begin_green, end_green)
        blue_value = self.__gradulated_color(percent, begin_blue, end_blue)
        return (red_value, green_value, blue_value)

    def __gradulated_color(self, percent, start, endd):
        # calc a gradualted color between start. endd)
        color = start
        if percent < 0.01:
            color = start
        elif percent > 1.00:
            color = endd
        else:
            color_part = math.trunc((endd - start) * percent) + start
            color = start
            if endd > start:
                if color_part < start:
                    color = start
                elif color_part > endd:
                    color = endd
                else:
                    color = color_part
            else:
                if color_part > start:
                    color = start
                elif color_part < endd:
                    color = endd
                else:
                    color = color_part
        return color
