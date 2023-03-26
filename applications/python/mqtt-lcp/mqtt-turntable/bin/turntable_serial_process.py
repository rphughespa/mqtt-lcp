#!/usr/bin/python3
# turntable_serial_process.py
"""

        turntable_seriall_process - process class for turntable serial message processings

        Generates and parses messages for the turntable

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

sys.path.append('../lib')

from utils.global_constants import Global

from processes.serial_process import SerialProcess



class TurntableSerialProcess(SerialProcess):
    """ Process Some turntable Messages from Serial Port"""
    def __init__(self, events=None, queues=None):
        self.queues = queues
        # we don't have a separate driver process
        # redirect driver messages to application process
        self.queues[Global.DRIVER] = queues[Global.APPLICATION]
        super().__init__(events=events,queues=queues)

        self.bytes_queue = []
        self.bytes_queue_length_desired = 0
        self.message_type = {}
        self.queues[Global.DEVICE].put((Global.DEVICE_SEND, "!INFO"))
        # self.queues[Global.DEVICE].put((Global.DEVICE_SEND, "!HOME"))

    def decode_message(self, msg_body):
        """ decode a message """
        #print(">>> decode: " + str(msg_body))
        return msg_body

    def encode_message(self, msg_body):
        """ encode a message """
        #print(">>> encode: " + str(msg_body))
        return msg_body
