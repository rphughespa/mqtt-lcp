# node_base_mqtt.py - base class for mqtt nodes
"""

        node_base_mqtt - base class for nodes that use mqtt. Derived from node_base.

The MIT License (MIT)

Copyright 2020 richard p hughes

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

import time
import json
import sys
# platforms for esp32 = esp32, for lobo esp32 = esp32_LoBo, for pi = linux
if sys.platform.startswith('esp32'):
    from queue_esp32 import Queue
else:
    from queue_py import Queue

from node_base import NodeBase
from mqtt_client_thread import MqttClientThread
from io_data import IoData

from global_constants import Global


class NodeBaseMqtt(NodeBase):
    """
        Base class for node programs that uses MQTT messaging
        Manages IO via threads
    """

    def __init__(self):
        super().__init__()
        self.mqtt_client = None
        self.subscribed_topics = {}
        self.publish_topics = {}
        self.other_topics = {}
        self.topic_self_subscribed = None
        self.topic_fastclock_subscribed = None
        self.topic_broadcast_subscribed = None
        self.topic_backup_pub = None
        self.topic_ping_pub = None
        self.topic_sensor_pub = None
        self.powerdown_computer = False
        self.reboot_computer = False
        self.shutdown_command = "sudo halt"
        self.reboot_command = "sudo reboot"
        self.last_ping_seconds = 0
        self.ping_interval = 15
        self.delay = 0
        self.global_data = {}
        self.alt_mqtt_client_name = None
        self.mqtt_in_queue = Queue(100)
        self.mqtt_out_queue = Queue(100)

    def start_mqtt(self, client_name):
        """ Start MQTT IO """
        #print(socket.gethostbyname(socket.gethostname()));
        #print(socket.getfqdn())
        self.mqtt_client = None
        broker = None
        user_name = None
        user_password = None
        if Global.CONFIG in self.config:
            if Global.IO in self.config[Global.CONFIG]:
                if Global.MQTT in self.config[Global.CONFIG][Global.IO]:
                    if Global.BROKER in self.config[Global.CONFIG][Global.IO][Global.MQTT]:
                        broker = self.config[Global.CONFIG][Global.IO][Global.MQTT][Global.BROKER]
                    if Global.USER in self.config[Global.CONFIG][Global.IO][Global.MQTT]:
                        user_name = self.config[Global.CONFIG][Global.IO][Global.MQTT][Global.USER]
                    if Global.PASSWORD in self.config[Global.CONFIG][Global.IO][Global.MQTT]:
                        user_password = self.config[Global.CONFIG][Global.IO][Global.MQTT][Global.PASSWORD]
        if broker is None or user_name is None or user_password is None:
            print("Bad MQTT config")
        self.mqtt_client = MqttClientThread(self.log_queue, self.mqtt_in_queue, self.mqtt_out_queue, broker,
                client_name, user_name, user_password, "MqttThread")
        self.log_queue.add_message("debug", Global.MQTT+' '+Global.START+'..')
        self.mqtt_client.start()
        self.write_log_messages()
        #loop = 0
        #while not self.mqtt_client.is_connected():    #Wait for connection
        #    time.sleep(0.1)
        #    self.write_log_messages()
        #    loop = loop + 1
        #    if loop > 500:
        #        raise OSError
        self.write_log_messages()

    def subscribe_to_topic(self, topic):
        """ subscribe to a topic """
        self.write_log_messages()
        self.mqtt_client.subscribe(topic)   #subscribe

    def unsubscribe_from_topic(self, topic):
        """ unsunscribe to a topic """
        self.write_log_messages()
        self.mqtt_client.unsubscribe(topic)   #unsubscribe

    def parse_mqtt_subscriptions(self):
        """ Subscibe to MQTT topics"""
        # print("parse subs/pubs")
        self.log_queue.add_message("debug", Global.SUBSCRIBE)
        self.write_log_messages()
        time.sleep(5)
        self.subscribed_topics = {}
        if Global.CONFIG in self.config:
            if Global.IO in self.config[Global.CONFIG]:
                if Global.MQTT in self.config[Global.CONFIG][Global.IO]:
                    if Global.SUB_TOPICS in self.config[Global.CONFIG][Global.IO][Global.MQTT]:
                        sub_topics = self.config[Global.CONFIG][Global.IO][Global.MQTT][Global.SUB_TOPICS]
                        for topic in sub_topics:
                            topic_topic_config = topic[Global.TOPIC]
                            topic_topic = topic_topic_config.replace("**"+Global.NODE+"**", self.node_name)
                            self.log_queue.add_message("info", Global.SUBSCRIBE+": "+ topic_topic)
                            self.subscribe_to_topic(topic_topic)
                            topic_text = topic_topic
                            if topic_text.endswith("/+"):
                                topic_text = topic_text.replace("/+", "")
                            if topic_text.endswith("/#"):
                                topic_text = topic_text.replace("/#", "")
                            self.subscribed_topics[topic[Global.ID]] = topic_text
                            if Global.SELF in self.subscribed_topics:
                                self.topic_self_subscribed = self.subscribed_topics[Global.SELF]
                            if Global.FASTCLOCK in  self.subscribed_topics:
                                self.topic_fastclock_subscribed = self.subscribed_topics[Global.FASTCLOCK]
                            if Global.BROADCAST in self.subscribed_topics:
                                self.topic_broadcast_subscribed = self.subscribed_topics[Global.BROADCAST]
                    self.publish_topics = {}
                    if Global.PUB_TOPICS in self.config[Global.CONFIG][Global.IO][Global.MQTT]:
                        pub_topics = self.config[Global.CONFIG][Global.IO][Global.MQTT][Global.PUB_TOPICS]
                        for topic in pub_topics:
                            topic_topic_config = topic[Global.TOPIC]
                            topic_key = topic[Global.ID]
                            topic_topic = topic_topic_config.replace("**"+Global.NODE+"**", self.node_name)
                            self.log_queue.add_message("info", Global.PUBLISH+": "+topic_key+", "+topic_topic)
                            self.publish_topics[topic_key] = topic_topic
                        if Global.PING in  self.publish_topics:
                            self.topic_ping_pub = self.publish_topics[Global.PING]
                        if Global.SENSOR in self.publish_topics:
                            self.topic_sensor_pub = self.publish_topics[Global.SENSOR]
                    self.other_topics = {}
                    if Global.OTHER_TOPICS in self.config[Global.CONFIG][Global.IO][Global.MQTT]:
                        other_topics = self.config[Global.CONFIG][Global.IO][Global.MQTT][Global.OTHER_TOPICS]
                        for topic in other_topics:
                            topic_topic_config = topic[Global.TOPIC]
                            topic_topic = topic_topic_config.replace("**"+Global.NODE+"**", self.node_name)
                            self.log_queue.add_message("debug", Global.OTHER_TOPICS+": "+ topic_topic)
                            self.other_topics[topic[Global.ID]] = topic_topic

    def received_from_mqtt(self, message_topic, io_data):
        """ call back to process received subsctibed messages. override in derived class"""
        pass

    def backup_config_data(self, io_data):
        """ publish back (config data) out as data """
        now_seconds = self.now_seconds()
        session_id = 'dt:'+str(int(now_seconds))
        state_message = self.format_state_body(self.node_name, Global.BACKUP,
                session_id, Global.BACKUP, None, metadata=self.config)
        self.send_to_mqtt(io_data.mqtt_resp_topic, state_message)
        self.log_queue.add_message("info", Global.PUBLISH+": "+Global.BACKUP)
        self.write_log_messages()

    def process_common_broadcasts(self, _message_topic, io_data):
        """ process some common broadcast eg: shutdown, reboot, backup """
        consume_message = False
        # if True, message is consumed at this level and not forwarded
        if io_data.mqtt_message_root == Global.COMMAND:
            if io_data.mqtt_desired == Global.BACKUP:
                consume_message = True
                self.log_queue.add_message("critical",
                    Global.MSG_BACKUP_RECEIVED)
                self.backup_config_data(io_data)
            if io_data.mqtt_desired == Global.SHUTDOWN:
                consume_message = True
                self.log_queue.add_message("critical",
                    Global.MSG_SHUTDOWN_RECEIVED)
                self.shutdown_app = True
                self.powerdown_computer = True
            if io_data.mqtt_desired == Global.REBOOT:
                consume_message = True
                self.log_queue.add_message("critical",
                    Global.MSG_REBOOT_RECEIVED)
                self.shutdown_app = True
                self.reboot_computer = True
        return consume_message

    def process_input(self):
        """ process input from all source input queues"""
        # process all input of a given type in order of importance: keyboard, serial, mqtt
        self.write_log_messages()
        if self.mqtt_client is not None:
            topic = None
            message_body_dict = {}
            next_message = self.get_incomming_mqtt_message_from_queue()
            if next_message is not None:
                body = next_message['body']
                topic = next_message['topic']
                try:
                    message_body_dict = json.loads(body)
                except Exception as _exc:
                    message_body_dict = {}
                    self.log_queue.add_message("error", Global.MSG_ERROR_JSON_PARSE+" "+body)
                    self.write_log_messages()
                consume_message = False
                io_data = IoData()
                io_data.parse_mqtt_mesage_body(message_body_dict)
                if ((topic is not None) and
                        (topic == self.topic_broadcast_subscribed) or
                        (topic.startswith(self.topic_self_subscribed))):
                    consume_message = self.process_common_broadcasts(topic, io_data)
                if not consume_message:
                    self.received_from_mqtt(topic, io_data)

    def publish_ping_broadcast(self):
        """ Publish a ping message to mqtt"""
        now_seconds = self.now_seconds()
        session_id = 'dt:'+str(int(now_seconds))
        self.last_ping_seconds = now_seconds
        if self.topic_ping_pub is not None:
            state_topic = self.topic_ping_pub
            state_message = self.format_state_body(self.node_name, Global.PING,
                    session_id, Global.PING, None)
            self.send_to_mqtt(state_topic, state_message)
            self.log_queue.add_message("debug", Global.PUBLISH+": "+Global.PING)
            self.write_log_messages()

    def get_requested_state(self, _key, _message_body_dict):
        """ placeholder for method in derived call"""
        return(None, None)

    def publish_error_reponse(self, error_message, _message_topic, io_data):
        """ respond with an error message """
        message = self.format_state_body(self.node_name, io_data.mqtt_message_root,
                        io_data.mqtt_session_id, Global.ERROR, io_data.mqtt_desired,
                        metadata={Global.ERROR : error_message})
        if io_data.mqtt_resp_topic is not None:
            self.send_to_mqtt(io_data.mqtt_resp_topic, message)
        self.log_queue.add_message("warn", error_message)
        self.write_log_messages()

    def format_state_body(self, node, message_group,
                session_id, reported_state, desired_state,
                response_topic=None, metadata=None, port_id=None):
        """ for mate a state message body"""
        now_seconds = self.now_seconds()
        #     session_id = 'res:'+str(int(now_seconds))
        state_dict = {message_group: {Global.VERSION: '1.0', Global.TIMESTAMP: int(now_seconds),
                    Global.SESSION_ID : session_id,
                    Global.NODE_ID: node}}
        if port_id is not None:
            state_dict[message_group][Global.PORT_ID] = port_id
        if response_topic is not None:
            state_dict[message_group][Global.RES_TOPIC] = response_topic
        if desired_state is not None and reported_state is not None:
            state_dict[message_group][Global.STATE] = {
                    Global.DESIRED: desired_state, Global.REPORTED: reported_state}
        elif desired_state is not None:
            state_dict[message_group][Global.STATE] = {
                    Global.DESIRED: desired_state}
        elif reported_state is not None:
            state_dict[message_group][Global.STATE] = {
                    Global.REPORTED: reported_state}
        if metadata is not None:
            state_dict[message_group][Global.METADATA] = metadata
        return json.dumps(state_dict)

    def send_to_mqtt(self, new_topic, new_message):
        """ publish an  mqtt message"""
        new_message = {'topic' : new_topic,
            'body' : new_message}
        self.log_queue.add_message("debug", "Queue Publish MQTT: "+str(new_topic)+" ... "+str(new_message))
        # print(new_topic)
        # print(" ... "+str(new_message) )
        self.mqtt_out_queue.put(new_message)

    def get_incomming_mqtt_message_from_queue(self):
        """ retrieve a receieved message from the queue """
        message = None
        if not self.mqtt_in_queue.empty():
            message = self.mqtt_in_queue.get()
        return message

    def initialize_threads(self):
        """ initialize all IO threads"""
        super().initialize_threads()
        if Global.IO in self.config[Global.CONFIG]:
            io_config = self.config[Global.CONFIG][Global.IO]
            if "mqtt" in io_config:
                client_name = self.node_name
                if self.alt_mqtt_client_name is not None:
                    client_name = self.alt_mqtt_client_name
                self.start_mqtt(client_name)
                if self.mqtt_client is not None:
                    self.parse_mqtt_subscriptions()
        if Global.OPTIONS in self.config[Global.CONFIG]:
            if Global.DELAY in self.config[Global.CONFIG][Global.OPTIONS]:
                self.delay = self.config[Global.CONFIG][Global.OPTIONS][Global.DELAY]
            if Global.PING in self.config[Global.CONFIG][Global.OPTIONS]:
                self.ping_interval = self.config[Global.CONFIG][Global.OPTIONS][Global.PING]
            if Global.SHUTDOWN+"-"+Global.COMMAND in self.config[Global.CONFIG][Global.OPTIONS]:
                self.shutdown_command = self.config[Global.CONFIG][Global.OPTIONS][Global.SHUTDOWN+"-"+Global.COMMAND]
            if Global.REBOOT+"-"+Global.COMMAND in self.config[Global.CONFIG][Global.OPTIONS]:
                self.reboot_command = self.config[Global.CONFIG][Global.OPTIONS][Global.REBOOT+"-"+Global.COMMAND]

    def loop(self):
        """ loop through IO.  override in dericed class"""
        while not self.shutdown_app:
            try:
                time.sleep(0.01)
                self.write_log_messages()
                self.process_input()
            except KeyboardInterrupt:
                self.shutdown_app = True

    def shutdown_threads(self):
        """ shutdown all IO threads"""
        if self.mqtt_client is not None:
            # print("shutdown mqtt")
            self.mqtt_client.shutdown()
        super().shutdown_threads()
