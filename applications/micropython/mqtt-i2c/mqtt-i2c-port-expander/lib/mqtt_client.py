#  mqtt_client
"""
MqttClient - interface to mqtt broker

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
sys.path[1] = '../lib'


# import utime
import time
import machine
from ucollections import deque

from umqtt_robust import MQTTClient

class MqttClient:
    """ an mqtt client """
    def __init__(self, broker, node_name, user_name, user_password):
        """ initialize mqtt client:"""
        self.connected = False
        self.queue = deque((), 64)
        try:
            print( "Start MQTT Client")
            print( " ... "+str(broker))
            print("MQTT: Connecting to broker: " + str(broker))
            self.mqtt = MQTTClient(b'node_name',
                    broker,
                    # cleansession=True,
                    user=user_name,
                    password=user_password)
            self.mqtt.set_callback(self.datacb)
            self.mqtt.connect()
            self.connected = True
            print('Connected to MQTT broker')
        except OSError as exc:
            print("!!! MQTT Error", "Error during MQTT init")
            print("!!! MQTT Error", exc.args[0])
            print("Error during MQTT init")
            print(exc.args[0])

    def check_msg(self):
        """ non blocking call to mqtt driver to check for new message arrivals"""
        self.mqtt.check_msg()

    def datacb(self, topic_binary, message_binary):
        """ called when new mqtt message has been received"""
        topic = topic_binary.decode('utf-8')
        message = message_binary.decode('utf-8')
        # print(topic, message)
        self.queue.append({"topic":topic, "body": message})

    def restart_and_reconnect(self):
        """ restart mqtt and attempt to reconnect"""
        print('Failed to connect to MQTT broker. Rebooting...')
        time.sleep(3)
        machine.reset()

    def subscribe(self, topic_sub):
        """ subscrive to an mqtt topic """
        self.mqtt.subscribe(topic_sub)
        return True

    def is_connected(self):
        """ is mqtt broker connected """
        return self.connected

    def get_next_message(self):
        """ get next mqtt message from in queue"""
        message = None
        try:
            message = self.queue.popleft()
        except IndexError:
            pass
        return message

    def publish(self, topic, body):
        """ publish an mqtt message """
        self.mqtt.publish(topic,body)
