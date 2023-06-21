#!/usr/bin/python3
# ic2_servo_pca9685.py
"""

I2cServoPca9685 - driver for a i2c server controller board
    exampes: Examples are Spartkfun Servo PHat amd Zio 16 Servo Controller

    Note: much of the logic is this module is borowwed from code posted in GitHub:
        https://github.com/jimfm/servo_driver
    Therefore use of this code is subject to any restrictions specified by the orignal author

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

import time
import sys
import math

sys.path.append('../../../lib')

# from utils.bit_utils import BitUtils

# from global_constants import Global

from i2c.devices.i2c_base_device import I2cBaseDevice



class I2cServoPca9685(I2cBaseDevice):
    """ Class for an I2C connected servo controller device"""
    # Registers/etc.
    __FREQ               = 50
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __MODE1              = 0x00
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD

    def __init__(self, i2c_address=None, i2c_bus=None, log_queue=None,
            pulse_min=400, pulse_max=1700):
        """ Initialize """
        super().__init__(name="i2c_servo",
                         i2c_address=i2c_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)
        self.__initialize_device()
        self.pulse_min = pulse_min
        self.pulse_max = pulse_max

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def initialize_channel(self, _channel):
        """ initialize a channel """
        pass

    def move_servo(self, channel, desired_position):
        """  Move servo a desired position within a range """
        # normally servo has a range of 0-90 degrees
        select_channel = 0
        if 0 <= channel <= 15:
            select_channel = channel
        self.__setServoPulse(select_channel, desired_position)

    #
    # private functions
    #

    def __initialize_device(self):
        """ initialize the device """
        self.__setPWMFreq(self.__FREQ)
        self.__write(self.__MODE1, 0x00)

    def __write(self, reg, value):
        """ Writes an 8-bit value to the specified register/address """
        self.i2c_bus.write_byte_data(self.i2c_address, reg, value)
        #self.log_debug("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
        self.log_debug("I2C: Write 0x{value:02X} to register 0x{reg:02X}")

    def __read(self, reg):
        """ Read an unsigned byte from the I2C device """
        result = self.i2c_bus.read_byte_data(self.i2c_address, reg)
        # self.log_debug("I2C: Device 0x%02X returned 0x%02X "+\
        #       "from reg 0x%02X" % (self.i2c_address, result & 0xFF, reg))
        self.log_debug("I2C: Device 0x{self.i2c_address:02X} "+\
                       " returned 0x{result & 0xFF02X} from reg 0x{reg:02X}")
        return result

    def __setPWMFreq(self, freq):
        """ Sets the PWM frequency """
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        self.log_debug("Setting PWM frequency to {freq:d} Hz")
        self.log_debug("Estimated pre-scale: {prescaleval:d}")
        prescale = math.floor(prescaleval + 0.5)
        self.log_debug("Final pre-scale: {prescale:d}")

        oldmode = self.__read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.__write(self.__MODE1, newmode)        # go to sleep
        self.__write(self.__PRESCALE, int(math.floor(prescale)))
        self.__write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.__write(self.__MODE1, oldmode | 0x80)

    def __setPWM(self, channel, on, off):
        """ Sets a single PWM channel """
        self.__write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.__write(self.__LED0_ON_H+4*channel, on >> 8)
        self.__write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.__write(self.__LED0_OFF_H+4*channel, off >> 8)
        self.log_debug("channel: {:channel}  LED_ON: {on:d} LED_OFF: {off:d}")

    def __setServoPulse(self, channel, degrees):
        """Sets the Servo Pulse """
        # The PWM frequency must be 50HZ
        # Degrees must be 0-90
        pulse = self.__convert_degrees_to_pulse(degrees)
        self.log_debug(" ... pulse: " + str(degrees)+ " >>> " + str(pulse))
        pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us
        self.__setPWM(channel, 0, int(pulse))

    def __convert_degrees_to_pulse(self, req_degrees):
        """ convert degrees (0-90) to pulse (min-max) """
        req = int(req_degrees)
        # imit travel to 10-90
        req = max(req, 10)
        req = min(req, 90)
        pulse = int(((req/90) * \
            (self.pulse_max - self.pulse_min)) + self.pulse_min)
        return pulse
