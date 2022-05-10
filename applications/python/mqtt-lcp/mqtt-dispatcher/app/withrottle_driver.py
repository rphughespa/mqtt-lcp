#!/usr/bin/python3
# withrottle_driver.py
"""

        WithrottleDriver - process class for withrottle message processings
        Translates messages from ThrottleMessage format to/from Withrottle format.


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

import copy

from utils.global_constants import Global
from decoders.withrottle_encoder import WithrottleEncoder
from decoders.withrottle_decoder import WithrottleDecoder
from processes.base_process import SendAfterMessage

from command_mapping_manager import CommandMappingManager
from base_driver import BaseDriver


MAIN_THROTTLE = "withrottle1"


class WithrottleDriver(BaseDriver):
    """ Process withrottle Messages to/from device"""

    def __init__(self, name="withrottle-driver", events=None, queues=None):
        self.local_queues = queues
        self.local_queues[Global.DEVICE] = queues[MAIN_THROTTLE]
        super().__init__(name=name,
                         events=events,
                         queues=self.local_queues)
        self.all_device_queues = []
        self.all_device_queues += [Global.WITHROTTLE1]
        self.all_device_queues += [Global.WITHROTTLE2]
        self.all_device_queues += [Global.WITHROTTLE3]
        self.all_device_queues += [Global.WITHROTTLE4]
        self.decoder = WithrottleDecoder(queues[Global.LOGGER])
        self.encoder = WithrottleEncoder(queues[Global.LOGGER])
        self.cab_queue = queues[Global.CAB]
        self.switch_queue = queues[Global.SWITCH]
        self.wi_ping_send_after_message = None
        self.mapping_manager = CommandMappingManager()

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        self.wi_ping_send_after_message = \
            SendAfterMessage(Global.PING, None,
                             5000)  # call wi_ping method every 5 seconds
        self.send_after(self.wi_ping_send_after_message)

    def process_message(self, new_message):
        """ process messages from queue """

        if len(new_message) == 3:
            (msg_type, msg_body, msg_device_identity) = new_message
            if msg_type == Global.DEVICE_INPUT:
                self.log_info("Rcvd from Server: " + str(msg_device_identity) + ": " + str(msg_body))

        # print(">>> message: " + str(new_message))
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            msg_type = None
            _msg_body = None
            _msg_device_identity = None
            # message are in either (type,message) or (type, message, identity) format
            if len(new_message) == 3:
                (msg_type, _msg_body, _msg_device_identity) = new_message
            else:
                (msg_type, _msg_body) = new_message
            if msg_type == Global.PING:
                self.send_after(self.wi_ping_send_after_message)
                self.__send_withrottle_pings()
                msg_consummed = True
            else:
                self.log_debug("Unprocessed message: " + str(new_message))
        return msg_consummed

    def decode_message(self, msg_body, source):
        """ decode withrottle message """
        #print(">>> decode, before: " + str(msg_body))
        decoded_message = self.decoder.decode_message(msg_body, source)
        #print(">>> .... after: " + str(decoded_message))
        return decoded_message

    def encode_message(self, msg_body, source):
        """ encode withrottle message """
        #print(">>> encode, before: " + str(msg_body))
        encoded_message = self.encoder.encode_message(msg_body, source)
        #print(">>> .... after: " + str(encoded_message))
        return encoded_message

    def process_unsolicited_device_input_message(self, msg_body, msg_device_identity):
        """ received unsolicted input from device """
        #  print(">>> from: " + str(msg_device_identity))
        ### if msg_device_identity == MAIN_THROTTLE:
        # only accent unsolicited message from the main throttle
        decoded_message = self.decoder.decode_message(msg_body, Global.SERVER)
        #  ignore certain unsolicited messages ...
        if decoded_message.command in \
                [Global.VERSION, Global.PING, Global.INFO,
                Global.FASTCLOCK, Global.TURNOUT, Global.LABEL, Global.ROSTER]:
            if msg_device_identity == MAIN_THROTTLE:
                self.log_info(str(msg_device_identity) + ": " + str(decoded_message.command)
                        + " ... " + str(decoded_message.text))
        # but process some ...
        elif decoded_message.command in [Global.SWITCH, Global.POWER]:
            # send some input to the cab_process
            if msg_device_identity == MAIN_THROTTLE: # only send if from main_throttle
                self.switch_queue.put((Global.DRIVER_INPUT, decoded_message))
        elif decoded_message.command == Global.UNKNOWN:
            self.log_error(str(msg_device_identity) +
                        ": Unknown withrottle input: " + str(decoded_message.text))
        else:
            if decoded_message.command not in [Global.ROUTE, Global.CONSIST, Global.ADDRESS]:
                self.log_warning(str(msg_device_identity) +
                            ": Unexpected withrottle input: " + str(decoded_message))

    def acquire_loco(self, throttle_message):
        """ acquire a new loco for throttle """
        acquire_message = copy.deepcopy(throttle_message)
        response_message = super().acquire_loco(throttle_message)
        self.send_and_wait_throttle_message(acquire_message)
        return response_message

    def release_loco(self, throttle_message):
        """ release a loco from throttle """
        release_message = copy.deepcopy(throttle_message)
        response_message = super().release_loco(throttle_message)
        self.send_and_wait_throttle_message(release_message)
        return response_message


    def find_device_queue(self, throttle_message):
        """ determine which device queue to use for sending messages """
        return throttle_message.throttle_id

    def disconnect_throttle(self, throttle_message):
        """ disconnect a throttle"""
        self.mapping_manager.clear_mqtt_throttle(throttle_message)
        return super().disconnect_throttle(throttle_message)

    def adjust_device_message_after_read(self, throttle_message):
        """ translate wi throttle info to mqtt info """
        #print(">>> adjust after: " +str(throttle_message), end="\n")
        adj_message = self.mapping_manager.translate_wi_to_mqtt_cab(throttle_message)
        #print("   >>> " + str(adj_message))
        return adj_message

    def adjust_device_message_before_send(self, throttle_message):
        """ translate wi throttle info to mqtt info """
        #print(">>> adjust after: " +str(throttle_message), end="\n")
        adj_message = self.mapping_manager.translate_mqtt_to_wi_cab(throttle_message)
        #print("   >>> " + str(adj_message))
        return adj_message

    #
    # private functions
    #

    def __send_withrottle_pings(self):
        """ send 'pings' to withrottle server """
        for queue_name in self.all_device_queues:
            #print(">>> wi queue: " + str(queue_name))
            queue = self.queues[queue_name]
            queue.put((Global.DEVICE_SEND, "*"))
