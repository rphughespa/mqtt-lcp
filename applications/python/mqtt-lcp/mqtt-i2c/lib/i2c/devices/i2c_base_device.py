#!/usr/bin/python3
# ic2_base_device.py
"""

I2cBaseDevice - contain soem common helper functions for I2C device devices


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

# import time

from utils.global_constants import Global


class I2cBaseDevice(object):
    """ Base Class for an I2C device drivers """
    def __init__(self,
                 name=None,
                 i2c_address=None,
                 i2c_bus=None,
                 log_queue=None):
        """ Initialize """
        self.name = name
        self.log_queue = log_queue
        self.i2c_address = i2c_address
        self.i2c_bus = i2c_bus
        if i2c_bus is None:
            self.log_error("I2C Bus not open: ")
        if not isinstance(self.i2c_address, int):
            self.log_error("I2C Address not integer: " + str(self.i2c_address))

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def read_input(self):
        """ read input """
        # nothing read
        return []

    def request_device_action(self, _message):
        """ send output to the i2c device """
        # (reported, message, data reported, send after)
        return (None, None, None, None)

    def perform_other(self):
        """ perform periodic operations """
        pass

    def log_debug(self, message=None):
        """ log a debug message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_DEBUG, self.name + ": " + message))

    def log_info(self, message=None):
        """ log an info message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_INFO, self.name + ": " + message))

    def log_warning(self, message=None):
        """ log an warn message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_WARNING, self.name + ": " + message))

    def log_error(self, message=None):
        """ log an error message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_ERROR, self.name + ": " + message))

    def log_critical(self, message=None):
        """ log an critical message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_CRITICAL, self.name + ": " + message))
