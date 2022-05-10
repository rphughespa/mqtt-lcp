#!/usr/bin/python3
# withrottle_client_socket.py
"""

        withrottle_socket - process class for withrottle socket client connect to a withrottle server


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

#import time
#import socket
from processes.socket_client_process import SocketClientProcess
from utils.global_constants import Global

MAX_BUFFER = 120


class WithrottleClientSocket(SocketClientProcess):
    """ Specializes a socket client to connect to a withrottle server """

    def __init__(self, events=None, queues=None, identity=None):
        SocketClientProcess.__init__(self,
                                     identity=identity,
                                     events=events,
                                     queues=queues,
                                     mode="client")

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        # init communication with withrottle server

        self.in_queue.put((Global.DEVICE_SEND, "N" + "mqtt-lcp-" +str(self.identity)))
        self.in_queue.put((Global.DEVICE_SEND, "HU" + "mqtt-lcp-"+ str(self.identity)))

    def publish_input(self, serial_data):
        """ publish serial input """
        # override base class method, add identity to message to indicate source
        message = (Global.DEVICE_INPUT, serial_data, self.identity)
        if self.driver_queue is not None:
            self.driver_queue.put(message)
        else:
            self.send_to_application(message)
    #
    # private functions
    #
