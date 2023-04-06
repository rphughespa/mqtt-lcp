# main.py

"""

    main.py for MqttI2cRfid - interface an i2c based rfid board with mqtt messaging

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
import machine,sys
import time,json
import gc

from global_constants import Global
from global_synonyms import Synonyms
from utility import Utility
from io_data import IoData
from mqtt_i2c_base import MqttI2cBase
from i2c_encoder import I2cEncoder
gc.collect()

class MqttI2cRfid(MqttI2cBase):
    """ An i2c connected device """

    def __init__(main_process):
        super().__init__()


    def is_device_correct_type(main_process, item):
        """ is config device correct type """
        rett = False
        meta_rfid = None
        if item.io_metadata is not None:
            # print("meta: "+str(item.io_metadata))
            meta_rfid = item.io_metadata.get(Global.TYPE, None)
        if item.io_device_type == Global.SENSOR and \
                item.io_device == Global.ENCODER:
            rett = True
            print(">>> dev: "+str(item.io_device)+" : "+str(item.io_device_type)+ \
                  " : "+str(rett))
        return rett

    def create_new_device(main_process, device_item):
        """ instantiate a instance of device class """
        device = I2cEncoder(i2c_bus=main_process.i2c_bus, \
                                io_device=device_item, \
                                node_name=main_process.node_name, \
                                pub_topics=main_process.pub_topics,\
                                logger=main_process.logger)
        return device

    def start_i2c(main_process):
        """ start i2c bus and device """
        super().start_i2c()

    def perform_initial_operations(self):
        """ perform initial one-time operation at startup """
        super().perform_initial_operations()
        self.publish_roster_report_request(Global.ROSTER)

    def process_data_message(self, i2c_device, message):
        """ process a received data message """
        if message.mqtt_message_root == Global.ROSTER and \
               message.mqtt_port_id == Global.ROSTER and \
               message.mqtt_reported == Global.CHANGED:
            self.publish_roster_report_request(Global.REPORT)
            self.logger.log_line("data message recvd: "+ message.mqtt_message_root)
        else:
            self.logger.log_line("Error: Unexpected data message: " + str(message.mqtt_desired))

    def process_response_message(self, i2c_device, message):
        """ a response message was received """
        self.logger.log_line("response message recvd: "+ message.mqtt_message_root)
        i2c_device.process_response_message(message)

    def process_request_message(self, i2c_device, message):
        """ process a request message """
        rett = i2c_device.process_request_message(message)
        return rett

time.sleep(2)

print("In Main...")

main_process = MqttI2cRfid()

start_ok = False
main_process.led_blink_fast(3)
main_process.parse_config()
main_process.led_blink(1)
if main_process.config is not None:
    main_process.start_network()
main_process.led_blink(2)
if main_process.net_services is not None:
    main_process.start_mqtt()
main_process.led_blink(3)
if main_process.mqtt_client is not None:
    main_process.start_i2c()
main_process.led_blink(4)
if len(main_process.i2c_devices) > 0:
    start_ok = True
main_process.led_blink(5)

if start_ok == False:
    print("Error: Initialization failed")
    print("Rebooting ...")
    main_process.led_blink(6)
    time.sleep(1)
    main_process.led_blink_fast(20)
    machine.reset()
    # sys.exit()
else:
    main_process.main_loop()

print("Exiting")


