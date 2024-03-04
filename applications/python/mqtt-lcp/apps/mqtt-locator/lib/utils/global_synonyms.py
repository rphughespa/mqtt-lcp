#!/usr/bin/python3
# global_synonyms.py
"""

global_synonyms.py - helper class to provide use of synonyms for certain terms.
        All methods are class level functions


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


class Synonyms(object):
    """ help class for synonyms of global terms """
    def __init__(self):
        pass

    @classmethod
    def is_on(cls, name):
        """ is value a synonym for on """
        rett = False
        if name in (Global.THROWN, Global.THROW, Global.ON, "1", 1, True):
            rett = True
        return rett

    @classmethod
    def is_off(cls, name):
        """ is value a synonym for off """
        rett = False
        if name in (Global.CLOSED, Global.CLOSE, Global.OFF, "0", 0, False):
            rett = True
        return rett

    @classmethod
    def desired_to_reported(cls, desired=None):
        """ convert synonyms to past tense reported """
        reported = desired
        if desired == Global.THROW:
            reported = Global.THROWN
        if desired == Global.CLOSE:
            reported = Global.CLOSED
        return reported

    @classmethod
    def reverse(cls, desired=None):
        """ convert synonyms to opposite """
        reported = desired
        if desired == Global.THROW:
            reported = Global.CLOSE
        if desired == Global.THROWN:
            reported = Global.CLOSED
        if desired == Global.ON:
            reported = Global.OFF
        if desired == Global.OFF:
            reported = Global.ON
        if desired == Global.ON:
            reported = Global.OFF
        if desired == Global.CONNECT:
            reported = Global.DISCONNECT
        if desired == Global.DISCONNECT:
            reported = Global.CONNECT
        if desired == Global.STOP:
            reported = Global.RUN
        if desired == Global.RUN:
            reported = Global.STOP
        if desired == Global.ACQUIRE:
            reported = Global.RELEASE
        if desired == Global.RELEASE:
            reported = Global.ACQUIRE
        return reported
