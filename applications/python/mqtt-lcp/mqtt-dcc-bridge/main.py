#!/usr/bin/python3
# main.py for mqtt-dcc-bridge
"""

mqtt-dcc-bridge - Bridges between MQTT and DCC++ command station connected via seria USB port
            This code uses the commands defined in the dcc++ documentation.
            Check for any applicable restrictions dcc++ places on the use of this information.

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
import random
import copy

from global_constants import Global
from local_constants import Local

from node_base_command_station import NodeBaseCommandStation

from io_data import IoData
from roster import Roster


class MqttDccBridge(NodeBaseCommandStation):
    """ bridge dcc++ command stations with mqtt messaging """

    def __init__(self):
        super().__init__()
        self.topic_cab_pub = None
        self.last_reported = {}


    def initialize_threads(self):
        """ init all io threads """
        super().initialize_threads()
        self.topic_cab_pub = self.publish_topics[Global.CAB]

    def send_data_message(self, io_data):
        """ send a data message """
        #send data message
        now_seconds = self.now_seconds()
        io_data.mqtt_timestamp = now_seconds
        self.last_reported[io_data.mqtt_port] = io_data
        if io_data.mqtt_data_topic is not None:
            session_id = 'dt:'+str(int(now_seconds))
            state_message = self.format_state_body(self.node_name,
                    io_data.dt_mqtt_type,
                    session_id,
                    io_data.mqtt_reported,
                    None,
                    response_topic=None,
                    # metadata=meta,
                    port_id=io_data.mqtt_port)
            self.send_to_mqtt(io_data.mqtt_data_topic, state_message)


    def publish_response_message(self, io_data):
        """ publish track power response """
        message = self.format_state_body(self.node_name, io_data.mqtt_type,
                io_data.mqtt_session_id, io_data.mqtt_reported, io_data.mqtt_desired,
                port_id=io_data.mqtt_port)
        self.send_to_mqtt(io_data.mqtt_resp_topic, message)
        self.write_log_messages()


    ### cab messages ###

    def publish_cab_data_message(self, io_data):
        """ publish track power response """
        now_seconds = self.now_seconds()
        session_id = 'dt:'+str(int(now_seconds))
        if io_data.mqtt_type is not None:
            if io_data.mqtt_port is not None:
                if io_data.mqtt_reported is not None:
                    io_data.mqtt_timestamp = now_seconds
                    self.last_reported[io_data.mqtt_port] = io_data
                    self.log_queue.add_message("info",
                            Global.PUBLISH+" "+io_data.mqtt_type+": "+io_data.mqtt_port+" "+str(io_data.mqtt_reported))
                    mqtt_body = self.format_state_body(self.node_name, io_data.mqtt_type,
                            session_id, io_data.mqtt_reported, None,
                            metadata=io_data.mqtt_metadata,
                            port_id=io_data.mqtt_port)
                    mqtt_topic = self.topic_cab_pub + '/' + io_data.mqtt_port
                    self.send_to_mqtt(mqtt_topic, mqtt_body)
                    self.log_queue.add_message("critical", Local.MSG_CAB_PUBLISHED+" "+str(io_data.mqtt_reported))
                    self.write_log_messages()

    def process_cab_request_message(self, message_topic, io_data):
        """ Process a request to move a swich """
        self.log_queue.add_message("info", Global.CAB + " " + Global.MSG_REQUEST_MSG_RECEIVED+ message_topic)
        new_io_data = copy.deepcopy(io_data)
        new_io_data.i2c_type = Global.CAB
        new_io_data.mqtt_type = io_data.mqtt_message_root
        new_io_data.reported = Global.UNKNOWN
        new_io_data.mqtt_data_topic = self.topic_cab_pub + "/" +  new_io_data.mqtt_port
        new_io_data.mqtt_type = io_data.mqtt_message_root
        new_io_data.dt_mqtt_type = Global.CAB
        request = ({'type':new_io_data.mqtt_message_root, 'message':new_io_data})
        self.dcc_out_queue.put(request)

    def process_cab_input(self, io_data):
        """ Process a cab input """
        self.log_queue.add_message("debug", Local.MSG_NEW_CAB+io_data.reported)
        if io_data.res_topic is not None:
            state_message = self.format_state_body(self.node_name,
                    io_data.mqtt_type,
                    io_data.res_session_id,
                    io_data.reported,
                    io_data.desired,
                    response_topic=None,
                    # metadata=meta,
                    port_id=io_data.mqtt_port)
            print("%%%% response: "+str(state_message))
            self.send_to_mqtt(io_data.res_topic, state_message)
        if io_data.mqtt_send_sensor_msg is True:   # send a sensor msg with response msg
            self.send_data_message(io_data)
        else:
            del self.last_reported[io_data.mqtt_port]  # another node will report state

    ### switch messages ###

    def process_switch_input(self, io_data):
        """ Process a switch input """
        self.log_queue.add_message("info", Local.MSG_NEW_SWITCH+io_data.mqtt_reported)
        if io_data.mqtt_resp_topic is not None:
            state_message = self.format_state_body(self.node_name,
                    io_data.mqtt_type,
                    io_data.mqtt_resp_session_id,
                    io_data.mqtt_reported,
                    io_data.mqtt_desired,
                    response_topic=None,
                    # metadata=meta,
                    port_id=io_data.mqtt_port)
            print("%%%% response: "+str(state_message))
            self.send_to_mqtt(io_data.mqtt_resp_topic, state_message)
        if io_data.mqtt_send_sensor_msg is True:   # send a sensor msg with response msg
            self.send_data_message(io_data)
        else:
            del self.last_reported[io_data.mqtt_port]  # another node will report state

    def process_switch_request_message(self, _message_topic, io_data):
        """ Process a request to move a swich """
        self.log_queue.add_message("info", "switch id: "+ str(io_data.mqtt_port)+", "+str(io_data.mqtt_desired))
        dcc_device = None
        mqtt_key = io_data.mqtt_port +":"+ Global.SWITCH
        if mqtt_key in self.mqtt_devices:
            dcc_device = self.mqtt_devices[mqtt_key]
        new_io_data = copy.deepcopy(io_data)
        new_io_data.io_type = Global.SWITCH
        new_io_data.mqtt_type = io_data.mqtt_message_root
        new_io_data.mqtt_reported = Global.UNKNOWN
        if dcc_device is not None:
            # send sensor msg along with response msg
            new_io_data.mqtt_send_sensor_msg = dcc_device.mqtt_send_sensor_msg
        new_io_data.mqtt_data_topic = self.topic_sensor_pub + "/" +  new_io_data.mqtt_port
        new_io_data.mqtt_data_type = Global.SENSOR
        request = {Global.TYPE:new_io_data.mqtt_message_root, Global.MESSAGE:new_io_data}
        self.dcc_out_queue.put(request)
        data_io_data = copy.deepcopy(io_data)
        data_io_data.reported = Global.INCONSISTENT
        self.send_data_message(data_io_data)

    ### track messages ###

    def process_track_input(self, io_data):
        """ Process a switch input """
        self.log_queue.add_message("debug", Local.MSG_NEW_TRACK+io_data.reported)
        if io_data.res_topic is not None:
            state_message = self.format_state_body(self.node_name,
                    io_data.mqtt_type,
                    io_data.res_session_id,
                    io_data.reported,
                    io_data.desired,
                    response_topic=None,
                    # metadata=meta,
                    port_id=io_data.mqtt_port)
            print("%%%% response: "+str(state_message))
            self.send_to_mqtt(io_data.res_topic, state_message)
        if io_data.mqtt_send_sensor_msg is True:   # send a sensor msg with response msg
            self.send_data_message(io_data)
        else:
            del self.last_reported[io_data.mqtt_port]  # another node will report state

    def process_track_request_message(self, message_topic, io_data):
        """ Process a request to move a swich """
        self.log_queue.add_message("info", Global.TRACK + " " + Global.MSG_REQUEST_MSG_RECEIVED+ message_topic)
        new_io_data = copy.deepcopy(io_data)
        new_io_data.io_type = Global.TRACK
        new_io_data.mqtt_type = io_data.mqtt_message_root
        new_io_data.mqtt_reported = Global.UNKNOWN
        new_io_data.mqtt_data_topic = self.topic_sensor_pub + "/" +  new_io_data.mqtt_port
        new_io_data.dt_mqtt_type = Global.TRACK
        request = ({'type':new_io_data.mqtt_message_root, 'message':new_io_data})
        self.dcc_out_queue.put(request)

    ### other messages ###

    def process_broadcast_message(self, message_topic, _io_data):
        """ process broadcast message """
        if message_topic.endswith("/"+Global.SHUTDOWN):
            self.log_queue.add_message("info", Global.MSG_SHUTDOWN_RECEIVED)
            self.shutdown_app = True

    def process_received_ping_message(self, _message_topic, _io_data):
        """ process a ping message """
        pass

    def process_received_switch_message(self, _message_topic, _io_data):
        """ process a sensor essage """
        pass

    def process_received_sensor_message(self, message_topic, _io_data):
        """ process sensor message received"""
        pass

    def process_request_message(self, message_topic, io_data):
        """ process request message"""
        self.log_queue.add_message("info", Global.MSG_REQUEST_MSG_RECEIVED+ message_topic)
        if message_topic != self.topic_broadcast_subscribed:
            # broadcasts handled in parent class, node_mqtt
            if io_data.mqtt_message_root == Global.TRACK:
                self.process_track_request_message(message_topic, io_data)
            elif io_data.mqtt_message_root == Global.SWITCH:
                self.process_switch_request_message(message_topic, io_data)
            elif io_data.mqtt_message_root == Global.CAB:
                self.process_cab_request_message(message_topic, io_data)
            else:
                self.log_queue.add_message("critical", Global.MSG_UNKNOWN_REQUEST+ message_topic)
                self.publish_error_reponse(Global.MSG_UNKNOWN_REQUEST, message_topic, io_data)

    def process_response_message(self, message_topic, _io_data):
        """ process response message"""
        self.log_queue.add_message("debug", Global.MSG_RESPONSE_RECEIVED+ message_topic)

    def received_from_mqtt(self, message_topic, io_data):
        """ process mqtt input """
        if message_topic.startswith(Global.CMD+"/"):
            if message_topic.endswith("/"+Global.RES):
                self.process_response_message(message_topic, io_data)
            else:
                self.process_request_message(message_topic, io_data)
        elif io_data.mqtt_message_root == Global.PING:
            # print("found ping")
            self.process_received_ping_message(message_topic, io_data)
        elif io_data.mqtt_message_root == Global.SWITCH:
            self.process_received_switch_message(message_topic, io_data)

    def received_from_keyboard(self, key_input):
        """ process keyboard input"""
        self.log_queue.add_message("debug", Global.MSG_KEYBOARD_RECEIVED+" {"+ key_input+"}")
        self.send_serial_message(key_input)

    def loop(self):
        """ main program loop"""
        self.log_queue.add_message("critical", Global.READY)
        self.get_track_status()  # get initial power status of dcc
        self.log_queue.add_message("info", Global.TRACK + " " + Global.POWER+": "+self.dcc_power_status)
        self.write_log_messages()
        self.last_ping_seconds = int(time.mktime(time.localtime()))
        while not self.shutdown_app:
            try:
                time.sleep(0.1)
                self.write_log_messages()
                self.process_input()
                now_seconds = self.now_seconds()
                self.purge_expired_throttles(now_seconds)
                if (now_seconds - self.last_ping_seconds) > self.ping_interval:
                    self.publish_ping_broadcast()
            except KeyboardInterrupt:
                self.shutdown_app = True

# this app normally starts at boot, allow tiem for mqtt-broker to initialize
# time.sleep(30+random.randint(0, 2)) # delay a bit less less than other nodes

node = MqttDccBridge()
node.initialize_threads()
time.sleep(2)
node.log_queue.add_message("critical", node.node_name+" "+Global.MSG_STARTING)
node.write_log_messages()

node.loop()

end_seconds = node.now_seconds()
node.log_queue.add_message("critical", node.node_name+" "+Global.MSG_COMPLETED)
node.log_queue.add_message("critical", node.node_name+" "+Global.MSG_EXITING)
node.write_log_messages()
node.shutdown_threads()
node.write_log_messages()
sys.exit(0)
