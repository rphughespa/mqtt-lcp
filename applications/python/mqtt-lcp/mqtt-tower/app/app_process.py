#!/usr/bin/python3
# app_process.py
"""

app_process - the application process for mqtt-tower


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

sys.path.append('../lib')

from processes.base_mqtt_process import BaseMqttProcess
from utils.global_constants import Global


class AppProcess(BaseMqttProcess):
    """ Class that waits for an event to occur """
    def __init__(self, events=None, queues=None):
        super().__init__(name="app",
                         events=events,
                         in_queue=queues[Global.APPLICATION],
                         mqtt_queue=queues[Global.MQTT],
                         log_queue=queues[Global.LOGGER])
        self.log_info("Starting")
        self.fastclock_queue = queues[Global.FASTCLOCK]
        self.inventory_queue = queues[Global.INVENTORY]
        self.report_queue = queues[Global.REPORT]
        self.data_path = None
        self.backup_path = None
        self.dashboard_timeout = 60

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        pass

    def process_message(self, new_message=None):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            (msg_type, msg_body) = new_message
            if msg_type == Global.PUBLISH:
                if msg_body[Global.TYPE] == Global.DATA:
                    self.publish_data_message(msg_body[Global.TOPIC],
                                              msg_body[Global.BODY])
                    msg_consummed = True
                elif msg_body[Global.TYPE] == Global.RESPONSE:
                    # response: " + str(msg_body))
                    self.publish_response_message(msg_body[Global.REPORTED], \
                                    msg_body[Global.METADATA], None, msg_body[Global.BODY])
                    msg_consummed = True
                elif msg_body[Global.TYPE] == Global.REQUEST:
                    self.publish_request_message(msg_body[Global.TOPIC],
                                                 msg_body[Global.BODY])
                    msg_consummed = True
            elif msg_type == Global.RESPONSE:

                msg_consummed = True
        return msg_consummed

    def process_request_tower_message(self, msg_body=None):
        """ process request tower message """
        self.log_info("Tower Request: " + str(msg_body.mqtt_desired))
        report_desired = msg_body.get_desired_value_by_key(Global.REPORT)
        #print(">>> tower desired:" + str(report_desired))
        if report_desired in [Global.INVENTORY, Global.STATES]:
            self.inventory_queue.put((Global.REQUEST, msg_body))
        elif report_desired in \
                [Global.DASHBOARD, Global.PANELS, \
                Global.WARRANTS, Global.PANELS]:
            self.report_queue.put((Global.REQUEST, msg_body))
        else:
            self.log_unexpected_message(msg_body=msg_body)
            metadata = {Global.ERROR, "Unknown report requested"}
            reported = Global.ERROR
            self.in_queue.put((Global.PUBLISH, {Global.TYPE: Global.RESPONSE, \
                Global.REPORTED: reported, Global.METADATA: metadata}))

    def process_request_fastclock_message(self, msg_body=None):
        """ process fastclock request """
        # print(">>> fastclock request")
        # forward message to fastclock process for processing
        self.fastclock_queue.put((Global.REQUEST, msg_body))

    def process_data_ping_message(self, msg_body=None):
        """ process data ping received message """
        self.report_queue.put((Global.PING, msg_body))

    def process_response_inventory_message(self, msg_body=None):
        """ process inventory request response """
        # forward message to inventory process for processing
        self.inventory_queue.put((Global.RESPONSE, msg_body))

    def process_data_sensor_message(self, msg_body=None):
        """ process data sensor message """
        # forward message to inventory process for processing
        self.inventory_queue.put((Global.STATE, msg_body))

    def process_data_switch_message(self, msg_body=None):
        """ process data switch message """
        # forward message to inventory process for processing
        self.inventory_queue.put((Global.STATE, msg_body))

    def process_data_signal_message(self, msg_body=None):
        """ process data signal message """
        # forward message to inventory process for processing
        self.inventory_queue.put((Global.STATE, msg_body))

    def process_data_block_message(self, msg_body=None):
        """ process data block message """
        self.inventory_queue.put((Global.STATE, msg_body))

    def process_data_locator_message(self, msg_body=None):
        """ process data locator message """
        # forward message to inventory process for processing
        self.inventory_queue.put((Global.STATE, msg_body))

    #
    # private functions
    #
