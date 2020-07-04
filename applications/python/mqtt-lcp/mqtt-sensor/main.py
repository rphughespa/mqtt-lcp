#!/usr/bin/python3
# main.py for mqtt-sensor

"""

mqtt-sensor - Read and report various I2C sensors: RFID tags, Rotary knobs, etc.
                Generate MQTT-LCP sensor messages

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
if sys.platform.startswith("esp32"):
    sys.path[1] = './lib'
else:
    sys.path[1] = '../lib'

import time
import copy


from node_base_i2c import NodeBaseI2c
from io_data import IoData

from global_constants import Global

class MqttSensor(NodeBaseI2c):
    """ Process rfid tag readers"""

    def __init__(self):
        super().__init__()
        self.topic_sensor_pub = None
        self.last_reported = {}

    def initialize_threads(self):
        """ Initailize all threads"""
        super().initialize_threads()
        self.topic_sensor_pub = self.publish_topics[Global.SENSOR]
        for device in self.i2c_devices:
            i2c_device = device['dev']
            if hasattr(i2c_device, 'mqtt_port'):
                io_data = IoData()
                io_data.mqtt_port = i2c_device.mqtt_port
                io_data.mqtt_reported = Global.UNKNOWN
                io_data.mqtt_timestamp = 0
                print("init reported: "+str(io_data.mqtt_port))
                self.last_reported[io_data.mqtt_port] = io_data

    def process_rotary_input(self, io_data):
        """ process rfid input """
        now_seconds = self.now_seconds()
        session_id = 'dt:'+str(int(now_seconds))
        # print("rfid: "+str(io_data.mqtt_type)+", "+str(io_data.mqtt_port)+", "+str(io_data.reported))
        if io_data.mqtt_type is not None:
            if io_data.mqtt_port is not None:
                if io_data.reported is not None:
                    io_data.mqtt_timestamp = now_seconds
                    reported_io_data = copy.deepcopy(io_data)
                    print("update reported: "+str(reported_io_data.mqtt_port))
                    self.last_reported[reported_io_data.mqtt_port] = reported_io_data
                    self.log_queue.add_message("info",
                            Global.PUBLISH+" "+Global.ROTARY+": "+io_data.mqtt_port+" "+str(io_data.reported))
                    mqtt_body = self.format_state_body(self.node_name, Global.SENSOR,
                            session_id, {io_data.mqtt_type:io_data.reported}, None,
                            port_id=io_data.mqtt_port)
                    mqtt_topic = self.topic_sensor_pub + '/' + io_data.mqtt_port
                    self.send_to_mqtt(mqtt_topic, mqtt_body)

    def process_rfid_input(self, io_data):
        """ process rfid input """
        now_seconds = self.now_seconds()
        session_id = 'req:'+str(int(now_seconds))
        if io_data.mqtt_port is not None:
                if io_data.reported is not None:
                    io_data.mqtt_timestamp = now_seconds
                    reported_io_data = copy.deepcopy(io_data)
                    print("update reported: "+str(reported_io_data.mqtt_port))
                    self.last_reported[reported_io_data.mqtt_port] = reported_io_data
                    self.log_queue.add_message("info",
                            Global.PUBLISH+" "+Global.RFID+": "+io_data.mqtt_port+" "+str(io_data.reported))
                    mqtt_body = self.format_state_body(self.node_name, Global.SENSOR,
                            session_id, {io_data.mqtt_type:io_data.reported}, None,
                            port_id=io_data.mqtt_port)
                    mqtt_topic = self.topic_sensor_pub + '/' + io_data.mqtt_port
                    self.send_to_mqtt(mqtt_topic, mqtt_body)

    def received_from_i2c(self, io_data):
        """ process i2c input"""
        self.log_queue.add_message("debug", "I2C "+Global.INPUT+" "+Global.RECEIVED+": "+str(io_data))
        if io_data.i2c_type == Global.RFID:
            self.process_rfid_input(io_data)
        elif io_data.i2c_type == Global.ROTARY:
            self.process_rotary_input(io_data)

    def process_fastclock_message(self, _message_topic, _io_data):
        """ process a fastclock message"""
        self.log_queue.add_message("info", Global.RECEIVED+": "+Global.FASTCLOCK)

    def process_inventory_request(self, message_topic, io_data):
        """ process inventory request """
        request_ok = False
        self.log_queue.add_message("info", Global.INVENTORY + " " + Global.MSG_REQUEST_MSG_RECEIVED+ message_topic)
        report_value = io_data.get_desired_value_by_key(Global.REPORT)
        if report_value is not None:
            if report_value == Global.INVENTORY:
                request_ok = True
                inventory_devices = []
                for device in self.i2c_devices:
                    i2c_device = device['dev']
                    if hasattr(i2c_device, 'mqtt_port'):
                        mqtt_port = i2c_device.mqtt_port
                        mqtt_type = i2c_device.mqtt_type
                        i2c_data = {}
                        i2c_data[Global.PORT] = mqtt_port
                        i2c_data[Global.TYPE] = mqtt_type
                        i2c_data[Global.SENSOR] = str(self.topic_sensor_pub)+"/"+str(mqtt_port)
                        if mqtt_port in self.last_reported:
                            i2c_data[Global.REPORTED] = self.last_reported[mqtt_port].mqtt_reported
                            i2c_data[Global.TIMESTAMP] = int(self.last_reported[mqtt_port].mqtt_timestamp)
                        else:
                            i2c_data[Global.REPORTED] = Global.UNKNOWN
                            i2c_data[Global.TIMESTAMP] = 0
                        inventory_devices.append(i2c_data)
                device_inventory = [{Global.TYPE:Global.SENSORS,
                    Global.ITEMS: inventory_devices}]
                mqtt_body = self.format_state_body(self.node_name, Global.REGISTRY,
                        io_data.mqtt_session_id, {Global.REPORT:Global.INVENTORY}, io_data.mqtt_desired,
                        metadata={Global.INVENTORY:device_inventory})
                mqtt_topic = io_data.mqtt_resp_topic
                self.send_to_mqtt(mqtt_topic, mqtt_body)
                request_ok = True
        if not request_ok:
            error_msg = (Global.UNKNOWN + " " +
                    Global.TRACK + " "+ Global.STATE+" : ["+ str(io_data.mqtt_desired)+"]")
            self.publish_error_reponse(error_msg, message_topic, io_data)

    def process_report_node_status(self, message_topic, io_data):
        """ process report node status """
        new_io_data = copy.deepcopy(io_data)
        new_io_data.mqtt_reported = Global.UNKNOWN
        new_io_data.mqtt_type = Global.UNKNOWN
        new_io_data.timestamp = 0
        if new_io_data.mqtt_port in self.last_reported:
            print("%%% not in last reported: "+str(new_io_data.mqtt_port))
            new_io_data.mqtt_reported = self.last_reported[new_io_data.mqtt_port].mqtt_reported
            new_io_data.mqtt_timestamp = int(self.last_reported[new_io_data.mqtt_port].mqtt_timestamp)
        else:
            new_io_data.mqtt_reported  = Global.UNKNOWN
            new_io_data.mqtt_timestamp  = 0
        self.log_queue.add_message("info",
                Global.REPORT+" "+Global.SENSOR+": "+new_io_data.mqtt_port+" "+str(io_data.mqtt_reported))
        mqtt_body = self.format_state_body(self.node_name, Global.SENSOR,
                new_io_data.mqtt_session_id, {new_io_data.mqtt_type: new_io_data.mqtt_reported}, None,
                metadata={Global.TIMESTAMP: int(new_io_data.mqtt_timestamp)},
                port_id=new_io_data.mqtt_port)
        mqtt_topic = new_io_data.mqtt_resp_topic
        self.send_to_mqtt(mqtt_topic, mqtt_body)


    def process_request_message(self, message_topic, io_data):
        """ process a mqtt request"""
        self.log_queue.add_message("info", Global.MSG_REQUEST_MSG_RECEIVED+ message_topic)
        if message_topic != self.topic_broadcast_subscribed:
            # broadcasts handled in parent class, node_mqtt
            message_type_error = True
            if io_data.mqtt_message_root == Global.REGISTRY:
                if io_data.get_desired_value_by_key(Global.REPORT):
                    self.process_inventory_request(message_topic, io_data)
                    message_type_error = False
            elif ((io_data.mqtt_message_root == Global.SENSOR) and
                        (io_data.mqtt_desired == Global.REPORT)):
                self.process_report_node_status(message_topic, io_data)
                message_type_error = False
            if message_type_error:
                self.log_queue.add_message("critical", Global.MSG_UNKNOWN_REQUEST + message_topic)
                self.publish_error_reponse(Global.MSG_UNKNOWN_REQUEST, message_topic, io_data)

    def process_response_message(self, message_topic, _io_data):
        """ process mqtt response """
        self.log_queue.add_message("debug", Global.RECEIVED+": "+Global.RESPONSE+": "+message_topic)

    def received_from_mqtt(self, message_topic, io_data):
        """ process subscribes messages"""
        if message_topic.startswith(Global.CMD):
            if message_topic.endswith("/"+Global.RES):
                self.process_response_message(message_topic, io_data)
            else:
                self.process_request_message(message_topic, io_data)
        elif message_topic.startswith(self.topic_fastclock_subscribed):
            self.process_fastclock_message(message_topic, io_data)

    def loop(self):
        """ main loop"""
        self.log_queue.add_message("critical", Global.READY)
        self.last_ping_seconds = self.now_seconds()
        while not self.shutdown_app:
            try:
                time.sleep(0.1)
                self.write_log_messages()
                self.process_input()
                now_seconds = self.now_seconds()
                if (now_seconds - self.last_ping_seconds) > self.ping_interval:
                    self.publish_ping_broadcast()
            except KeyboardInterrupt:
                self.shutdown_app = True

# this app normally starts at boot, allow time for mqtt-broker to initialize
# time.sleep(30+random.randint(0, 5))
node = MqttSensor()
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
