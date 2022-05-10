#!/usr/bin/python3
# throttle_process.py
"""


throttle_process - the application process for mqtt-throttle


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
OUT OFSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys
import time
import datetime
from queue import Queue
from multiprocessing import Event

sys.path.append('../lib')

from utils.global_constants import Global
# from utils.global_synonyms import Synonyms
from utils.utility import Utility

from structs.throttle_message import ThrottleMessage

from processes.base_process import BaseProcess
from processes.base_process import SendAfterMessage

from throttle_thread import ThrottleThread
from components.tk_message import TkMessage

class ThrottleProcess(BaseProcess):
    """ Class that waits for an event to occur """
    def __init__(self, events=None, queues=None):
        super().__init__(name="throttle",
                         events=events,
                         in_queue=queues[Global.DEVICE],
                         app_queue=queues[Global.APPLICATION],
                         log_queue=queues[Global.LOGGER])
        self.log_info("Starting")
        self.tk_exit_event = Event()
        self.tk_exit_event.clear()
        self.tk_client = None
        self.screensize = Global.MEDIUM   # small, medium, large
        self.tk_in_queue = Queue(100)
        self.tk_out_queue = Queue(100)
        self.screensize = Global.MEDIUM   # small, medium, large
        self.topic_sensor_pub = None
        self.topic_registry_pub = None
        self.time_send_after_message = None
        # self.registry_helper = MqttRegistryHelper(self, self.log_queue)

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        connect_message = ThrottleMessage()
        connect_message.command = Global.CONNECT
        connect_message.name = "pi-throttle"
        # send first time after 3 seconds
        self.time_send_after_message = \
                SendAfterMessage(Global.TIME, None,3000)
        self.send_after(self.time_send_after_message)
        self.app_queue.put((Global.PUBLISH, connect_message))
        self.display_time_message()
        self.start_tk()

    def shutdown_process(self):
        """ shutdown the process """
        if self.tk_client is not None:
            self.tk_client.shutdown()
            self.tk_client = None
        super().shutdown_process()


    def start_tk(self):
        """Start tk IO"""
        self.log_info('starting tk client thread')
        self.tk_client = ThrottleThread(self.log_queue, 'tk_thread', self, self.events, self.tk_exit_event)
        self.tk_client.start()
        time.sleep(1)

    def process_message(self, new_message=None):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        # print("New Message: " + str(new_message))
        if not msg_consummed:
            (msg_type, msg_body) = new_message
            if msg_type == Global.TIME:
                # send next time after 30 seconds
                self.time_send_after_message.send_after=30000
                self.send_after(self.time_send_after_message)
                self.display_time_message()
                msg_consummed = True
            elif msg_type == Global.DEVICE_SEND:
                self.send_message_to_tk(msg_body)
                msg_consummed = True
        return msg_consummed

    def process_other(self):
        """ perform other none message relared tasks """
        super().process_other()
        if self.tk_exit_event.is_set():
            #print(">>> send disconnect")
            disconnect_message = ThrottleMessage()
            disconnect_message.command = Global.DISCONNECT
            disconnect_message.name = "pi-throttle"
            self.app_queue.put((Global.PUBLISH, disconnect_message))
            # wait a bit for message to be send before shuttong down
            time.sleep(1)
            # now shutdown all processes
            #print(">>> now shutdown app")
            self.events[Global.SHUTDOWN].set()
        if self.tk_client is not None:
            message = None
            if not self.tk_in_queue.empty():
                message = self.tk_in_queue.get()
                if message.msg_type == Global.PUBLISH:
                    # msg_data s/b a thrtottle message
                    # fprward to app_process
                    self.app_queue.put((Global.PUBLISH, message.msg_data))

    def process_request_registry_message(self, msg_body=None):
        """ process request registry message """
        report_desired = msg_body.get_desired_value_by_key(Global.REPORT)
        if report_desired == Global.INVENTORY:
            #self.report_inventory(msg_body=msg_body)
            pass
        else:
            self.log_unexpected_message(msg_body=msg_body)

    def display_time_message(self):
        """ display the current local time """
        local_time_epoch = Utility.now_seconds()
        local_time = datetime.datetime.fromtimestamp( \
                local_time_epoch).isoformat()
        time_msg_body = TkMessage(msg_type=Global.TIME, \
                            cab=Global.ALL,
                            msg_data={Global.DATETIME: local_time})
        # print("Time: "+str(time_msg_body))
        self.send_message_to_tk(time_msg_body)

    def send_message_to_tk(self, message):
        """ send message to an tk screens """
        if self.tk_client is not None:
            self.tk_out_queue.put(message)

    def received_from_tk(self, tk_input):
        """ call back to process received tk input. override in derived class"""
        self.app_queue.put((tk_input.msg_type, tk_input.msg_data))

    def get_incomming_message_from_queue(self):
        """ get a message from incomming queue"""
        message = None
        if not self.tk_in_queue.empty():
            message = self.tk_in_queue.get()
        return message

    def queue_tk_input(self, tk_input):
        """ queue tk input """
        # print("queue input: " + str(tk_input))
        self.tk_in_queue.put(tk_input)

    def process_input(self):
        """ process input from all source input queues"""
        # process all input of a given type in order of importance: keyboard, serial, mqtt
        if self.tk_client is not None:
            tk_input = self.get_incomming_message_from_queue()
            if tk_input is not None:
                self.received_from_tk(tk_input)


    #
    # private functions
    #
