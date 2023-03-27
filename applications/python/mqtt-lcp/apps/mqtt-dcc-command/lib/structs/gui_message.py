#!/usr/bin/python3
# gui_message.py
"""

    GuiMessage - class that is used decoding/encoding giu messages

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


class WiThrottleConst(object):
    """ data struct for decodec withrottle message """
    CLOSED = 2
    THROWN = 4
    UNKNOWN = 1
    ACTIVE = 2
    INACTIVE = 4
    FORWARD = 1
    REVERSE = 0
    MAJOR_SEP = "]\\["
    MINOR_SEP = "}|{"
    SUB_SEP = "<;>"
    PORT_SEP = ":"


class GuiMessage(object):
    """ Data structure used to store decoded gui message """
    def __init__(self):
        """ Initialize """
        self.command = None
        self.sub_command = None
        self.key = None
        self.name = None
        self.node_id = None
        self.port_id = None
        self.gui_id = None
        self.cab_id = None
        self.dcc_id = None
        self.slot_id = None
        self.throttle_id = None
        self.command_topic = None
        self.speed = None
        self.direction = None
        self.function = None
        self.address_type = None
        self.sub_address = None
        self.items = None  # items may be either a list or a dict
        self.text = None
        self.image = None
        self.sequence = None
        self.value = None
        self.mode = None
        self.reported = None
        self.respond_to = None
        self.response_queue = None

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def get_gui_key(self):
        """ get gui key """
        return str(self.node_id) + ":" + str(self.gui_id)
