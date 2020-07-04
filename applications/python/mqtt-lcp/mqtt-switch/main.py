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
import copy

# platforms for esp32 = esp32, for lobo esp32 = esp32_LoBo, for pi = linux
if sys.platform.startswith('esp32'):
    from queue_esp32 import Queue
else:
    from queue_py import Queue

from global_constants import Global
from local_constants import Local
from io_data import IoData
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
        now_seconds = self.now_seconds()
        self.topic_sensor_pub = self.publish_topics[Global.SENSOR]
        for device in self.i2c_devices:
            i2c_device = device['dev']
            if hasattr(i2c_device, 'mqtt_port'):
                if i2c_device.mqtt_send_sensor_msg is True:
                    i2c_data = IoData()
                    i2c_data.mqtt_port = i2c_device.mqtt_port
                    i2c_data.mqtt_reported = Global.UNKNOWN
                    i2c_data.mqtt_timestamp = 0
                    self.last_reported[i2c_data.mqtt_port] = i2c_data

    def send_data_message(self, io_data):
        """ send a data message """
        #send data message
        now_seconds = self.now_seconds()
        io_data.timestamp = now_seconds
        self.last_reported[io_data.mqtt_port] = io_data
        if io_data.mqtt_data_topic is not None:
            session_id = 'dt:'+str(int(now_seconds))
            state_message = self.format_state_body(self.node_name,
                    io_data.mqtt_data_type,
                    session_id,
                    io_data.mqtt_reported,
                    None,
                    response_topic=None,
                    # metadata=meta,
                    port_id=io_data.mqtt_port)
            self.send_to_mqtt(io_data.mqtt_data_topic, state_message)

    def process_switch_input(self, io_data):
        """ Process a switch input """
        self.log_queue.add_message("debug", Local.MSG_NEW_SWITCH+io_data.mqtt_reported)
        if io_data.mqtt_resp_topic is not None:
            state_message = self.format_state_body(self.node_name,
                    io_data.mqtt_type,
                    io_data.mqtt_session_id,
                    io_data.mqtt_reported,
                    io_data.mqtt_desired,
                    response_topic=None,
                    # metadata=meta,
                    port_id=io_data.mqtt_port)
            # print("response: "+str(state_message))
            self.send_to_mqtt(io_data.mqtt_resp_topic, state_message)
        if io_data.mqtt_send_sensor_msg is True:   # send a sensor msg with response msg
            self.send_data_message(io_data)
        else:
            del self.last_reported[io_data.mqtt_port]  # another node will report state


    def process_inventory_request(self, message_topic, io_data):
        """ process inventory request """
        request_ok = False
        self.log_queue.add_message("info", Global.SENSOR + " " + Global.MSG_REQUEST_MSG_RECEIVED+ message_topic)
        report_value = io_data.get_desired_value_by_key(Global.REPORT)
        if report_value is not None:
            if report_value == Global.INVENTORY:
                request_ok = True
                inventory_switches = []
                inventory_sensors = []
                for device in self.i2c_devices:
                    if device['type'] == Global.SERVO:
                        servo = device['dev']
                        if hasattr(servo, 'mqtt_port'):
                            mqtt_port = servo.mqtt_port
                            mqtt_type = servo.mqtt_type
                            i2c_data = {}
                            i2c_data[Global.PORT] = mqtt_port
                            i2c_data[Global.TYPE] = mqtt_type
                            i2c_data[Global.REPORTED] = Global.UNKNOWN
                            i2c_data[Global.TIMESTAMP] = 0
                            # print(">>>"+str(mqtt_port))
                            inventory_switches.append(i2c_data)
                            if servo.mqtt_send_sensor_msg is True:
                                i2c_data[Global.SENSOR] = str(self.topic_sensor_pub)+"/"+mqtt_port
                                if mqtt_port in self.last_reported:
                                    i2c_data[Global.REPORTED] = self.last_reported[mqtt_port].mqtt_reported
                                    i2c_data[Global.TIMESTAMP] = int(self.last_reported[mqtt_port].mqtt_timestamp)
                                inventory_sensors.append(i2c_data)
                if len(inventory_sensors) > 0:
                    device_inventory = [{Global.TYPE:Global.SWITCH,
                            Global.ITEMS: inventory_switches},
                                {Global.TYPE:Global.SENSOR, Global.ITEMS: inventory_sensors}]
                else:
                    device_inventory = [{Global.TYPE:Global.SWITCH,
                            Global.ITEMS: inventory_switches}]
                mqtt_body = self.format_state_body(self.node_name, Global.REGISTRY,
                        io_data.mqtt_session_id, {Global.REPORT:Global.INVENTORY}, io_data.mqtt_desired,
                        metadata={Global.INVENTORY:device_inventory})
                mqtt_topic = io_data.mqtt_resp_topic
                self.send_to_mqtt(mqtt_topic, mqtt_body)
                request_ok = True
        if not request_ok:
            error_msg = (Global.UNKNOWN + " " +
                    Global.TRACK + " "+ Global.STATE+" : ["+ str(io_data.desired)+"]")
            self.publish_error_reponse(error_msg, message_topic, io_data)

    def process_switch_request(self, _message_topic, io_data):
        """ Process a request to move a swich """
        self.log_queue.add_message("debug", "switch id: "+ io_data.mqtt_port+", "+io_data.mqtt_desired)
        new_io_data = copy.deepcopy(io_data)
        i2c_device = None
        mqtt_key = new_io_data.mqtt_port +":"+ Global.SWITCH
        if mqtt_key in self.mqtt_devices:
            i2c_device = self.mqtt_devices[mqtt_key]
        new_io_data.io_type = Global.SWITCH
        new_io_data.mqtt_type = io_data.mqtt_message_root
        new_io_data.mqtt_reported = Global.UNKNOWN
        if i2c_device is not None:
            new_io_data.mqtt_send_sensor_msg = i2c_device.mqtt_send_sensor_msg  # send sensor msg along with response msg
        new_io_data.mqtt_data_topic = self.topic_sensor_pub + "/" +  new_io_data.mqtt_port
        new_io_data.mqtt_data_type = Global.SENSOR
        self.send_to_i2c({'type':new_io_data.mqtt_message_root, 'message':new_io_data})
        data_io_data = copy.deepcopy(new_io_data)
        data_io_data.reported = Global.INCONSISTENT
        self.send_data_message(data_io_data)

    def process_report_node_status(self, message_topic, io_data):
        """ process report node status """
        topic_parts = message_topic.split("/")
        mqtt_port = topic_parts[-2] # next to last item in list
        new_io_data = copy.deepcopy(io_data)
        new_io_data.mqtt_reported = Global.UNKNOWN
        new_io_data.mqtt_type = Global.UNKNOWN
        new_io_data.mqtt_port = mqtt_port
        new_io_data.timestamp = 0
        if mqtt_port in self.last_reported:
            new_io_data.mqtt_reported = self.last_reported[mqtt_port]
        self.log_queue.add_message("info",
                Global.REPORT+" "+Global.SENSOR+": "+new_io_data.mqtt_port+" "+str(io_data.reported))
        mqtt_body = self.format_state_body(self.node_name, Global.SENSOR,
                new_io_data.session_id, {new_io_data.mqtt_type:new_io_data.mqtt_reported}, None,
                metadata={Global.TIMESTAMP: int(new_io_data.timestamp)},
                port_id=new_io_data.mqtt_port)
        mqtt_topic = new_io_data.res_topic
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
            elif io_data.mqtt_message_root == Global.SWITCH:
                self.process_switch_request(message_topic, io_data)
                message_type_error = False
            if message_type_error:
                self.log_queue.add_message("critical", Global.MSG_UNKNOWN_REQUEST + message_topic)
                self.publish_error_reponse(Global.MSG_UNKNOWN_REQUEST, message_topic, io_data)

    def process_response_message(self, message_topic, _io_data):
        """ process mqtt response """
        self.log_queue.add_message("debug", "response message recvd: "+ message_topic)

    def received_from_i2c(self, io_data):
        """ process i2c input"""
        self.log_queue.add_message("debug", Global.MSG_I2C_DATA_RECEIVED+str(io_data))
        if io_data.io_type == Global.SWITCH:
            self.process_switch_input(io_data)

    def received_from_mqtt(self, message_topic, io_data):
        """ process subscribes messages"""
        if message_topic.startswith(Global.CMD):
            if message_topic.endswith("/"+Global.RES):
                self.process_response_message(message_topic, io_data)
            else:
                self.process_request_message(message_topic, io_data)
        # elif message_topic.startswith(self.topic_state_switch_sub):
        #   self.process_state_switch_message(message_topic, message_body)


    def loop(self):
        """ main loop"""
        self.log_queue.add_message("critical", Global.READY)
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

node.loop()

end_seconds = node.now_seconds()
node.log_queue.add_message("critical", node.node_name+" "+Global.MSG_COMPLETED)
node.log_queue.add_message("critical", node.node_name+" "+Global.MSG_EXITING)
node.write_log_messages()
node.shutdown_threads()
node.write_log_messages()
sys.exit(0)
