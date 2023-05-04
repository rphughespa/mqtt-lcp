# main.py

"""

    mqtt_i2c_base  for various mqtt i2c apps

    Note: The LED code is very board specific.
    Tested with Raspberry RP2040 Pico W board and an Adafruit QY Py ESP32 Pico.

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
import gc
import time
import json
import machine
import micropython


from global_constants import Global
from global_synonyms import Synonyms
from utility import Utility
from io_data import IoData
from json_utils import JsonUtils
from io_config import IoConfig
from netservices import NetServices
from mqtt_client import MqttClient

from logger_display import LoggerDisplay
from logger_console import LoggerConsole

# uncomment the appropiate board class
# from board_qt_esp32_pico import BoardQtEsp32Pico as Board
from board_rp2040_pico_w import BoardRp2040PicoW as Board

# from config import Config

class MqttI2cBase:
    """ An i2c connected device """

    def __init__(self):
        self.net_services = None
        self.mqtt_client = None
        self.i2c_devices = []
        self.display_device = None
        self.logger = None
        self.pub_topics = {}
        self.sub_topics = {}
        self.config = None
        self.io_config = None
        self.shutdown = False
        self.port_id = "block 10"
        self.node_name = ""
        self.ping_seconds = 10
        self.topic_self_sub =  ""
        self.reversed_globals = self.reverse_globals()
        self.board = Board()
        self.i2c_bus = self.board.i2c_bus

    def led_on(self):
        """ turn on led on board """
        self.board.led_on()

    def led_off(self):
        """ turn off led on board """
        self.board.led_off()

    def led_blink(self, times):
        """ blink led a number of times """
        for _i in range(times):
            self.led_on()
            time.sleep_ms(300)
            self.led_off()
            time.sleep_ms(300)

    def led_blink_fast(self, times):
        """ blink led a number of times """
        for _i in range(times):
            self.led_on()
            time.sleep_ms(50)
            self.led_off()
            time.sleep_ms(50)

    def parse_config(self):
        """ load config.json data """
        gc.collect()
        json_helper = JsonUtils()
        try:
            self.config = json_helper.load_and_parse_file("configure")
        except Exception as exc:
            message = "Exception during JSON parsing, exiting: "\
                + str(exc) + "\n" + str("config") # parse all config file in a folder
            print(message)
        gc.collect()
        self.node_name = self.config[Global.CONFIG][Global.NODE][Global.NAME]
        print("Node Name: "+ self.node_name)
        self.io_config = IoConfig(self.config)
        gc.collect()
        self.io_config.parse_io_configs()
        gc.collect()
        # micropython.mem_info()
        self.io_config.build_port_map()
        gc.collect()
        self.setup_logger(self.io_config)


    def start_network(self):
        """ start network connection """
        self.net_services = NetServices(self.config)
        self.net_services.do_connect()
        self.net_services.start_net_time()

    def start_mqtt(self):
        """ start mqtt connection """

        if self.net_services is not None and self.net_services.is_connected():
            mqtt_config = self.config[Global.CONFIG][Global.IO][Global.MQTT]
            self.ping_seconds = mqtt_config.get("ping", 10)
            self.logger.log_line("MQTT Config: " + str(mqtt_config))
            mqtt_broker = mqtt_config['broker']
            self.logger.log_line("Broker: " + str(mqtt_broker))

            self.mqtt_client = MqttClient(mqtt_broker,
                    self.node_name,
                    mqtt_config['user'],
                    mqtt_config['password'])

            wait_count = 0
            while self.mqtt_client.is_connected() is not True:
                self.logger.log_line('... waiting for mqtt connection')
                time.sleep(1)
                wait_count += 1
                if wait_count > 10:
                    self.logger.log_line('Failed to connect to MQTT broker. Rebooting...')
                    time.sleep(3)
                    machine.reset()
            if self.mqtt_client is not None:
                time.sleep(2)
                self.logger.log_line('... mqtt connected')
                sub_topics = self.config[Global.CONFIG][Global.IO][Global.MQTT][Global.SUB_TOPICS]
                for key, topic in sub_topics.items():
                    self.logger.log_line("Sub: "+str(key) + " ... " + str(topic))
                    topic_topic = topic.replace("**node**", self.node_name)
                    result = self.mqtt_client.subscribe(topic_topic)   #subscribe
                    if result is None or result is True:
                        self.logger.log_line(" ... subscribed to topic: "+str(topic_topic))
                    else:
                        self.logger.log_line(" ... error on subscribing: "+str(topic_topic) + " .." +str(result))
                    if topic_topic.endswith("/+"):
                        topic_topic = topic_topic.replace("/+", "")
                    if topic_topic.endswith("/#"):
                        topic_topic = topic_topic.replace("/#", "")
                    self.sub_topics[key] = topic_topic
                    if key == "self":
                        self.topic_self_sub = topic_topic

                pub_topics = self.config[Global.CONFIG][Global.IO][Global.MQTT][Global.PUB_TOPICS]
                # self.logger.log_line(">>> Pub Topics: "+str(pub_topics))
                for key, topic in pub_topics.items():
                    topic_topic = topic.replace("**node**", self.node_name)
                    self.pub_topics[key] = topic_topic
        self.__parse_io_config()
        gc.collect()

    def start_i2c(self):
        """ start i2c bus and device """
        print("I2C Bus: "+str(self.i2c_bus.scan()))

    def setup_logger(self, _io_config):
        """ setup a logger, console only or console and i2c display """
        for _key, item in self.io_config.io_device_map.items():
            # print(">>> i2c: "+str(item.io_device))
            if item.io_device == Global.DISPLAY and \
                    item.io_address in self.i2c_bus.scan():
                meta = item.io_metadata
                # found an i2c display
                self.logger = LoggerDisplay(self.i2c_bus, item.io_address, meta.get(Global.TYPE, None))
        if self.logger is None:
            self.logger = LoggerConsole()
        self.logger.log_line("Node Starting: "+ self.node_name)
        # time.sleep(2)

    def publish_message(self, topic, body):
        """ publish an mqtt message """
        self.led_on()
        if isinstance(body, IoData):
            encoded_body = body.encode_mqtt_message()
            self.mqtt_client.publish(topic, encoded_body)
        else:
            self.mqtt_client.publish(topic, body)
        self.led_off()

    def publish_data_message(self, topic, msg_body):
        """ publish a data type mqtt message """
        if topic is None:
            self.logger.log_line(
                "base_mqtt: Topic not specified on publish data:\n" +
                str(msg_body.reported))
        now = Utility.now_milliseconds()
        msg_body.mqtt_node_id = self.node_name
        msg_body.mqtt_version = "1.0"
        msg_body.mqtt_timestamp = now
        pub_topic = topic
        port_id = msg_body.mqtt_port_id
        if port_id is not None and not port_id in pub_topic:
            pub_topic = pub_topic + "/" + port_id
        self.publish_message(pub_topic, msg_body)

    def publish_sensor_data_message(self, msg_body):
        """ publish a sensor type data mqtt message """
        pub_topic = self.pub_topics.get(msg_body.mqtt_message_root, None)
        if pub_topic is None:
            pub_topic = self.pub_topics.get(Global.SENSOR, None)
        if pub_topic is not None:
            if msg_body.mqtt_port_id is not None:
                pub_topic += "/" + msg_body.mqtt_port_id
            self.publish_data_message(pub_topic, msg_body)

    def publish_roster_report_request(self, _report_desired):
        """ request roster from dcc_command """
        now = Utility.now_milliseconds()
        topic = self.pub_topics.get(Global.ROSTER, Global.UNKNOWN) + "/req"
        topic_splits = topic.split("/")
        body = IoData()
        if len(topic_splits) > 3:
            body.mqtt_node_id = topic_splits[3]
        else:
            body.mqtt_node_id = self.node_name
        body.mqtt_message_root = Global.ROSTER
        body.mqtt_port_id = Global.RFID
        body.mqtt_desired = Global.REPORT
        body.mqtt_respond_to = self.topic_self_sub + "/res"
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        self.publish_message(topic, body)

    def publish_response_message(self,
                                 reported=None,
                                 metadata=None,
                                 data_reported=None,
                                 message_io_data=None):
        """ format and publish an mqtt response message """
        now = Utility.now_milliseconds()
        topic = message_io_data.mqtt_respond_to
        if topic is not None:
            body = IoData()
            body.mqtt_message_root = message_io_data.mqtt_message_root
            body.mqtt_node_id = self.node_name
            body.mqtt_port_id = message_io_data.mqtt_port_id
            body.mqtt_throttle_id = message_io_data.mqtt_throttle_id
            body.mqtt_cab_id = message_io_data.mqtt_cab_id
            body.mqtt_loco_id = message_io_data.mqtt_loco_id
            body.mqtt_identity = message_io_data.mqtt_identity
            body.mqtt_desired = message_io_data.mqtt_desired
            body.mqtt_reported = Synonyms.desired_to_reported(reported)
            body.mqtt_session_id = message_io_data.mqtt_session_id
            body.mqtt_version = "1.0"
            body.mqtt_metadata = metadata
            body.mqtt_timestamp = now
            self.publish_message(topic, body)
        if data_reported is not None:
            sensor_body = body = IoData()
            sensor_body.mqtt_message_root = message_io_data.mqtt_message_root
            sensor_body.mqtt_node_id = self.node_name
            sensor_body.mqtt_port_id = message_io_data.mqtt_port_id
            sensor_body.mqtt_reported = Synonyms.desired_to_reported(
                data_reported)
            sensor_body.mqtt_version = "1.0"
            sensor_body.mqtt_metadata = metadata
            sensor_body.mqtt_timestamp = now
            self.publish_sensor_data_message(sensor_body)

    def publish_ping_message(self):
        """ publish ping message """
        now = Utility.now_milliseconds()
        # print("Mem: " + str(micropython.mem_info()))
        metadata = {Global.IP_ADDRESS: self.net_services.ip_address}
        topic = self.pub_topics.get(Global.PING,
                    Global.UNKNOWN)
        body = IoData()
        body.mqtt_message_root = Global.PING
        body.mqtt_node_id = self.node_name
        body.mqtt_reported = Global.PING
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        body.mqtt_metadata = metadata
        self.publish_message(topic, body)

    def process_report_inventory(self, msg_body):
        """ process an inventory report request """
        metadata = self.io_config.report_inventory(self.node_name, self.sub_topics, self.pub_topics)
        self.publish_response_message(reported=Global.INVENTORY,
                                      metadata={Global.INVENTORY: metadata},
                                      message_io_data=msg_body)

    def process_request_message(self, _i2c_device, message):
        """ a request message was received """
        self.logger.log_line("Error: Unexpected request message: " + str(message.mqtt_desired))
        return None

    def process_response_message(self, _i2c_device, message):
        """ a response message was received """
        self.logger.log_line("Error: Unexpected response message: " + str(message.mqtt_desired))

    def process_data_message(self, _i2c_device, message):
        """ a data message was received """
        self.logger.log_line("Error: Unexpected data message: " + str(message.mqtt_desired))

    def process_subscribed_messages(self, message_topic, message_body):
        """ parse and process mqtt message received """
        new_message = IoData.parse_mqtt_mesage(topic=message_topic, body=message_body, \
                                        reversed_globals=self.reversed_globals)
        if self.__is_inventory_request(new_message):
            self.process_report_inventory(new_message)
        else:
            for i2c_device in self.i2c_devices:
                if new_message.mqtt_major_category == Global.MQTT_RESPONSE:
                    self.led_on()
                    self.process_response_message(i2c_device, new_message)
                    self.led_off()
                elif new_message.mqtt_major_category == Global.MQTT_DATA:
                    self.led_on()
                    self.process_data_message(i2c_device, new_message)
                    self.led_off()
                else:
                    self.led_on()
                    messages = self.process_request_message(i2c_device, new_message)
                    self.led_off()
                    if messages is not None:
                        for (reported, metadata, data_reported, message_io_data) in messages:
                            self.publish_response_message(reported, metadata, \
                                     data_reported, message_io_data)
                    else:
                        # message not processed, wrong port ID
                        err_msg = "Unknown Port Id: " + str(new_message.mqtt_port_id)
                        self.logger.log_line(err_msg)
                        self.publish_response_message(Global.ERROR, {Global.MESSAGE: err_msg}, \
                                                                     None, new_message)

    def process_periodic_operations(self, _now):
        """ do periodic operation on the i2c device """
        for i2c_device in self.i2c_devices:
            messages = None
            if i2c_device is not None:
                messages = i2c_device.perform_periodic_operation()
            if messages is not None:
                for (topic, body) in messages:
                    self.publish_data_message(topic, body)

    def reverse_globals(self):
        """ generate a reversed list of globals """
        return Global.generate_reversed_list()

    def perform_initial_operations(self):
        """ perform initial one-time operation at startup """
        pass

    def main_loop(self):
        """ main i2c devicce processing loop """
        gc.collect()
        gc_count = 0
        last_ping_seconds = int(time.mktime(time.localtime()))
        self.led_blink(5)
        self.perform_initial_operations()
        self.logger.log_line("Running...")
        self.led_blink_fast(10)
        gc.collect()
        while True:
            # gc.collect()
            # time.sleep(2)
            time.sleep_ms(50)
            now_seconds = int(time.mktime(time.localtime()))
            self.mqtt_client.check_msg()
            next_message = self.mqtt_client.get_next_message()
            if next_message is not None:
                self.process_subscribed_messages(next_message['topic'], next_message['body'])
            self.process_periodic_operations(now_seconds)
            if (now_seconds - last_ping_seconds) > self.ping_seconds:
                self.publish_ping_message()
                last_ping_seconds = now_seconds
            gc_count += 1
            if gc_count > 10:
                gc.collect()
                gc_count = 0

    def is_device_correct_type(self, _item):
        """ is device type ok"""
        # override in derived class
        return False

#
# private functions
#
    def __is_device_display(self, item):
        """ determine if an io_config item is a display """
        rett = False
        if item.io_device_type == Global.DISPLAY:
            rett = True
        return rett

    def __is_inventory_request(self, message):
        """ check if message is inventory request """
        is_inventory = False
        if message.mqtt_major_category == Global.MQTT_REQUEST and \
                message.mqtt_message_root == Global.TOWER:
            if message.mqtt_port_id == Global.INVENTORY and \
                    message.mqtt_desired == Global.REPORT:
                is_inventory = True
        return(is_inventory)

    def __parse_io_config(self):
        """ parse out info from io device in map """
        i2c_devices_found = self.i2c_bus.scan()
        for key, item in self.io_config.io_device_map.items():
            print("io dev config: " + str(key) + \
                  " , type: " + str(item.io_device_type) + \
                  " , address: " + str(item.io_address) + \
                  " , mux: " + str(item.io_mux_address) + \
                  " , sub: " + str(item.io_sub_address) + \
                  " , port: " + str(item.mqtt_port_id))
            if self.is_device_correct_type(item):
                if item.io_address != 0 and item.io_address not in i2c_devices_found:
                    print("I2C Device not active: "+str(item.io_address))
                else:
                    new_device = self.create_new_device(item)
                    self.i2c_devices.append(new_device)
            elif not self.__is_device_display(item):
                print("Error: device configured is not correct type: " + str(item.io_device_type))


