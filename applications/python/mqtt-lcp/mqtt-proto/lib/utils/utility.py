#!/usr/bin/python3
# Utility.py
"""


   Utility.py - Misc utility functionx

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
import time


class Utility(object):
    """ help class utility functions """
    def __init__(self):
        pass

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    @classmethod
    def now_seconds(cls):
        """ calc now seconds """
        now_sec = 0
        now_sec = int(time.mktime(time.localtime()))
        return now_sec

    @classmethod
    def now_milliseconds(cls):
        """ calc now seconds """
        now_millisec = 0
        now_millisec = int(time.time() * 1000)
        return now_millisec

    @classmethod
    def now_seconds_rounded_up(cls, round_amount):
        """ round current seconds up to the necxt increment """
        # pass 60 for next minute, pass 3600 for next hour
        now_seconds = int(time.mktime(time.localtime()))
        now_minute = now_seconds - (now_seconds % round_amount)
        next_minute = now_minute + round_amount
        return next_minute

    @classmethod
    def is_number(cls, string):
        """ check if a string is numeric """
        try:
            float(string)
            return True
        except ValueError:
            return False
