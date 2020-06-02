#!/usr/bin/python3
# main.py for mqtt-servo

"""

mqtt-servo - Interface to servos typically used for switches

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

# platforms for esp32 = esp32, for lobo esp32 = esp32_LoBo, for pi = linux
if sys.platform.startswith('esp32'):
    from queue_esp32 import Queue
else:
    from queue_py import Queue

from global_constants import Global
from local_constants import Local
from mqtt_parsed_message_data import MqttParsedMessageData
from i2c_io_data import I2cIoData
from node_base_i2c import NodeBaseI2c


class MqttServo(NodeBaseI2c):
    """ Process rfid tag readers"""

    def __init__(self):
        super().__init__()
        self.topic_sensor_pub = None
        self.last_reported = {}

    def initialize_threads(self):
        """ Initailize all threads"""
        super().initialize_threads()
        self.topic_sensor_pub = self.publish_topics[Global.SENSOR]

    def process_switch_input(self, i2c_io_data):
        """ Process a switch input """
        self.log_queue.add_message("debug", Local.MSG_NEW_SWITCH+i2c_io_data.reported)
        self.last_reported[i2c_io_data.mqtt_port] = i2c_io_data
        if i2c_io_data.res_topic is not None:
            state_message = self.format_state_body(self.node_name,
                    i2c_io_data.res_mqtt_type,
                    i2c_io_data.res_session_id,
                    i2c_io_data.reported,
                    i2c_io_data.desired,
                    response_topic=None,
                    # metadata=meta,
                    port_id=i2c_io_data.mqtt_port)
            # print("response: "+str(state_message))
            self.send_to_mqtt(i2c_io_data.res_topic, state_message)
        #send data message
        if i2c_io_data.dt_topic is not None:
            now_seconds = self.now_seconds()
            session_id = 'dt:'+str(int(now_seconds))
            state_message = self.format_state_body(self.node_name,
                    i2c_io_data.dt_mqtt_type,
                    session_id,
                    i2c_io_data.reported,
                    None,
                    response_topic=None,
                    # metadata=meta,
                    port_id=i2c_io_data.mqtt_port)
            self.send_to_mqtt(i2c_io_data.dt_topic, state_message)

    def process_inventory_request(self, message_topic, message_body_dict, parsed_body):
        sensor_devices = []
        for device in self.i2c_devices:
            i2c_device = device['dev']
            if hasattr(i2c_device, 'mqtt_port'):
                mqtt_port = i2c_device.mqtt_port
                mqtt_type = i2c_device.mqtt_type
                i2c_data = {}
                i2c_data["port"] = mqtt_port
                i2c_data["type"] = mqtt_type
                i2c_data["sensor"] = str(self.topic_sensor_pub)+"/"+mqtt_port
                if mqtt_port in self.last_reported:
                    i2c_data["reported"] = self.last_reported[mqtt_port].reported
                    i2c_data["timestamp"] = int(self.last_reported[mqtt_port].timestamp)
                else:
                    i2c_data["reported"] = Global.UNKNOWN
                    i2c_data["timestamp"] = 0
                sensor_devices.append(i2c_data)
        device_inventory={"name":"sensors", "description":"collection of sensors", 
            "items": sensor_devices}
        self.log_queue.add_message("info",
                Global.REPORT+" "+Global.INVENTORY)
        mqtt_body = self.format_state_body(self.node_name, Global.REGISTRY,
                parsed_body.session_id, Global.REPORT, Global.REPORT,
                metadata=device_inventory)
        mqtt_topic = parsed_body.res_topic
        self.send_to_mqtt(mqtt_topic, mqtt_body)

    def process_switch_request(self, message_topic, message_body_dict, parsed_body):
        """ Process a request to move a swich """
        port_id = parsed_body.port_id
        desired_state = parsed_body.desired
        response_topic = parsed_body.res_topic
        response_session_id = parsed_body.session_id
        self.log_queue.add_message("debug", "switch id: "+ port_id+", "+desired_state)
        i2c_io_data = I2cIoData()
        i2c_io_data.i2c_type = Global.SWITCH
        i2c_io_data.mqtt_port = port_id
        i2c_io_data.desired = desired_state
        i2c_io_data.reported = Global.UNKNOWN
        i2c_io_data.res_topic = response_topic
        i2c_io_data.res_session_id = response_session_id
        i2c_io_data.dt_topic = self.topic_sensor_pub + "/" +  port_id
        i2c_io_data.res_mqtt_type = Global.SWITCH
        i2c_io_data.dt_mqtt_type = Global.SIGNAL
        self.send_to_i2c({'type':Global.SERVO, 'message':i2c_io_data})

    def process_report_node_status(self, message_topic, message_body_dict):
        topic_parts = message_topic.split("/")
        mqtt_port= topic_parts[-2] # next to last item in list
        parsed_body = MqttParsedMessageData(message_body_dict)
        i2c_io_data = I2cIoData()
        i2c_io_data.reported = Global.UNKNOWN
        i2c_io_data.mqtt_type = Global.UNKNOWN
        i2c_io_data.mqtt_port = parsed_body.port_id
        i2c_io_data.timestamp = 0
        if mqtt_port in self.last_reported:
            i2c_io_data = self.last_reported[mqtt_port]
        self.log_queue.add_message("info",
                Global.REPORT+" "+Global.SWITCH+": "+i2c_io_data.mqtt_port+" "+str(i2c_io_data.reported))
        mqtt_body = self.format_state_body(self.node_name, Global.SENSOR,
                parsed_body.session_id, i2c_io_data.reported, None,
                metadata={Global.TYPE: i2c_io_data.mqtt_type, Global.TIMESTAMP: int(i2c_io_data.timestamp)},
                port_id=i2c_io_data.mqtt_port)
        mqtt_topic = parsed_body.res_topic
        self.send_to_mqtt(mqtt_topic, mqtt_body)

    def process_request_message(self, message_topic, message_body_dict):
        """ process a mqtt request"""
        self.log_queue.add_message("info", Global.MSG_REQUEST_MSG_RECEIVED+ message_topic)
        if message_topic != self.topic_broadcast_subscribed:
            # broadcasts handled in parent class, node_mqtt
            message_type_error = True
            parsed_body = MqttParsedMessageData(message_body_dict)
            if message_topic.endswith("/"+Global.INVENTORY+"/"+Global.REQ):
                self.process_inventory_request(message_topic, message_body_dict, parsed_body)
                message_type_error = False
            else:
                if ((parsed_body.message_root == Global.SENSOR) and
                        (parsed_body.desired == Global.REPORT)):
                    self.process_report_node_status(message_topic, message_body_dict)
                    message_type_error = False
                elif parsed_body.message_root == Global.SWITCH:
                    self.process_switch_request(message_topic, message_body_dict, parsed_body)
                    message_type_error = False
            if message_type_error:
                self.log_queue.add_message("critical", Global.MSG_UNKNOWN_REQUEST + message_topic)
                self.publish_error_reponse(Global.MSG_UNKNOWN_REQUEST, message_topic, message_body_dict)

    def process_response_message(self, message_topic, _message_body_dict):
        """ process mqtt response """
        self.log_queue.add_message("debug", "response message recvd: "+ message_topic)

    def received_from_i2c(self, i2c_io_data):
        """ process i2c input"""
        self.log_queue.add_message("debug", Global.MSG_I2C_DATA_RECEIVED+str(i2c_io_data))
        if i2c_io_data.i2c_type == Global.SWITCH:
            self.process_switch_input(i2c_io_data)

    def received_from_mqtt(self, message_topic, message_body):
        """ process subscribes messages"""
        if message_topic.startswith(Global.CMD):
            if message_topic.endswith("/"+Global.RES):
                self.process_response_message(message_topic, message_body)
            else:
                self.process_request_message(message_topic, message_body)
        # elif message_topic.startswith(self.topic_state_switch_sub):
        #   self.process_state_switch_message(message_topic, message_body)


    def loop(self):
        """ main loop"""
        self.last_ping_seconds = time.mktime(time.localtime())
        while not self.shutdown_app:
            try:
                time.sleep(0.1)
                self.write_log_messages()
                self.process_input()
                now_seconds = self.now_seconds()
                if (now_seconds - self.last_ping_seconds) > self.ping_interval:
                    #print("process pub ping")
                    self.publish_ping_broadcast()
                    #print("... proces ping pub done")
            except KeyboardInterrupt:
                self.shutdown_app = True

# time.sleep(30+random.randint(0,5)) # this app normally starts at boot, allow time for mqtt-broker to initialize
node = MqttServo()
node.initialize_threads()
time.sleep(2)
node.log_queue.add_message("critical", node.node_name+" "+Global.MSG_STARTING)
node.write_log_messages()
node.write_log_messages()

node.loop()

end_seconds = node.now_seconds()
node.log_queue.add_message("critical", node.node_name+" "+Global.MSG_COMPLETED)
node.log_queue.add_message("critical", node.node_name+" "+Global.MSG_EXITING)
node.write_log_messages()
node.shutdown_threads()
node.write_log_messages()
sys.exit(0)
