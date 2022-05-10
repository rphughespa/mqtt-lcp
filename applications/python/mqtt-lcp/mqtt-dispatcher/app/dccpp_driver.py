#!/usr/bin/python3
# dccpp_driver.py
"""

        DccppDriver - process class for dccpp serial message processings
        Translates messages to/from ThrottleMessage format to DCC++ format


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

sys.path.append('../lib')

from utils.global_constants import Global

from decoders.dccpp_decoder import DccppDecoder
from decoders.dccpp_encoder import DccppEncoder

from base_driver import BaseDriver


class DccppDriver(BaseDriver):
    """ Process dcc++ Messages to/from device """
    def __init__(self, events=None, queues=None):
        super().__init__(name="dcc++ driver",
                         events=events,
                         queues=queues)

        self.decoder = DccppDecoder()
        self.encoder = DccppEncoder()

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()

    def process_non_throttle_message(self, msg_body):
        """ process messages not related to throttles """
        # print(">>> non throttle: " + str(msg_body))
        if msg_body.command == Global.SWITCH:
            # for dcc++, switch command do not get acknowleged, send only
            self.send_throttle_message(msg_body)
            # print(">>> send response: " + msg_body.response_queue)
            self.publish_response(msg_body, msg_body.response_queue)
        else:
            # print(">>> non throttle: " + str(msg_body))
            response_message = self.send_and_wait_throttle_message(msg_body)
            # print(">>> device response: " + str(response_message))
            self.publish_response(response_message, msg_body.response_queue)
