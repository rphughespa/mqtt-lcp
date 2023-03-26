#!/usr/bin/python3
# appe_process.py
"""


app_process - the application process for mqtt-railcom


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
OUT OFSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys


sys.path.append('../lib')

import time
import copy

from utils.global_constants import Global
from utils.global_synonyms import Synonyms


from processes.base_mqtt_process import BaseMqttProcess


class AppProcess(BaseMqttProcess):
    """ Class that waits for an event to occur """
    def __init__(self, events=None, queues=None):
        super().__init__(name="app",
                         events=events,
                         in_queue=queues[Global.APPLICATION],
                         mqtt_queue=queues[Global.MQTT],
                         log_queue=queues[Global.LOGGER])
        self.log_info("Starting")


    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        self.log_info("IoDevices:")
        if self.io_config is not None:
            if self.io_config.io_device_map is not None:
                for _key, dev in self.io_config.io_device_map.items():
                    self.log_info("IoDevice: " + str(dev.io_device_type)+" ... " +str(dev.mqtt_port_id))


    def process_message(self, new_message=None):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            # print(">>> new message: " + str(new_message))
            if not msg_consummed:
                self.log_warning("Unknown Message TYpe Received: " +
                                 str(new_message))
                msg_consummed = True
        return msg_consummed

    def process_other(self):
        """ perform other none message relared tasks """
        super().process_other()
        _now = time.mktime(time.localtime())
        # if now > self.exit_time:
        #    print("crashing app_process")
        #    raise ValueError("app_process - time expired")


    def process_request_switch_message(self, msg_body=None):
        """ process for switch requests """
        self.log_info("switch request: "+str(msg_body.mqtt_port_id)+" ... "+str(msg_body.mqtt_desired))
        reported = Synonyms.desired_to_reported(msg_body.mqtt_desired)
        if reported == Global.TOGGLE:
            reported = Global.THROWN
        self.__publish_response(msg_body, reported, None, reported)
        msg_consummed = True
        return msg_consummed

    def process_request_signal_message(self, msg_body=None):
        """ process for signal requests """
        self.log_info("signal request: "+str(msg_body.mqtt_port_id)+" ... "+str(msg_body.mqtt_desired))
        reported = Synonyms.desired_to_reported(msg_body.mqtt_desired)
        self.__publish_response(msg_body, reported, None, reported)
        msg_consummed = True
        return msg_consummed
    #
    # private functions
    #


    def __publish_response(self, msg_body, reported, message, data_reported):
        """ send response back to requestor """
        metadata = None
        if message is not None:
            metadata = {Global.ERROR: message}
        # print(">>> response: " + str(reported+" ... " + str(data_reported)+" ...\n"+str(msg_body.mqtt_port_id)))
        self.publish_response_message(\
                reported=reported,
                metadata=metadata,
                data_reported=data_reported,
                message_io_data=msg_body)
