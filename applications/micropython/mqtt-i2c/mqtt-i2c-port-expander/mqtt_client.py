#  mqtt_client
import sys
sys.path[1] = '../lib'


# import utime
from ucollections import deque

from umqtt_simple import MQTTClient

class MqttClient:

    def __init__(self, broker, node_name, user_name, user_password):
        """ mqtt client:"""
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
        print('Failed to connect to MQTT broker. Reconnecting...')
        time.sleep(3)
        machine.reset()

    def subscribe(self, topic_sub):
        """ subscrive to an mqtt topic """
        self.mqtt.subscribe(topic_sub)

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
