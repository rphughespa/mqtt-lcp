#!/usr/bin/python3
# mqtt_process.py
"""

        mqtt_process - process class for mqtt_messaging.


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
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import sys

sys.path.append('../../lib')

import time
from random import randrange

import json

import paho.mqtt.client as mqtt

# mqtt error codes

MQTT_ERR_AGAIN = -1
MQTT_ERR_SUCCESS = 0
MQTT_ERR_NOMEM = 1
MQTT_ERR_PROTOCOL = 2
MQTT_ERR_INVAL = 3
MQTT_ERR_NO_CONN = 4
MQTT_ERR_CONN_REFUSED = 5
MQTT_ERR_NOT_FOUND = 6
MQTT_ERR_CONN_LOST = 7
MQTT_ERR_TLS = 8
MQTT_ERR_PAYLOAD_SIZE = 9
MQTT_ERR_NOT_SUPPORTED = 10
MQTT_ERR_AUTH = 11
MQTT_ERR_ACL_DENIED = 12
MQTT_ERR_UNKNOWN = 13
MQTT_ERR_ERRNO = 14
MQTT_ERR_QUEUE_SIZE = 15

from structs.io_data import IoData
from structs.mqtt_config import MqttConfig
from utils.global_constants import Global

from processes.base_process import BaseProcess


class MqttProcess(BaseProcess):
    """ interface to mqtt broker """
    def __init__(self, events=None, queues=None):
        BaseProcess.__init__(self,
                             name="mqtt",
                             events=events,
                             in_queue=queues[Global.MQTT],
                             app_queue=queues[Global.APPLICATION],
                             log_queue=queues[Global.LOGGER])
        self.delay = 0
        self.global_data = {}
        self.alt_mqtt_client_name = None
        self.mqtt_client = None
        self.connected = False
        self.mqtt_config = None

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        self.__start_mqtt_process()

    def shutdown_process(self):
        """ shutdown the process """
        self.__shutdown_mqtt_client()

    def process_message(self, new_message=None):
        """ process messages from in queue """
        #  mqtt: " + str(new_message))
        (message_type, message) = new_message
        if message_type == Global.MQTT_PUBLISH_JSON:
            # message body is already in JSON format
            (topic, message_body) = message
            payload = json.dumps(message_body)
            self.__send_to_mqtt(topic, payload)
        elif message_type == Global.MQTT_PUBLISH_IODATA:
            # message body id iodata instance
            (topic, message_body) = message
            payload = message_body.encode_mqtt_message()
            self.__send_to_mqtt(topic, payload)
        elif message_type == Global.MQTT_SUBSCRIBE:
            self.__subscribe_to_topic(message)
        elif message_type == Global.MQTT_UNSUBSCRIBE:
            self.__unsubscribe_from_topic(message)
        else:
            self.log_error(self.name + ": Unknown message type: " +
                           str(message_type) + " .:. " + str(message))

    def process_other(self):
        """ proceesses not related to messages to in_queue """
        pass



    #
    # privarte functions
    #

    def __start_mqtt_process(self):
        """ Start MQTT IO """
        self.mqtt_client = None
        self.mqtt_config = MqttConfig(self.config, self.node_name,
                                      self.host_name, self.log_queue)
        self.node_name = self.mqtt_config.node_name

        if self.mqtt_config.broker is None or self.mqtt_config.user_name is None or\
                self.mqtt_config.user_password is None or self.node_name is None:
            print("!!! Bad MQTT config")
        else:
            self.__start_mqtt_client()
        if self.log_level == Global.LOG_LEVEL_DEBUG:
            self.log_debug(Global.MQTT + ' ' + Global.START + '..')

    def __start_mqtt_client(self):
        """ start up the paho mqtt client """
        try:
            if self.node_name == "":
                super().node_name = "client-" + str(randrange(1000))
            self.log_info("Start MQTT Client")
            self.log_info(" ... Broker: " + self.mqtt_config.broker)
            self.log_info(" ... Node: " + self.node_name)
            self.mqtt_client = mqtt.Client(self.node_name)
            self.mqtt_client.username_pw_set(
                username=self.mqtt_config.user_name,
                password=self.mqtt_config.user_password)
            self.mqtt_client.on_message = self.data_cb
            self.mqtt_client.on_connect = self.connect_cb
            self.mqtt_client.on_subscribe = self.subscribe_cb
            self.mqtt_client.on_disconnect = self.disconnect_cb
            self.log_info('connecting ...')
            # connect to broker
            self.mqtt_client.connect(self.mqtt_config.broker)
            # start the loop
            self.mqtt_client.loop_start()
            time.sleep(4)
            loop = 0
            while not self.connected:
                # Wait for connection
                time.sleep(0.1)
                loop = loop + 1
                if loop > 200:
                    raise OSError(" Timeout on connection")
            self.log_info("Connected to MQTT Broker")
        except OSError as exc:
            self.log_info("Error during MQTT init")
            self.log_info("Exception during mqtt init:")
            self.log_info(str(exc))

    def connect_cb(self, client, userdata, flags, rcode):
        """ callback from paho module called after connection """
        if self.log_level == Global.LOG_LEVEL_DEBUG:
            self.log_debug('connect cb: ' + str(rcode))
        if rcode == 0:
            self.log_info("... MQTT Connected...")
            # Signal connection
            self.connected = True
        else:
            self.log_critical("Connection failed: " + str(rcode))
            # raise OSError("MQTT Connettion Failed")
            self.log_critical("Reconnecting ...")
            time.sleep(3)
            self.close()

    def disconnect_cb(self, client, userdata, rcode=0):
        """ callback from paho modile during disconnection """
        if not self.events[Global.SHUTDOWN].is_set():
            # raise OSError("MQTT Connettion Failed")
            self.log_critical("DisConnected result code " + str(rcode))
            self.log_critical("Reconnecting ...")
            time.sleep(3)
            self.close()
        else:
            self.mqtt_client.loop_stop()

    def subscribe_cb(self, client, userdata, mid, granted_qos):
        """ callback from paho module during subscription """
        if self.log_level == Global.LOG_LEVEL_DEBUG:
            self.log_debug("Subsription acknowledged")

    def data_cb(self, client, userdata, message):
        """ callback from paho module. A new message has been received """
        payload = str(message.payload.decode("utf-8"))
        # print("message received ", payloady)
        # print("message topic=", message.topic)
        # print("message qos=", message.qos)
        # print("message retain flag=", message.retain)
        new_message = IoData.parse_mqtt_mesage(message.topic, payload,
                                               self.reversed_globals)
        self.send_to_application((Global.MQTT_MESSAGE, new_message))

    def restart_and_reconnect(self):
        """ restart mqtt connection """
        print("Failed to connect to MQTT broker. Reconnecting...")
        time.sleep(10)

    def __shutdown_mqtt_client(self):
        """ stop the mqtt client """
        if self.mqtt_client is not None:
            self.mqtt_client.loop_stop()

    def __subscribe_to_topic(self, topic=None):
        """ subrecibe to a new topic """
        self.log_info("Subscribing to: " + topic)
        self.mqtt_client.subscribe(topic)

    def __unsubscribe_from_topic(self, topic=None):
        """ unsubrecibe to a new topic """
        self.log_info("Unsubscribing to: " + topic)
        self.mqtt_client.unsubscribe(topic)

    #def __is_connected(self):
    #    """ return connection status """
    #    return self.connected

    def __send_to_mqtt(self, topic=None, payload=None):
        """ publish a new message """
        # print(">>>"+message_topic)
        (rc, _mid) = self.mqtt_client.publish(topic=topic, payload=payload)
        if rc == MQTT_ERR_NO_CONN:
            self.log_error("Error Sendng MQTT Message: MQTT_ERR_NO_CONN: " +
                           str(rc) + ' .. ' + topic)
        elif rc != 0:
            self.log_error("Error Sendng MQTT Message: " + str(rc) + ' .. ' +
                           topic)
