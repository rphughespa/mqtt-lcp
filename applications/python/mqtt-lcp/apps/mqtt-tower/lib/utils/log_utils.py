#!/usr/bin/python3
# log_utils.py
"""


   LogUtils.py - utility logging functionx

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

sys.path.append('../../lib')

from utils.global_constants import Global


class LogUtils(object):
    """ help class for logging operations """
    def __init__(self, log_name="log", log_queue=None):
        self.log_queue = log_queue
        self.log_name = log_name

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def log_debug(self, message=None):
        """ log a debug message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_DEBUG, self.log_name + ": " + message))

    def log_info(self, message=None):
        """ log an info message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_INFO, self.log_name + ": " + message))

    def log_warning(self, message=None):
        """ log an warn message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_WARNING, self.log_name + ": " + message))
        else:
            print("WARNING: " + self.log_name + ": " + message)

    def log_error(self, message=None):
        """ log an error message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_ERROR, self.log_name + ": " + message))
        else:
            print("ERROR: " + self.log_name + ": " + message)

    def log_critical(self, message=None):
        """ log an critical message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_CRITICAL, self.log_name + ": " + message))
        else:
            print("CRITICAL: " + self.log_name + ": " + message)
