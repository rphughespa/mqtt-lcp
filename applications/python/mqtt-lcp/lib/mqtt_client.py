#  mqtt_client - interface to paho.mqtt.client library module

"""
    mqtt_client - Interface to paho.mqtt.client module.
    Intended to run as a thread.  As such, messages to be sent
    or receieved are passed in and out of the module via the thread safe
    python Queue class.

The MIT License (MIT)

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
OUT OFSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import sys
# platforms for esp32 = esp32, for lobo esp32 = esp32_LoBo, for pi = linux
if sys.platform.startswith('esp32'):
    from queue_esp32 import Queue
else:
    from queue_py import Queue

import time
from random import randrange

if sys.platform.startswith("esp32"):
    from umqtt.robust import MQTTClient
else:
    import paho.mqtt.client as mqtt

class MqttClient():
    """ Interface to paho.mqtt.client """

    def __init__(self, log_queue, in_queue, out_queue, broker, node_name, user_name, user_password):
        """ Initialize """
        self.mqtt = None
        self.connected = False
        self.log_queue = log_queue
        self.broker = broker
        self.node_name = node_name
        if self.node_name == "":
            self.node_name = "client-"+str(randrange(1000))
        self.log_queue.add_message("debug", "MQTT Client Name: "+self.node_name)
        self.user_name = user_name
        self.user_password = user_password
        self.mqtt_in_queue = in_queue
        self.mqtt_out_queue = out_queue

    def start(self):
        """ start up the thrread """
        # print("start mqtt client")
        try:
            self.log_queue.add_message("info", "Start MQTT Client")
            self.log_queue.add_message("info", self.broker)

            # esp32 self.mqtt = mqtt.Client(self.node_name)
            # esp32 self.mqtt.username_pw_set(username=self.user_name, password=self.user_password)
            if sys.platform.startswith("esp32"):
                self.mqtt = MQTTClient(self.node_name,
                        self.broker,
                        # cleansession=True,
                        user=self.user_name,
                        password=self.user_password)
                self.log_queue.add_message("info", 'MQTT connecting ...')
                self.mqtt.set_callback(self.data_cb_esp32)
                self.mqtt.connect()
                self.connected = True
            else:
                self.mqtt = mqtt.Client(self.node_name)
                self.mqtt.username_pw_set(username=self.user_name, password=self.user_password)
                self.mqtt.on_message = self.data_cb
                self.mqtt.on_connect = self.connect_cb
                self.mqtt.on_subscribe = self.subscribe_cb
                self.mqtt.on_disconnect = self.disconnect_cb
                self.log_queue.add_message("info", 'MQTT connecting ...')
                # connect to broker
                self.mqtt.connect(self.broker)
                #start the loop
                self.mqtt.loop_start()
                time.sleep(4)
                loop = 0
                while not self.connected:
                    #Wait for connection
                    time.sleep(0.1)
                    loop = loop + 1
                    if loop > 200:
                        raise OSError
            self.log_queue.add_message("info", "Connected to MQTT Broker")
        except OSError as exc:
            self.log_queue.add_message("info", "Error during MQTT init")
            self.log_queue.add_message("info", 'Exception during mqtt init:')
            self.log_queue.add_message("info", str(exc))

    def connect_cb(self, client, userdata, flags, rcode):
        """ callback from paho module called after connection """
        self.log_queue.add_message("debug", 'connect cb: ' +str(rcode))
        if rcode == 0:
            self.log_queue.add_message("info", " ... MQTT Connected...")
            #Signal connection
            self.connected = True

        else:
            self.log_queue.add_message("info", "Connection failed:", str(rcode))
            raise OSError

    def disconnect_cb(self, client, userdata, rcode=0):
        """ callback from paho modile during disconnection """
        self.log_queue.add_message("critical", "DisConnected result code "+str(rcode))
        self.mqtt.loop_stop()

    def subscribe_cb(self, client, userdata, mid, granted_qos):
        """ callback from paho module during subscription """
        time.sleep(1)
        if len(client.topic_ack) == 0:
            self.log_queue.add_message("debug", "All subs acknowledged")
        else:
            self.log_queue.add_message("debug", "on_subscribe error")

    def data_cb(self, client, userdata, message):
        """ callback from paho module. A new message has been received """
        message_body = str(message.payload.decode("utf-8"))
        #print("message received ", message_body)
        #print("message topic=", message.topic)
        #print("message qos=", message.qos)
        #print("message retain flag=", message.retain)
        new_message = {'topic' : message.topic, 'body' : message_body}
        self.mqtt_in_queue.put(new_message)

    def data_cb_esp32(self, topic_binary, message_binary):
        """ data callback in esp32 """
        # print("mqtt data cb")
        topic = topic_binary.decode('utf-8')
        message = message_binary.decode('utf-8')
        # print(">>> "+str(topic) + "<<<>>>"+str(message)+"<<<")
        self.mqtt_in_queue.put({"topic":topic, "body": message})

    def restart_and_reconnect(self):
        """ restart mqtt connection """
        print('Failed to connect to MQTT broker. Reconnecting...')
        time.sleep(10)
        machine.reset()

    def shutdown(self):
        """ sown the thread """
        if self.mqtt is not None:
            self.mqtt.loop_stop()

    def subscribe(self, topic):
        """ subrecibe to a new topic """
        self.log_queue.add_message("debug", "Subscribing to: "+topic)
        self.mqtt.subscribe(topic)

    def unsubscribe(self, topic):
        """ unsubrecibe to a new topic """
        self.log_queue.add_message("debug", "Unsubscribing to: "+topic)
        self.mqtt.unsubscribe(topic)

    def is_connected(self):
        """ return connection status """
        return self.connected

    def send_to_mqtt(self, message):
        """ publish a new message """
        message_topic = message["topic"]
        message_body = message["body"]
        # print(">>>"+message_topic)
        if sys.platform.startswith("esp32"):
            self.mqtt.publish(message_topic, message_body)
        else:
            (rc, _mid) = self.mqtt.publish(message_topic, message_body)
            if rc != 0:
                self.log_queue.add_message("error", "Error Sendng MQTT Message: "
                        +str(rc)+' .. '+message_topic)

    def check_msg(self):
        """ check message """
        if sys.platform.startswith("esp32"):
            self.mqtt.check_msg()
        else:
            pass
