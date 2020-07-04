# mqtt_client_thread - thread to manage a mqtt-client connection

"""

    mqtt_client_thread: Executes the mqtt-client as a python thread



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
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import sys
# platforms for esp32 = esp32, for lobo esp32 = esp32_LoBo, for pi = linux
if sys.platform.startswith("esp32_LoBo"):
    from queue_esp32 import Queue
    from threading_lobo import Thread
    import _thread
    from mqtt_client_lobo import MqttClient
elif sys.platform.startswith("esp32"):
    from threading_esp32 import Thread
    from queue_esp32 import Queue
    from mqtt_client import MqttClient
else:
    from threading import Thread
    from queue_py import Queue
    from mqtt_client import MqttClient


import time


BUFFER_LENGTH = 4096


class MqttClientThread(Thread):
    """ Run mqtt-client as a thread """

    def __init__(self, log_queue, in_queue, out_queue, broker, node_name, user_name, user_password, thread_name):
        # initialize
        Thread.__init__(self)
        self.broker = broker
        self.node_name = node_name
        self.thread_name = thread_name
        self.user_name = user_name
        self.user_password = user_password
        self.mqtt_client = None
        self.mqtt_client_thread = None
        self.mqtt_out_queue = out_queue
        self.mqtt_in_queue = in_queue
        self.log_queue = log_queue
        self.exit = False
        if sys.platform.startswith("esp32_LoBo"):
            self.loop_thread_id = None

    def run(self):
        """ execute the thread """
        self.log_queue.add_message("debug", 'MQTTClient starting connection..')
        self.mqtt_client = MqttClient(self.log_queue, self.mqtt_in_queue, self.mqtt_out_queue, self.broker,
                self.node_name, self.user_name, self.user_password)
        if self.mqtt_client is None:
            print("ERROR MQTT not initialized")
        #print("before start mqtt_client")
        self.mqtt_client.start()
        if sys.platform.startswith("esp32_LoBo"):
            loop = 0
            while not self.mqtt_client.connected and loop < 30:
                loop += 1
                print('... waiting for mqtt connection, '+str(loop))
                time.sleep(1)
            if self.mqtt_client.connected:
                print('MQTT Connected')
            else:
                print('MQTT Connection Failed !!!')
            #print("after start mqtt client")
            time.sleep(0.5)
            self.log_queue.add_message("info", 'Starting Mqtt Client Thread...')
            # on lobo micropython the only threaded function is mqtt_send_loop,
            # not the entrie class
            self.loop_thread_id = _thread.start_new_thread("mqtt_send_loop", self.mqtt_send_loop, ())
        else:
            #print("after start mqtt client")
            time.sleep(2.0)
            self.log_queue.add_message("info", 'Starting Mqtt Client Thread...')
            while not self.exit:
                self.send_one_message()
                time.sleep(0.1)

    # threading is different in lobo micropython
    def mqtt_send_loop(self):
        """ send mqtt loop """
        # threading is different in lobo micropython
        if sys.platform.startswith("esp32_LoBo"):
            _thread.allowsuspend(True)
            while True:
                ntf = _thread.getnotification()
                if ntf:
                    # some notification received
                    if ntf == _thread.EXIT:
                        return
                self.send_one_message()
                time.sleep(0.1)
        else:
            pass

    def send_one_message(self):
        """ send on emessage """
        message = None
        if self.mqtt_client is not None:
            self.mqtt_client.check_msg()
            if not self.mqtt_client.mqtt_out_queue.empty():
                message = self.mqtt_client.mqtt_out_queue.get()
                self.mqtt_client.send_to_mqtt(message)

    def shutdown(self):
        """ shutdown the thread """
        self.log_queue.add_message("info", "Exiting Mqtt Client Thread")
        if sys.platform.startswith("esp32_LoBo"):
            if self.loop_thread_id is not None:
                _thread.stop(self.loop_thread_id)
        self.mqtt_client.shutdown()
        self.exit = True
        if sys.platform.startswith("esp32"):
            self.mqtt_client_thread.exit()
        self.join()

    def is_connected(self):
        """ Test if connected to mqtt broker """
        status = False
        if self.mqtt_client is not None:
            status = self.mqtt_client.is_connected()
        return status

    def subscribe(self, topic):
        """ subscribe to a new topic """
        self.mqtt_client.subscribe(topic)

    def unsubscribe(self, topic):
        """ subscribe to a new topic """
        self.mqtt_client.unsubscribe(topic)
