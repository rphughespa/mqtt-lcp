# i2c_servo.py

"""

i2c_servo_hat.py - helper class to process i2c connected servo devices

    Supports the SparkFun pi hat servo board, Some code in this module has been copied from
    the SparkFun python modules:

        PiServoHat.py, Qwiic_PCA9685_Py

    Please check theses modules for SparkFun code license.

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
if sys.platform.startswith("esp32"):
    from queue_esp32 import Queue
else:
    from queue_py import Queue

class I2cServo():
    """ Class for an I2C connected servo device"""

    def __init__(self, i2c_io_data, center_degrees=None, throw_degrees=None, close_degrees=None):
        """ initialize """
        self.i2c_io_data = i2c_io_data
        self.center_degrees = center_degrees
        self.throw_degrees = throw_degrees
        self.close_degrees = close_degrees
        self.desired_degrees = None
        self.current_degrees = None
        self.move_degrees = None
        self.max_moves = None

    def read_input(self):
        """ Read input from servo device"""
        pass

    def write_output(self, message):
        """ process servo movement message """
        pass
