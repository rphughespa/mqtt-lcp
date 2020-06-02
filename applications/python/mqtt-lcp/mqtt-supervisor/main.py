#!/usr/bin/python3
# main.py for mqtt-supervisor

"""


mqtt-supervisor - power down/reboot computer after receipt of a "broadcast/shutdown" message.
    A "shutdown" o/s cmmand is executed after a delay.  Both the delay and the command
    are specified in the JSON config file.  Since this application will be run on many
    computer in the network, The computer name passed to the MQTT broker is not
    the node name in the config file, but a unique name generted by the applicaion.

Note: on PI's, only Raspbian is stopped, the power is not actually turned off.

the MIT License (MIT)

Copyright  2020 richard p hughes

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
import time
import random
from subprocess import call

sys.path[1] = '../lib'

from mqtt_parsed_message_data import MqttParsedMessageData

from global_constants import Global

from node_base_mqtt import NodeBaseMqtt

class GlobalSupervisor(NodeBaseMqtt):
    """Powerdown this MQTT Node."""

    def __init__(self):
        super().__init__()
        self.delay = 15
        self.ping_interval = 60

    def initialize_threads(self):
        """Initialize all IO threads."""
        super().initialize_threads()

    def powerdown_system(self):
        """ Execute the powerdown."""
        self.log_queue.add_message("info", Global.MSG_SHUTDOWN_RECEIVED)
        # a broadcast "shutdown received", wait and then powerdown computer
        self.write_log_messages()
        time.sleep(self.delay)
        self.log_queue.add_message("info", Global.SHUTDOWN)
        self.write_log_messages()
        time.sleep(self.delay)
        call(self.shutdown_command, shell=True)

    def reboot_system(self):
        """ Execute the powerdown."""
        self.log_queue.add_message("info", Global.MSG_REBOOT_RECEIVED)
        # a broadcast "shutdown received", wait and then powerdown computer
        self.write_log_messages()
        time.sleep(self.delay)
        self.log_queue.add_message("info", Global.REBOOT)
        self.write_log_messages()
        time.sleep(self.delay)
        call(self.reboot_command, shell=True)

    def process_inventory_request(self, message_topic, message_body_dict):
        parsed_body = MqttParsedMessageData(message_body_dict)
        self.log_queue.add_message("info",
                Global.REPORT+" "+Global.INVENTORY)
        mqtt_body = self.format_state_body(self.node_name, Global.REGISTRY,
                parsed_body.session_id, Global.REPORT, Global.REPORT)
        mqtt_topic = parsed_body.res_topic
        self.send_to_mqtt(mqtt_topic, mqtt_body)


    def process_request_message(self, message_topic, message_body_dict):
        """ Process MQTT request messages"""
        self.log_queue.add_message("debug",
                Global.MSG_RESPONSE_RECEIVED+ message_topic)
        message_type_error = True
        if message_topic.endswith("/"+Global.INVENTORY+"/"+Global.REQ):
            self.process_inventory_request(message_topic, message_body_dict)
            message_type_error = False
        if message_type_error:
                self.log_queue.add_message("critical", Global.MSG_UNKNOWN_REQUEST + message_topic)
                self.publish_error_reponse(Global.MSG_UNKNOWN_REQUEST, message_topic, message_body_dict)

    def process_response_message(self, message_topic, _message_body_dict):
        """ Process MQTT response messages"""
        self.log_queue.add_message("debug",
                Global.MSG_RESPONSE_RECEIVED+ message_topic)

    def received_from_mqtt(self, message_topic, message_body_dict):
        """ Process Subscribed MQTT messages"""
        if message_topic.startswith(Global.CMD+"/"):
            if message_topic.endswith("/"+Global.RES):
                self.process_response_message(message_topic, message_body_dict)
            else:
                self.process_request_message(message_topic, message_body_dict)
        # elif message_topic.startswith(self.topic_state_turnout_sub):
        #   self.process_state_turnout_message(message_topic, message_body)

    def loop(self):
        """ Main process loop"""
        self.log_queue.add_message("critical", Global.READY)
        self.last_ping_seconds = self.now_seconds()
        while not self.shutdown_app:
            try:
                time.sleep(0.5)
                self.write_log_messages()
                self.process_input()
                now_seconds = self.now_seconds()
                if (now_seconds - self.last_ping_seconds) > self.ping_interval:
                    self.publish_ping_broadcast()
            except KeyboardInterrupt:
                self.shutdown_app = True

# this app normally starts at boot, allow time for mqtt-broker to initialize
time.sleep(30+random.randint(0, 5))

node = GlobalSupervisor()
node.initialize_threads()
time.sleep(2)
node.log_queue.add_message("critical", node.node_name+ " "+Global.MSG_STARTING)
node.write_log_messages()

node.loop()

end_seconds = node.now_seconds()
node.log_queue.add_message("critical", node.node_name + " "+Global.MSG_COMPLETED)
node.log_queue.add_message("critical", node.node_name + " "+Global.MSG_EXITING)
node.write_log_messages()
node.shutdown_threads()
node.write_log_messages()
if node.powerdown_computer:
    node.powerdown_system()
elif node.reboot_computer:
    node.reboot_system()
else:
    sys.exit(0)
