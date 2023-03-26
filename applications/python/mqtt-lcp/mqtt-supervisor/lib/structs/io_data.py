#!/usr/bin/python3
# io_data.py
"""

    IoData - class that is used when passing io data between modules

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
from copy import deepcopy
import json

sys.path.append('../../lib')

from utils.global_constants import Global
from utils.utility import Utility
#import time


class IoData(object):
    """ Data structure used to store i2c device data """

    def __init__(self):
        """ Initialize """
        self.io_type = None
        self.io_device_key = None
        self.io_address = None
        self.io_sub_address = None
        self.io_device = None
        self.io_device_type = None
        self.io_device_state = None
        self.io_mux_address = None
        self.io_sub_devices = None
        self.io_metadata = None
        self.io_blocks = None
        self.mqtt_major_category = None
        self.mqtt_message_category = None
        self.mqtt_topic = None
        self.mqtt_body = None
        self.mqtt_message_root = None
        self.mqtt_node_id = None
        self.mqtt_port_id = None
        self.mqtt_throttle_id = None
        self.mqtt_cab_id = None
        self.mqtt_loco_id = None
        self.mqtt_identity = None
        self.mqtt_type = None
        # send sensor message if messaging for a switch
        self.mqtt_send_sensor_message = False
        self.mqtt_state = None
        self.mqtt_desired = None
        self.mqtt_reported = None
        self.mqtt_respond_to = None
        self.mqtt_session_id = None
        self.mqtt_description = None
        self.data_topic = None
        self.mqtt_version = None
        self.mqtt_command_topic = None
        self.mqtt_data_topic = None
        self.mqtt_roster_topic = None
        self.mqtt_data_type = None
        self.mqtt_timestamp = None
        self.mqtt_metadata = None

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    @classmethod
    def parse_mqtt_mesage(cls, topic=None, body=None, reversed_globals=None):
        """ parse a mqtt message body dictionary, returns a io_data object """
        new_io_data = IoData()
        new_io_data.mqtt_body = body
        try:
            body_map = json.loads(body)
        except Exception as exc:
            body_map = None
            print("Exception during JSON parsing: " + str(exc) + "\n" +
                  str(body))
        if body_map is not None:
            if not isinstance(body_map, dict):
                # opps, mqtt bost is a value, not a map, build a amp for it
                body_map = {Global.UNKNOWN: {Global.STATE: {Global.DESIRED: body_map}}}
            # get root key of dict
            mroot = list(body_map.keys())[0]
            mbody = body_map[mroot]
            if mbody is not None and isinstance(mbody, dict):
                new_io_data.mqtt_message_root = reversed_globals.get(
                    mroot, mroot).lower()

                new_io_data.mqtt_topic = topic
                new_io_data.mqtt_reported = mbody.get(Global.REPORTED, None)
                new_io_data.mqtt_node_id = mbody.get(Global.NODE_ID, None)
                new_io_data.mqtt_port_id = mbody.get(Global.PORT_ID, None)
                new_io_data.mqtt_throttle_id = mbody.get(
                    Global.THROTTLE_ID, None)
                new_io_data.mqtt_cab_id = mbody.get(Global.CAB_ID, None)
                new_io_data.mqtt_loco_id = mbody.get(Global.LOCO_ID, None)
                new_io_data.mqtt_identity = mbody.get(Global.IDENTITY, None)
                new_io_data.mqtt_session_id = mbody.get(
                    Global.SESSION_ID, None)
                new_io_data.mqtt_version = mbody.get(Global.VERSION, None)
                new_io_data.mqtt_timestamp = mbody.get(Global.TIMESTAMP, None)
                new_io_data.mqtt_respond_to = mbody.get(
                    Global.RESPOND_TO, None)
                new_io_data.mqtt_metadata = mbody.get(Global.METADATA, None)
                if ((new_io_data.mqtt_metadata is not None)
                        and (isinstance(new_io_data.mqtt_metadata, dict))):
                    new_io_data.mqtt_type = new_io_data.mqtt_metadata.get(
                        Global.TYPE, None)
                new_io_data.mqtt_state = mbody.get(Global.STATE, None)
                if ((new_io_data.mqtt_state is not None)
                        and (isinstance(new_io_data.mqtt_state, dict))):
                    new_io_data.mqtt_desired = new_io_data.mqtt_state.get(
                        Global.DESIRED, None)
                    new_io_data.mqtt_reported = new_io_data.mqtt_state.get(
                        Global.REPORTED, None)

                (m, c) = new_io_data.categorize_message(topic)
                new_io_data.mqtt_major_category = m
                new_io_data.mqtt_message_category = c
        return new_io_data

    @classmethod
    def parse_inventory_item(cls, root=None, body_map=None):
        """ parse an inventory item text payload """
        new_io_data = IoData()

        new_io_data.mqtt_metadata = body_map.get(Global.METADATA, None)
        if ((new_io_data.mqtt_metadata is not None)
                and (isinstance(new_io_data.mqtt_metadata, dict))):
            new_io_data.mqtt_type = new_io_data.mqtt_metadata.get(
                Global.TYPE, None)

        new_io_data.mqtt_state = body_map.get(Global.STATE, None)
        if ((new_io_data.mqtt_state is not None)
                and (isinstance(new_io_data.mqtt_state, dict))):
            new_io_data.mqtt_desired = new_io_data.mqtt_state.get(
                Global.DESIRED, None)
            new_io_data.mqtt_reported = new_io_data.mqtt_state.get(
                Global.REPORTED, None)

        send_message_data = body_map.get(Global.SEND_SENSOR_MESSAGE, "no")

        new_io_data.mqtt_send_sensor_message = False
        if send_message_data == "yes":
            new_io_data.mqtt_send_sensor_message = True

        new_io_data.io_type = body_map.get(Global.IO_TYPE, None)
        new_io_data.io_address = body_map.get(Global.IO_ADDRESS, None)
        new_io_data.io_sub_address = body_map.get(Global.IO_SUB_ADDRESS, None)
        new_io_data.io_device = body_map.get(Global.IO_DEVICE, None)
        new_io_data.io_device_type = body_map.get(Global.IO_DEVICE_TYPE, None)
        new_io_data.io_device_state = None
        new_io_data.io_mux_address = body_map.get(Global.IO_MUX_ADDRESS, None)
        new_io_data.io_metadata = body_map.get(Global.IO_METADATA, None)
        new_io_data.mqtt_major_category = None
        new_io_data.mqtt_message_category = None
        new_io_data.mqtt_topic = None
        new_io_data.mqtt_body = None
        new_io_data.mqtt_message_root = root
        new_io_data.mqtt_node_id = body_map.get(Global.NODE_ID, None)
        new_io_data.mqtt_port_id = body_map.get(Global.PORT_ID, None)
        new_io_data.mqtt_description = body_map.get(Global.DESCRIPTION, None)
        new_io_data.mqtt_throttle_id = body_map.get(Global.THROTTLE_ID, None)
        new_io_data.mqtt_cab_id = body_map.get(Global.CAB_ID, None)
        new_io_data.mqtt_loco_id = body_map.get(Global.LOCO_ID, None)
        new_io_data.mqtt_identity = body_map.get(Global.IDENTITY, None)
        new_io_data.mqtt_respond_to = body_map.get(Global.RESPOND_TO, None)
        new_io_data.mqtt_session_id = body_map.get(Global.SESSION_ID, None)
        new_io_data.mqtt_version = body_map.get(Global.VERSION, None)
        new_io_data.mqtt_data_topic = None
        new_io_data.mqtt_data_type = None
        new_io_data.mqtt_timestamp = body_map.get(Global.TIMESTAMP, None)
        return new_io_data

    def parse_state(self):
        """ get the state requested """
        key = None
        value = None
        key = list(self.mqtt_desired.keys())[0]
        value = self.mqtt_desired[key]
        return key, value

    def get_desired_value_by_key(self, key=None):
        """ get sub value in desire dictionary by a key """
        value = None
        if ((self.mqtt_desired is not None)
                and (isinstance(self.mqtt_desired, dict))):
            value = self.mqtt_desired.get(key, None)
        return value

    def get_reported_value_by_key(self, key=None):
        """ get sub value in reported dictionary by a key """
        value = None
        if ((self.mqtt_reported is not None)
                and (isinstance(self.mqtt_reported, dict))):
            value = self.mqtt_reported.get(key, None)
        return value

    def format_response_io_data(self, new_reported=None, error_message=None):
        """ format a response from a mqtt message """
        new_io_data = deepcopy(self)
        new_io_data.mqtt_respond_to = None
        response_topic = self.mqtt_respond_to
        if error_message is not None:
            if new_io_data.mqtt_metadata is None:
                new_io_data.mqtt_metadata = {
                    Global.ERROR_MESSAGE, error_message
                }
            elif isinstance(new_io_data.mqtt_metadata, dict):
                new_io_data.mqtt_metadata.update(Global.ERROR_MESSAGE,
                                                 error_message)
        new_io_data.mqtt_reported = new_reported
        now = Utility.now_milliseconds()
        new_io_data.mqtt_timestamp = now
        return (response_topic, new_io_data)

    def encode_mqtt_message(self):
        """ encode a new message """
        body_map = {}
        if self.mqtt_node_id is not None:
            body_map.update({Global.NODE_ID: self.mqtt_node_id})
        if self.mqtt_port_id is not None:
            body_map.update({Global.PORT_ID: self.mqtt_port_id})
        if self.mqtt_throttle_id is not None:
            body_map.update({Global.THROTTLE_ID: self.mqtt_throttle_id})
        if self.mqtt_cab_id is not None:
            body_map.update({Global.CAB_ID: self.mqtt_cab_id})
        if self.mqtt_loco_id is not None:
            body_map.update({Global.LOCO_ID: self.mqtt_loco_id})
        if self.mqtt_identity is not None:
            body_map.update({Global.IDENTITY: self.mqtt_identity})
        if self.mqtt_desired is not None or self.mqtt_reported is not None:
            state_map = {}
            if self.mqtt_desired is not None:
                state_map.update({Global.DESIRED: self.mqtt_desired})
            if self.mqtt_reported is not None:
                state_map.update({Global.REPORTED: self.mqtt_reported})
            body_map.update({Global.STATE: state_map})
        if self.mqtt_respond_to is not None:
            body_map.update({Global.RESPOND_TO: self.mqtt_respond_to})
        if self.mqtt_session_id is not None:
            body_map.update({Global.SESSION_ID: self.mqtt_session_id})
        if self.mqtt_version is not None:
            body_map.update({Global.VERSION: self.mqtt_version})
        if self.mqtt_timestamp is not None:
            body_map.update({Global.TIMESTAMP: self.mqtt_timestamp})
        if self.mqtt_metadata is not None:
            body_map.update({Global.METADATA: self.mqtt_metadata})
        if self.mqtt_type is not None:
            if self.mqtt_metadata is None:
                body_map.update(
                    {Global.METADATA: {
                        Global.TYPE: self.mqtt_type
                    }})
            elif isinstance(self.mqtt_metadata, dict):
                body_map[Global.METADATA].update(
                    {Global.METADATA: self.mqtt_metadata})

        mqtt_root = None
        if self.mqtt_message_root is not None:
            global_instance = Global()
            try:
                mqtt_root = getattr(global_instance,
                                    self.mqtt_message_root.upper())
            except Exception:
                pass
            body_map = {mqtt_root: body_map}
        # print(">>> !!! enoode JSON: " + str(body_map))
        json_string = json.dumps(body_map)
        return json_string

    def encode_inventory_map(self):
        """ encode an io_data instance as as a map """
        body_map = {}
        if self.mqtt_timestamp is not None:
            body_map.update({Global.TIMESTAMP: self.mqtt_timestamp})
        if self.mqtt_node_id is not None:
            body_map.update({Global.NODE_ID, self.mqtt_node_id})
        if self.mqtt_port_id is not None:
            body_map.update({Global.PORT_ID: self.mqtt_port_id})
        if self.mqtt_throttle_id is not None:
            body_map.update({Global.THROTTLE_ID: self.mqtt_throttle_id})
        if self.mqtt_cab_id is not None:
            body_map.update({Global.CAB_ID: self.mqtt_cab_id})
        if self.mqtt_loco_id is not None:
            body_map.update({Global.LOCO_ID: self.mqtt_loco_id})
        if self.mqtt_identity is not None:
            body_map.update({Global.IDENTITY: self.mqtt_identity})
        if self.mqtt_description is not None:
            body_map.update({Global.DESCRIPTION: self.mqtt_description})
        if self.mqtt_data_topic is not None:
            body_map.update({Global.DATA_TOPIC: self.mqtt_data_topic})
        if self.mqtt_command_topic is not None:
            body_map.update({Global.COMMAND_TOPIC: self.mqtt_command_topic})
        if self.mqtt_desired is not None or self.mqtt_reported is not None:
            state_map = {}
            if self.mqtt_desired is not None:
                state_map.update({Global.DESIRED: self.mqtt_desired})
            if self.mqtt_reported is not None:
                state_map.update({Global.REPORTED: self.mqtt_reported})
            body_map.update({Global.STATE: state_map})
        if self.mqtt_metadata is not None:
            body_map.update({Global.METADATA: self.mqtt_metadata})
        return body_map

    @classmethod
    def convert_inventory_maps_to_lists(cls, inventory_maps=None):
        """ convert a map of maps of inventory iodata structs to a map of lists of plain inventory maps """
        inventory_list = []
        for _i, (_k, value) in enumerate(inventory_maps.items()):
            inventory_list.append(value.encode_inventory_map())
        return inventory_list

    @classmethod
    def get_empty_inventory_maps(cls):
        """ get an empty inventory map initialized wit allowable incentory types """
        new_map = {
            Global.SENSOR: {},
            Global.SWITCH: {},
            Global.LOCATOR: {},
            Global.BLOCK: {},
            Global.SIGNAL: {}
        }
        return new_map

    @classmethod
    def get_inventory_type(cls, text_type=None, reversed_globals=None):
        """convert text based inventory type to a global """
        return reversed_globals.get(text_type, Global.UNKNOWN)

    def categorize_message(self, topic=None):
        """ determine the category of message """

        topic_list = topic.split('/')
        first_topic = topic_list[0].lower()
        last_topic = topic_list[-1].lower()
        major_category = Global.MQTT_OTHER
        if first_topic == "dt":
            major_category = Global.MQTT_DATA
        elif first_topic == "cmd":
            if last_topic == "req":
                major_category = Global.MQTT_REQUEST
            elif last_topic == "res":
                major_category = Global.MQTT_RESPONSE
            else:
                major_category = Global.MQTT_OTHER
        #  print(">>> major >>> "+str(major_category))
        category = major_category
        if major_category == Global.MQTT_REQUEST:
            # print(">>> major >>> "+str(major_category))
            category = self.categorize_request_message()
        elif major_category == Global.MQTT_RESPONSE:
            category = self.categorize_response_message()
        elif major_category == Global.MQTT_DATA:
            category = self.categorize_data_message()
        return (major_category, category)

    def categorize_request_message(self):
        """ categorize a request message """
        category = Global.MQTT_REQUEST
        # print(">>> root >>> "+str(self.mqtt_message_root))
        if self.mqtt_message_root == Global.NODE:
            if self.mqtt_desired == Global.SHUTDOWN:
                category = Global.MQTT_REQUEST_SHUTDOWN
            elif self.mqtt_desired == Global.REBOOT:
                category = Global.MQTT_REQUEST_REBOOT
            elif self.mqtt_desired == Global.BACKUP:
                category = Global.MQTT_REQUEST_BACKUP
            else:
                category = Global.MQTT_REQUEST_NODE
        elif self.mqtt_message_root == Global.TOWER:
            category = Global.MQTT_REQUEST_TOWER
        elif self.mqtt_message_root == Global.ROSTER:
            category = Global.MQTT_REQUEST_ROSTER
        elif self.mqtt_message_root == Global.FASTCLOCK:
            category = Global.MQTT_REQUEST_FASTCLOCK
        elif self.mqtt_message_root == Global.SWITCH:
            category = Global.MQTT_REQUEST_SWITCH
        elif self.mqtt_message_root == Global.SENSOR:
            category = Global.MQTT_REQUEST_SENSOR
        elif self.mqtt_message_root == Global.SIGNAL:
            category = Global.MQTT_REQUEST_SIGNAL
        elif self.mqtt_message_root == Global.CAB:
            category = Global.MQTT_REQUEST_CAB
        else:
            category = Global.MQTT_REQUEST
        return category

    def categorize_response_message(self):
        """ categorize a response message """
        # print(">>> response root: " + str(self.mqtt_message_root))
        category = Global.MQTT_RESPONSE
        if self.mqtt_message_root == Global.NODE:
            category = Global.MQTT_RESPONSE_NODE
        elif self.mqtt_message_root == Global.TOWER:
            #            if isinstance(self.mqtt_reported, dict):
            #                report = self.mqtt_reported.get(Global.REPORT, None)
            #                if report is None:
            #                    category = Global.MQTT_RESPONSE_TOWER
            #                elif report == Global.ROSTER:
            #                    category = Global.MQTT_RESPONSE_ROSTER_REPORT
            #                elif report == Global.INVENTORY:
            #                    category = Global.MQTT_RESPONSE_INVENTORY_REPORT
            #                else:
            #                    category = Global.MQTT_RESPONSE_REPORT
            #            else:
            #                category = Global.MQTT_RESPONSE_TOWER_REPORT
            report = self.mqtt_reported
            port_id = self.mqtt_port_id
            if report is None:
                category = Global.MQTT_RESPONSE_TOWER
            elif port_id == Global.INVENTORY:
                category = Global.MQTT_RESPONSE_INVENTORY_REPORT
            elif port_id == Global.PANELS:
                category = Global.MQTT_RESPONSE_PANELS_REPORT
            elif port_id == Global.STATES:
                category = Global.MQTT_RESPONSE_STATES_REPORT
            elif port_id == Global.SWITCHES:
                category = Global.MQTT_RESPONSE_SWITCHES_REPORT
            elif port_id == Global.SIGNALS:
                category = Global.MQTT_RESPONSE_SIGNALS_REPORT
            elif port_id == Global.ROUTES:
                category = Global.MQTT_RESPONSE_ROUTES_REPORT
            elif port_id == Global.FASTCLOCK:
                category = Global.MQTT_RESPONSE_FASTCLOCK
            else:
                category = Global.MQTT_RESPONSE_TOWER_REPORT
        elif self.mqtt_message_root == Global.ROSTER:
            category = Global.MQTT_RESPONSE_ROSTER_REPORT
        elif self.mqtt_message_root == Global.DCC_COMMAND:
            category = Global.MQTT_RESPONSE_DCC_COMMAND
        elif self.mqtt_message_root == Global.SWITCH:
            category = Global.MQTT_RESPONSE_SWITCH
        elif self.mqtt_message_root == Global.SENSOR:
            category = Global.MQTT_RESPONSE_SENSOR
        elif self.mqtt_message_root == Global.CAB:
            category = Global.MQTT_RESPONSE_CAB
        else:
            category = Global.MQTT_RESPONSE
        return category

    def categorize_data_message(self):
        """ categorize a data message """
        category = Global.MQTT_DATA
        if self.mqtt_message_root == Global.PING:
            category = Global.MQTT_DATA_PING
        elif self.mqtt_message_root == Global.SENSOR:
            category = Global.MQTT_DATA_SENSOR
        elif self.mqtt_message_root == Global.SIGNAL:
            category = Global.MQTT_DATA_SIGNAL
        elif self.mqtt_message_root == Global.BLOCK:
            category = Global.MQTT_DATA_BLOCK
        elif self.mqtt_message_root == Global.LOCATOR:
            category = Global.MQTT_DATA_LOCATOR
        elif self.mqtt_message_root == Global.SWITCH:
            category = Global.MQTT_DATA_SWITCH
        elif self.mqtt_message_root == Global.FASTCLOCK:
            category = Global.MQTT_DATA_FASTCLOCK
        elif self.mqtt_message_root == Global.BACKUP:
            category = Global.MQTT_DATA_BACKUP
        elif self.mqtt_message_root == Global.CAB:
            category = Global.MQTT_DATA_CAB
        elif self.mqtt_message_root == Global.ROSTER:
            category = Global.MQTT_DATA_ROSTER
        elif self.mqtt_message_root == Global.DASHBOARD:
            category = Global.MQTT_DATA_DASHBOARD
        elif self.mqtt_message_root == Global.TOWER:
            category = Global.MQTT_DATA_TOWER
        else:
            category = Global.MQTT_DATA
        return category
