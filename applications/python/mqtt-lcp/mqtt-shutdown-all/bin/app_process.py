#!/usr/bin/python3
# appe_process.py
"""


app_process - the application process for mqtt_shutdown_all


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

from utils.global_constants import Global
from utils.utility import Utility
from structs.io_data import IoData
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
        time.sleep(10)
        self.log_critical("Broadcasting a shutdown message to all nodes")
        time.sleep(3)
        max_sleep = 10
        while max_sleep > 0:
            print("... " + str(max_sleep))
            max_sleep -= 1
            time.sleep(1)
        now = Utility.now_milliseconds()
        session = "req" + str(now)
        topic = self.mqtt_config.publish_topics.get(Global.BROADCAST,
                                                    Global.UNKNOWN)
        body = IoData()
        body.mqtt_message_root = Global.NODE
        body.mqtt_node_id = Global.ALL
        body.mqtt_desired = Global.SHUTDOWN
        body.mqtt_session_id = session
        body.mqtt_version: "1.0"
        body.mqtt_timestamp: now
        super().publish_message(topic, body)
        self.log_critical(" ... exiting...")
        time.sleep(10)
        self.events[Global.SHUTDOWN].set()
