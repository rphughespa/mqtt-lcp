#!/usr/bin/python3
# command_throttle.py
"""

    CommandThrottle.py - Class representing a throttle in the mqtt-dcc-command

the MIT License (MIT)

Copyright © 2021 richard p hughes

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

sys.path.append('../lib')

# from utils.global_constants import Global


class CommandThrottle():
    """ Class representing a throttle in the mqtt-dcc-command """
    def __init__(self, node_id, throttle_id):
        """ initialize"""
        self.node_id = node_id
        self.throttle_id = throttle_id
        self.connect_message = None
        self.last_timestamp = 0
        self.ping_topic = None
        self.cabs = {}

    def key(self):
        """ get key for this object"""
        return self.node_id + ":" + self.throttle_id

    @classmethod
    def make_key(cls, node_id, throttle_id):
        """ generate a key """
        return node_id + ":" + throttle_id
