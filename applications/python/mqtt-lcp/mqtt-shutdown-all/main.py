#!/usr/bin/python3

# main.py for mqtt-shutdown-all
"""

mqtt-shutdwon-all - send a message to all nodes to shutdown.  Applicaion node Apps do a clean exit. 
        The "mqtt-supervisor" node app actually does an operating system shutdown.

Note: on PI's, only Raspbian is stopped, the power is not actully turned off.

the MIT License (MIT)

Copyright © 2020 richard p hughes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the “Software”), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import sys
sys.path[1] = '../lib'
import time

from global_constants import Global
from local_constants import Local

from node_base_mqtt import NodeBaseMqtt

class GlobalShutdownAll(NodeBaseMqtt):
    """ Publish shutdown message to all subectribed nodes"""

    def __init__(self):
        super().__init__()
        self.topic_broadcast_pub = None

    def initialize_threads(self):
        """ initialize threads"""
        super().initialize_threads()
        self.topic_broadcast_pub = self.publish_topics['broadcast']

    def publish_shutdown_broadcast(self):
        """ publish shutdown broadcast message"""
        now_seconds = self.now_seconds()
        session_id = 'req:'+str(int(now_seconds))
        new_state_message = self.format_state_body(self.node_name,
                Global.COMMAND, session_id, None, desired_state=Global.SHUTDOWN)
                # Global.COMMAND, session_id, None, desired_state=Global.REBOOT)
                # Global.COMMAND, session_id, None, desired_state=Global.BACKUP)
        self.send_to_mqtt(self.topic_broadcast_pub, new_state_message)
        self.log_queue.add_message("critical", Local.MSG_SHUTDOWN_PUBLISHED)
        self.write_log_messages()

    def loop(self):
        """ main loop"""
        self.log_queue.add_message("critical", Global.READY)
        # Not looping, just sending shutdown message")
        self.publish_shutdown_broadcast()

node = GlobalShutdownAll()
node.initialize_threads()
time.sleep(2)
node.log_queue.add_message("critical", node.node_name+ " "+Global.MSG_STARTING)
node.write_log_messages()

node.loop()

end_seconds = node.now_seconds()
node.log_queue.add_message("critical", node.node_name + " "+ Global.MSG_COMPLETED)
node.log_queue.add_message("critical", node.node_name + " " + Local.MSG_WAIT)
node.write_log_messages()
time.sleep(60)
node.log_queue.add_message("critical", node.node_name + " "+ Global.MSG_EXITING)
node.write_log_messages()
node.shutdown_threads()
node.write_log_messages()
sys.exit(0)
