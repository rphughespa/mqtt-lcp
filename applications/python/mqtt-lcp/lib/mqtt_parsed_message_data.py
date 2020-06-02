# mqtt_parsed_message_data.py

"""

    mqtt_parsed_message_data - class that is used when parsing mqtt message body

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

class MqttParsedMessageData():
    """ Parsed Message Data """

    def __init__(self, message_body_dict=None):
        """ Initialize """
        self.message_root = None
        self.node_id = None
        self.port_id = None
        self.type = None
        self.session_id = None
        self.timestamp = None
        self.desired = None
        self.reported = None
        self.metadata = None
        self.res_topic = None
        if message_body_dict is not None:
            self.message_root = list(message_body_dict.keys())[0] # get root key of dict
            message_body = message_body_dict[self.message_root]
            if Global.NODE_ID in message_body:
                self.node_id = message_body[Global.NODE_ID]
            if Global.PORT_ID in message_body:
                self.port_id = message_body[Global.PORT_ID]
            if Global.SESSION_ID in message_body:
                self.session_id = message_body[Global.SESSION_ID]
            if Global.TIMESTAMP in message_body:
                self.timestamp = message_body[Global.TIMESTAMP]
            if Global.RES_TOPIC in message_body:
                self.res_topic = message_body[Global.RES_TOPIC]
            if Global.METADATA in message_body:
                self.metadata = message_body[Global.METADATA]
                if isinstance(self.metadata, dict):
                    if Global.TYPE in self.metadata:
                        self.type = self.metadata[Global.TYPE]
            if Global.STATE in message_body:
                if Global.DESIRED in message_body[Global.STATE]:
                    self.desired = message_body[Global.STATE][Global.DESIRED]
                if Global.REPORTED in message_body[Global.STATE]:
                    self.reported = message_body[Global.STATE][Global.REPORTED]
