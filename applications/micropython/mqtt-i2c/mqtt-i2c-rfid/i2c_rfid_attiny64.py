#!/usr/bin/python3
# ic2_rfid_attiny64.py
"""

I2cRfidAttiny64 - low level hardware driver fot a rdif reader connected to i2c using the attiny64 circuit device


    supports sparkfun qwiic rfid reader; either one more device on same bus or multiple readers connected to a single i2c mux device

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

import time
from global_constants import Global
from utility import Utility
from io_data import IoData
from qwiic_rfid import QwiicRFID

class I2cRfidAttiny64:
    """ Class for an I2C connected RFID device"""

    def __init__(self, i2c_bus=None, io_device=None, node_name=None, pub_topics=None, logger=None):
        """ Initialize """
        self.is_initialized = False
        self.i2c_bus = i2c_bus
        self.node_name = node_name
        self.pub_topics = pub_topics
        self.logger = logger
        self.loco_rfid_map = {}
        self.locator_topic = self.pub_topics.get(Global.LOCATOR, Global.UNKNOWN)
        self.io_device = io_device
        self.rfid_device = QwiicRFID(address = self.io_device.io_address, i2c_driver=self.i2c_bus)
        self.__initialize_device()

    def perform_periodic_operation(self):
        messages = None
        tags_read = self.__read_input()
        if tags_read is not None:
            if messages is None:
                messages = []
            for tag in tags_read:
                if tag is not None and tag != "000000":
                    loco_id = self.loco_rfid_map.get(tag, "???")
                    self.logger.log_line("RFID: "+ str(tag))
                    self.logger.log_line(" ... LOCO: "+ str(loco_id))
                    body = IoData()
                    body.mqtt_port_id = self.io_device.mqtt_port_id
                    body.mqtt_reported = Global.DETECTED
                    body.mqtt_metadata = {Global.TYPE: Global.RFID,
                                             Global.IDENTITY: str(tag)}
                    body.mqtt_loco_id = loco_id
                    body.mqtt_message_root = Global.LOCATOR
                    body.mqtt_node_id = self.node_name
                    body.mqtt_version = "1.0"
                    body.mqtt_timestamp = Utility.now_milliseconds()
                    messages.append((self.locator_topic, body))
        return messages

    def process_response_message(self, msg_body):
        """ received a response """
        if msg_body.mqtt_message_root == Global.ROSTER:
            self.__process_response_roster_message(msg_body)
        else:
            self.logger.log_line("Error: Unxepected response message: "+str(msg_body))
            

#
# private functions
#

    def __process_response_roster_message(self, msg_body):
        """ received registry roster response message """
        self.logger.log_line("Roster response:")
        if msg_body.mqtt_metadata is not None:
            loco_rfid_list = msg_body.mqtt_metadata[Global.RFID]
            for loco_rfid_pair in loco_rfid_list:
                #print("loco: "+str(loco))
                if loco_rfid_pair.get(Global.RFID_ID, None) is not None:
                    #print("loco: "+str(loco))
                    dcc_id = loco_rfid_pair[Global.DCC_ID]
                    rfid = loco_rfid_pair[Global.RFID_ID]
                    #print("rfid: "+str(rfid)+" ... "+str(dcc_id))
                    if rfid is not None and rfid != Global.UNKNOWN:
                        self.logger.log_line("Locos: "+str(dcc_id)+" : "+str(rfid))
                        self.loco_rfid_map.update({str(rfid): dcc_id})

    def __read_input(self):
        """ Read from RFID device """
        rett = None
        # print("read tag from: "+str(io_device.io_config_item.mqtt_port_id))
        tag = self.rfid_device.get_tag()
        time.sleep_ms(100) 
        if tag is not None:
            rett = [tag]
        return rett


    def __initialize_device(self):
        """ initialize the device """
        self.is_initialized = True
        i2c_bus_devices = self.i2c_bus.scan()
        self.logger.log_line("I2C Devices: " + str(i2c_bus_devices))
