# io_data.py

"""

    IoData - class that is used when passing i2c io data between modules

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

from global_constants import Global

class IoData():
    """ Data structure used to store i2c device data """

    def __init__(self):
        """ Initialize """
        self.io_type = None
        self.io_address = None
        self.io_sub_address = None
        self.io_device_type = None
        self.mqtt_message_root = None
        self.mqtt_node = None
        self.mqtt_port = None
        self.mqtt_type = None
        self.mqtt_send_sensor_msg = False  # send sensor message if messaging for a switch
        self.mqtt_desired = None
        self.mqtt_reported = None
        self.mqtt_resp_topic = None
        self.mqtt_session_id = None
        self.mqtt_data_topic = None
        self.mqtt_data_type = None
        self.mqtt_timestamp = None
        self.mqtt_metadata = None


    def parse_mqtt_mesage_body(self, message_body_dict):
        """ parse a mqtt message body dictionary """
        if message_body_dict is not None:
            self.mqtt_message_root = list(message_body_dict.keys())[0] # get root key of dict
            message_body = message_body_dict[self.mqtt_message_root]
            if Global.NODE_ID in message_body:
                self.mqtt_node = message_body[Global.NODE_ID]
            if Global.PORT_ID in message_body:
                self.mqtt_port = message_body[Global.PORT_ID]
            if Global.SESSION_ID in message_body:
                self.mqtt_session_id = message_body[Global.SESSION_ID]
            if Global.TIMESTAMP in message_body:
                self.mqtt_timestamp = message_body[Global.TIMESTAMP]
            if Global.RES_TOPIC in message_body:
                self.mqtt_resp_topic = message_body[Global.RES_TOPIC]
            if Global.METADATA in message_body:
                self.mqtt_metadata = message_body[Global.METADATA]
                if isinstance(self.mqtt_metadata, dict):
                    if Global.TYPE in self.mqtt_metadata:
                        self.mqtt_type = self.mqtt_metadata[Global.TYPE]
            if Global.STATE in message_body:
                if Global.DESIRED in message_body[Global.STATE]:
                    self.mqtt_desired = message_body[Global.STATE][Global.DESIRED]
                if Global.REPORTED in message_body[Global.STATE]:
                    self.mqtt_reported = message_body[Global.STATE][Global.REPORTED]


    def parse_state(self):
        """ get the state requested """
        key = None
        value = None
        key = list(self.mqtt_desired.keys())[0]
        value = self.mqtt_desired[key]
        return key, value

    def get_desired_value_by_key(self, key):
        """ get sub value in desire dictionary by a key """
        value = None
        if ((self.mqtt_desired is not None) and (isinstance(self.mqtt_desired, dict))):
            if key in self.mqtt_desired:
                value = self.mqtt_desired[key]
        return value
