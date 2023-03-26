#!/usr/bin/python3
# global_synonyms.py
"""

global_synonyms.py - helper class to provide use of synonyms for certain terms.
        All methods are class level functions


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


from global_constants import Global


class Synonyms(object):
    """ help class for synonyms of global terms """
    def __init__(self):
        pass

    @classmethod
    def is_synonym_activate(cls, name=None):
        """ checks for synonyms of 'throw' """
        syn = False
        if name in [Global.THROW, Global.OPEN, Global.ON, Global.ACTIVATE,
                    "1", 1]:
            syn = True
        return syn

    @classmethod
    def is_synonym_inactive(cls, name=None):
        """ check for synonyms of 'closed' """
        syn = False
        if name in [Global.CLOSED, Global.OFF, Global.INACTIVE, "0", 0]:
            syn = True
        return syn

    @classmethod
    def is_synonym_deactivate(cls, name=None):
        """ check for synonyms of 'close' """
        syn = False
        if name in [Global.CLOSE, Global.OFF, Global.DEACTIVATE, "0", 0]:
            syn = True
        return syn

    @classmethod
    def desired_to_reported(cls, desired=None):
        """ convert synonyms to past tense reported """
        reported = desired
        if desired == Global.THROW:
            reported = Global.THROWN
        if desired == Global.CLOSE:
            reported = Global.CLOSED
        if desired == Global.OPEN:
            reported = Global.OPENED
        if desired == Global.ACTIVATE:
            reported = Global.ACTIVATED
        if desired == Global.DEACTIVATE:
            reported = Global.DEACTIVATED
        if desired == Global.CONNECT:
            reported = Global.CONNECTED
        if desired == Global.DISCONNECT:
            reported = Global.DISCONNECTED
        if desired == Global.ACQUIRE:
            reported = Global.ACQUIRED
        if desired == Global.PAUSE:
            reported = Global.PAUSED
        if desired == Global.RUN:
            reported = Global.RUNNING
        if desired == Global.RELEASE:
            reported = Global.RELEASED
        return reported
