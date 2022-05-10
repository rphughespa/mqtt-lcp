#!/usr/bin/python3
# base_mqtt_process.py
"""

base_mqtt_process - parent class for mqtt app processes


The MIT License (MIT)

Copyright 2021 richard p hughes

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
OUT OFSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
# import copy
import sys

sys.path.append('../../lib')

from structs.io_data import IoData
from structs.mqtt_config import MqttConfig
from structs.roster import Roster
from utils.global_constants import Global
from utils.global_synonyms import Synonyms
from utils.utility import Utility

from processes.base_process import BaseProcess
from processes.base_process import SendAfterMessage


class BaseMqttProcess(BaseProcess):
    """ base class for mqtt app processes """
    def __init__(self,
                 name=None,
                 events=None,
                 in_queue=None,
                 mqtt_queue=None,
                 app_queue=None,
                 log_queue=None):
        BaseProcess.__init__(self,
                             name=name,
                             events=events,
                             in_queue=in_queue,
                             app_queue=app_queue,
                             log_queue=log_queue)
        self.events = events
        self.mqtt_queue = mqtt_queue
        self.ping_time = 0
        self.mqtt_config = None
        self.roster = None
        self.ping_send_after_message = None
        print("base mqtt ok: " + str(self.name))

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def initialize_process(self):
        """ initialize the process """
        print("mqtt init starts: " + str(self.name))
        super().initialize_process()
        self.mqtt_config = MqttConfig(self.config, self.node_name,
                                      self.host_name, self.log_queue)
        self.node_name = self.mqtt_config.node_name
        if self.node_name is None:
            self.log_critical(
                "base-mqtt: !!!! Configuration file error: node name not specified, exiting"
            )
            self.events[Global.SHUTDOWN].set()
        for _i, (_key, topic) in enumerate(
                self.mqtt_config.subscribe_topics.items()):
            self.subscribe_to_topic(topic)
        self.ping_time = self.__parse_ping_time(self.config)
        if self.ping_time > 0:
            self.ping_send_after_message = \
                    SendAfterMessage(Global.PING, None,
                        self.ping_time * 1000)
            # print(">>> starting ping loop: " + str(self.ping_time))
            self.send_after(self.ping_send_after_message)

    def preprocess_message(self, new_message):
        """ pre process a received message """
        # print(">>> message: "+str(new_message))
        msg_consummed = False
        (msg_type, msg_body) = new_message
        if msg_type == Global.MQTT_MESSAGE:
            if isinstance(msg_body, IoData):
                # print(">>> mqtt: "+str(msg_body))
                self.parse_mqtt_message_categories(msg_body)
                msg_consummed = True
        return msg_consummed

    def process_message(self, new_message):
        """ process messages fro queue """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            (msg_type, _msg_body) = new_message
            if msg_type == Global.PING:
                #print(">>> ping...")
                self.send_after(self.ping_send_after_message)
                self.publish_ping_message()
                msg_consummed = True
        return msg_consummed

    def process_other(self):
        """ process no message related tasks """

    def publish_ping_message(self, metadata=None):
        """ publish ping message """
        if self.log_level == Global.LOG_LEVEL_DEBUG:
            self.log_debug("base-mqtt: Publish ping...")
        now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(Global.PING,
                                                    Global.UNKNOWN)
        body = IoData()
        body.mqtt_message_root = Global.PING
        body.mqtt_node_id = self.node_name
        body.mqtt_reported = Global.PING
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        body.mqtt_metadata = metadata
        self.publish_message(topic, body)

    def publish_request_message(self, topic=None, message_io_data=None):
        """ format and publish an mqtt response message """
        if topic is None:
            self.log_error(
                "base_mqtt: Topic missing in request, cannot send:\n" +
                str(message_io_data))
        now = Utility.now_milliseconds()
        body = IoData()
        body.mqtt_message_root = message_io_data.mqtt_message_root
        body.mqtt_node_id = self.node_name
        body.mqtt_port_id = message_io_data.mqtt_port_id
        body.mqtt_respond_to = message_io_data.mqtt_respond_to
        body.mqtt_throttle_id = message_io_data.mqtt_throttle_id
        body.mqtt_cab_id = message_io_data.mqtt_cab_id
        body.mqtt_loco_id = message_io_data.mqtt_loco_id
        body.mqtt_identity = message_io_data.mqtt_identity
        body.mqtt_desired = message_io_data.mqtt_desired
        body.mqtt_timestamp = now
        body.mqtt_session_id = "req:" + str(body.mqtt_timestamp)
        body.mqtt_version = "1.0"
        body.mqtt_metadata = message_io_data.mqtt_metadata
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
            # print(">>> data reported: " + str(data_reported))
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

    def publish_sensor_data_message(self, msg_body):
        """ publish a sensor type data mqtt message """
        #self.log_info("base_mqtt: Send_sensor data message: " +
        ##              str(msg_body.mqtt_port_id) + " ... " +
        #              str(msg_body.mqtt_reported))
        #now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(msg_body.mqtt_message_root, None)
        if topic is None:
            topic = self.mqtt_config.publish_topics.get(Global.SENSOR, None)
        if topic is not None:
            topic += "/" + msg_body.mqtt_port_id
            self.publish_data_message(topic, msg_body)
        #self.update_sensor_inventory_reported(port_id=msg_body.mqtt_port_id,
        #                                      reported=msg_body.mqtt_reported,
        #                                      timestamp=now)

    def publish_data_message(self, topic, msg_body):
        """ publish a data type mqtt message """
        if topic is None:
            self.log_error(
                "base_mqtt: Topic not specified on publish data:\n" +
                str(msg_body.reported))
        now = Utility.now_milliseconds()
        msg_body.mqtt_node_id = self.node_name
        msg_body.mqtt_version = "1.0"
        msg_body.mqtt_timestamp = now
        # print(">>> data: " + str(topic))
        self.publish_message(topic, msg_body)

    def update_sensor_inventory_reported(self,
                                         port_id=None,
                                         reported=None,
                                         timestamp=None):
        """ update reprted and timestamp of a sensor in the inventory """
        if port_id is not None and \
                self.io_config is not None and \
                self.io_config.io_device_map is not None and \
                self.io_config.io_port_map is not None:
            key = self.io_config.io_port_map.get(port_id, None)
            if key is not None:
                sensor = self.io_config.io_device_map.get(key, None)
                if sensor is not None:
                    # print(">>>> update: "+str(port_id)+" ... "+str(reported))
                    sensor.mqtt_reported = reported
                    sensor.mqtt_timestamp = timestamp
                    self.io_config.io_device_map[key] = sensor

    def get_sensor_inventory_state(self,port_id=None):
        """ get state of a sensor in inventory """
        state = None
        if port_id is not None and \
                self.io_config is not None and \
                self.io_config.io_device_map is not None and \
                self.io_config.io_port_map is not None:
            key = self.io_config.io_port_map.get(port_id, None)
            if key is not None:
                sensor = self.io_config.io_device_map.get(key, None)
                if sensor is not None:
                    # print(">>>> update: "+str(port_id)+" ... "+str(reported))
                    state = sensor.mqtt_reported
        return state

    def build_blocks_metadata(self, device_list):
        """ format blocks data, sensors with meta type 'railcom' """
        return self.build_sensors_metadata(device_list, stypes=[Global.BLOCK])

    def build_locators_metadata(self, device_list):
        """ format locator data, sensors with meta type 'railcom' """
        return self.build_sensors_metadata(
            device_list, stypes=[Global.RFID, Global.RAILCOM, Global.LOCATOR])

    def build_sensors_metadata(self, device_list, stypes=None):
        """ format sensor data """
        if stypes is None:
            stypes = []
        sensor_topic = self.mqtt_config.publish_topics.get(Global.SENSOR, None)
        inventory_meta = []
        for dev in device_list:
            #print("\n\n>>> dev: "+str(dev))
            #print(">>> ... stypes: "+str(stypes))
            if dev.io_device_type == Global.SENSOR:
                if dev.io_device in stypes:
                    sensor = {}
                    sensor.update({Global.NODE_ID: self.node_name})
                    if dev.mqtt_port_id is not None:
                        sensor.update({Global.PORT_ID: dev.mqtt_port_id})
                    if dev.mqtt_reported is not None:
                        sensor.update({Global.REPORTED: dev.mqtt_reported})
                    if dev.mqtt_timestamp is not None:
                        sensor.update({Global.TIMESTAMP: dev.mqtt_timestamp})
                    if dev.mqtt_description is not None:
                        sensor.update(
                            {Global.DESCRIPTION: dev.mqtt_description})
                    if dev.mqtt_data_topic is not None:
                        sensor.update({
                            Global.DATA + "-" + Global.TOPIC:
                            dev.mqtt_data_topic
                        })
                    elif sensor_topic is not None:
                        sensor.update({
                            Global.DATA + "-" + Global.TOPIC:
                            sensor_topic + "/" + dev.mqtt_port_id
                        })
                    # print(">>> sensor: "+str(sensor))
                    inventory_meta.append(sensor)
        return inventory_meta

    def build_switches_metadata(self, device_list):
        """ format inventory switch data for inventory reporting """
        inventory_meta = []
        sensor_topic = self.mqtt_config.publish_topics.get(Global.SENSOR, None)
        switch_topic = self.mqtt_config.subscribe_topics.get(
            Global.SWITCH, None)
        for dev in device_list:
            # print("\n\n\n>>> dev: "+str(key))
            if dev.io_device_type == Global.SWITCH:
                #print(">>> ... dev: "+str(dev))
                switch = {}
                switch.update({Global.NODE_ID: self.node_name})
                if dev.io_blocks is not None:
                    switch.update({Global.BLOCKS: dev.io_blocks})
                if dev.mqtt_port_id is not None:
                    switch.update({Global.PORT_ID: dev.mqtt_port_id})
                if dev.mqtt_description is not None:
                    switch.update({Global.DESCRIPTION: dev.mqtt_description})
                if dev.mqtt_data_topic is not None:
                    switch.update({
                        Global.DATA + "_" + Global.TOPIC:
                        dev.mqtt_data_topic
                    })
                elif sensor_topic is not None:
                    switch.update({
                        Global.DATA + "-" + Global.TOPIC:
                        sensor_topic + "/" + dev.mqtt_port_id
                    })
                if dev.mqtt_dispatcher_topic is not None:
                    switch.update({
                        Global.DISPATCHER + "_" + Global.TOPIC:
                        dev.mqtt_dispatcher_topic
                    })
                elif switch_topic is not None:
                    sw_topic = switch_topic.replace("/#", "")
                    switch.update({
                        Global.COMMAND + "-" + Global.TOPIC:
                        sw_topic + "/" + dev.mqtt_port_id + "/req"
                    })

                inventory_meta.append(switch)
        return inventory_meta

    def build_signals_metadata(self, device_list):
        """ format inventory signal data for inventory reporting """
        #print(">>> sub topics: "+str(self.mqtt_config.subscribe_topics))
        sensor_topic = self.mqtt_config.publish_topics.get(Global.SENSOR, None)
        signal_topic = self.mqtt_config.subscribe_topics.get(
            Global.SIGNAL, None)
        inventory_meta = []
        for dev in device_list:
            if dev.io_device_type == Global.SIGNAL:
                signal = {}
                signal.update({Global.NODE_ID: self.node_name})
                if dev.io_blocks is not None:
                    signal.update({Global.BLOCKS: dev.io_blocks})
                if dev.mqtt_port_id is not None:
                    signal.update({Global.PORT_ID: dev.mqtt_port_id})
                if dev.mqtt_description is not None:
                    signal.update({Global.DESCRIPTION: dev.mqtt_description})
                if dev.mqtt_data_topic is not None:
                    signal.update({
                        Global.DATA + "_" + Global.TOPIC:
                        dev.mqtt_data_topic
                    })
                elif sensor_topic is not None:
                    signal.update({
                        Global.DATA + "-" + Global.TOPIC:
                        sensor_topic + "/" + dev.mqtt_port_id
                    })
                if dev.mqtt_dispatcher_topic is not None:
                    signal.update({
                        Global.DISPATCHER + "_" + Global.TOPIC:
                        dev.mqtt_dispatcher_topic
                    })
                elif signal_topic is not None:
                    sig_topic = signal_topic.replace("/#", "")
                    signal.update({
                        Global.COMMAND + "-" + Global.TOPIC:
                        sig_topic + "/" + dev.mqtt_port_id + "/req"
                    })
                inventory_meta.append(signal)
        return inventory_meta

    def parse_mqtt_message_categories(self, msg_body=None):
        """ parse message by category """
        # presume msg_body is an instance of IoData
        major_category = msg_body.mqtt_major_category
        # print(">>> Major category: "+str(major_category))
        if major_category == Global.MQTT_REQUEST:
            self.parse_mqtt_request_message(msg_body=msg_body)
        elif major_category == Global.MQTT_RESPONSE:
            self.parse_mqtt_response_message(msg_body=msg_body)
        elif major_category == Global.MQTT_DATA:
            self.parse_mqtt_data_message(msg_body=msg_body)
        else:
            self.parse_mqtt_other_message(msg_body=msg_body)

    def parse_mqtt_request_message(self, msg_body=None):
        """ parse mqtt request message """
        category = msg_body.mqtt_message_category
        # print(">>> parse request: "+str(category))
        if category == Global.MQTT_REQUEST_SHUTDOWN:
            self.process_request_shutdown_message()
        elif category == Global.MQTT_REQUEST_REBOOT:
            self.process_request_reboot_message()
        elif category == Global.MQTT_REQUEST_BACKUP:
            self.process_request_backup_message(msg_body=msg_body)
        elif category == Global.MQTT_REQUEST_NODE:
            self.process_request_node_message(msg_body=msg_body)
        elif category == Global.MQTT_REQUEST_TOWER:
            self.process_request_tower_message(msg_body=msg_body)
        elif category == Global.MQTT_REQUEST_DISPATCHER:
            self.process_request_dispatcher_message(msg_body=msg_body)
        elif category == Global.MQTT_REQUEST_FASTCLOCK:
            self.process_request_fastclock_message(msg_body=msg_body)
        elif category == Global.MQTT_REQUEST_SIGNAL:
            self.process_request_signal_message(msg_body=msg_body)
        elif category == Global.MQTT_REQUEST_SWITCH:
            self.process_request_switch_message(msg_body=msg_body)
        elif category == Global.MQTT_REQUEST_SENSOR:
            self.process_request_sensor_message(msg_body=msg_body)
        elif category == Global.MQTT_REQUEST_CAB:
            self.process_request_cab_message(msg_body=msg_body)
        else:
            self.process_request_request_message(msg_body=msg_body)

    def parse_mqtt_response_message(self, msg_body=None):
        """ parse mqtt response message """
        category = msg_body.mqtt_message_category
        # print(">>> response category: "+str(category))
        if category == Global.MQTT_RESPONSE_NODE:
            self.process_response_node_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_TOWER:
            self.process_response_tower_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_DISPATCHER:
            self.process_response_dispatcher_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_INVENTORY_REPORT:
            self.process_response_inventory_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_PANELS_REPORT:
            self.process_response_panels_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_WARRANTS_REPORT:
            self.process_response_warrants_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_STATES_REPORT:
            self.process_response_states_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_REPORT:
            self.process_response_report_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_TOWER_REPORT:
            self.process_response_tower_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_DISPATCHER_REPORT:
            self.process_response_dispatcher_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_FASTCLOCK:
            self.process_response_fastclock_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_SWITCH:
            self.process_response_switch_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_SENSOR:
            self.process_response_sensor_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_TRACK:
            self.process_response_track_message(msg_body=msg_body)
        elif category == Global.MQTT_RESPONSE_CAB:
            self.process_response_cab_message(msg_body=msg_body)
        else:
            self.process_response_message(msg_body=msg_body)

    def parse_mqtt_data_message(self, msg_body=None):
        """ parse mqtt data message """
        category = msg_body.mqtt_message_category
        # print(">>> data cat: " + str(category))
        if category == Global.MQTT_DATA_PING:
            self.process_data_ping_message(msg_body=msg_body)
        elif category == Global.MQTT_DATA_SENSOR:
            self.process_data_sensor_message(msg_body=msg_body)
        elif category == Global.MQTT_DATA_SIGNAL:
            self.process_data_signal_message(msg_body=msg_body)
        elif category == Global.MQTT_DATA_BLOCK:
            self.process_data_block_message(msg_body=msg_body)
        elif category == Global.MQTT_DATA_LOCATOR:
            self.process_data_locator_message(msg_body=msg_body)
        elif category == Global.MQTT_DATA_FASTCLOCK:
            self.process_data_fastclock_message(msg_body=msg_body)
        elif category == Global.MQTT_DATA_DASHBOARD:
            self.process_data_dashboard_message(msg_body=msg_body)
        elif category == Global.MQTT_DATA_SWITCH:
            self.process_data_switch_message(msg_body=msg_body)
        elif category == Global.MQTT_DATA_BACKUP:
            self.process_data_backup_message(msg_body=msg_body)
        elif category == Global.MQTT_DATA_CAB:
            self.process_data_cab_message(msg_body=msg_body)
        else:
            self.process_data_message(msg_body=msg_body)

    # the following "process... " functions are expected to be overridden in derived classes, as needed

    def process_request_shutdown_message(self, _msg_body=None):
        """ process request shutdown message """
        # by default, end application
        print("Shutdown message received, exiting ...")
        self.events[Global.SHUTDOWN].set()

    def process_request_reboot_message(self, _msg_body=None):
        """ process request reboot message """
        # by default, end application
        print("Reboot messaging received, rebooting ...")
        self.events[Global.SHUTDOWN].set()

    def process_request_backup_message(self, msg_body=None):
        """ process request backup message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_request_node_message(self, msg_body=None):
        """ process request node message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_request_tower_message(self, msg_body=None):
        """ process request tower message """
        report_desired = msg_body.get_desired_value_by_key(Global.REPORT)
        # print(">>> reg req :" + str(report_desired))
        if report_desired == Global.INVENTORY:
            self.report_inventory(msg_body=msg_body)
        else:
            self.log_unexpected_message(msg_body=msg_body)

    def process_request_dispatcher_message(self, msg_body=None):
        """ process request dispatcher message """
        report_desired = msg_body.get_desired_value_by_key(Global.REPORT)
        # print(">>> reg req :" + str(report_desired))
        if report_desired == Global.INVENTORY:
            self.report_inventory(msg_body=msg_body)
        else:
            self.log_unexpected_message(msg_body=msg_body)

    def process_request_fastclock_message(self, msg_body=None):
        """ process request fastclock message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_request_switch_message(self, msg_body=None):
        """ process request switch message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_request_sensor_message(self, msg_body=None):
        """ process request sensor message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_request_signal_message(self, msg_body=None):
        """ process request signal message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_request_track_message(self, msg_body=None):
        """ process request track message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_request_cab_message(self, msg_body=None):
        """ process request cab message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_request_request_message(self, msg_body=None):
        """ process request request message """
        self.log_unexpected_message(msg_body=msg_body)

    def parse_mqtt_other_message(self, msg_body=None):
        """ parse mqtt other message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_node_message(self, msg_body=None):
        """ process response node message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_tower_message(self, msg_body=None):
        """ process response tower message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_dispatcher_message(self, msg_body=None):
        """ process response dispatcher message """
        desired = msg_body.get_desired_value_by_key(Global.REPORT)
        if desired == Global.ROSTER:
            self.process_response_roster_message(msg_body)
        else:
            self.log_unexpected_message(msg_body=msg_body)

    def process_response_panels_message(self, msg_body=None):
        """ process respons panels message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_roster_message(self, msg_body=None):
        """ received dispatcher roster response message """
        # (">>> dispatcher roster")
        roster_map = None
        meta = msg_body.mqtt_metadata
        if meta is not None:
            roster_map = meta.get(Global.ROSTER, None)
        if roster_map is None:
            # not a roster response, pass it to super instance
            self.log_error("base_cab: No roster found in tower response: " +
                           str(meta))
        else:
            # found a roster
            self.roster = Roster({Global.ROSTER: roster_map})

    def process_response_inventory_message(self, msg_body=None):
        """ process response inventory message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_warrants_message(self, msg_body=None):
        """ process response warrants message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_states_message(self, msg_body=None):
        """ process response inventory message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_report_message(self, msg_body=None):
        """ process response report message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_tower_report_message(self, msg_body=None):
        """ process response tower message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_dispatcher_report_message(self, msg_body=None):
        """ process response dispatcher message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_fastclock_message(self, msg_body=None):
        """ process response fastclock message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_switch_message(self, msg_body=None):
        """ process response switch message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_sensor_message(self, msg_body=None):
        """ process response sensor message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_track_message(self, msg_body=None):
        """ process response track message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_cab_message(self, msg_body=None):
        """ process response cab message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_response_message(self, msg_body=None):
        """ process response message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_ping_message(self, msg_body=None):
        """ process data ping message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_sensor_message(self, msg_body=None):
        """ process data sensor message """
        #print(">>> ... unexpected data sensor ...")
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_signal_message(self, msg_body=None):
        """ process data message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_fastclock_message(self, msg_body=None):
        """ process data fastclock message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_dashboard_message(self, msg_body=None):
        """ process data dashboard message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_block_message(self, msg_body=None):
        """ process data block message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_locator_message(self, msg_body=None):
        """ process data locator message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_switch_message(self, msg_body=None):
        """ process data switch message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_backup_message(self, msg_body=None):
        """ process data backup message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_cab_message(self, msg_body=None):
        """ process data cab message """
        self.log_unexpected_message(msg_body=msg_body)

    def process_data_message(self, msg_body=None):
        """ process data message """
        self.log_unexpected_message(msg_body=msg_body)

    def publish_tower_report_request(self, report_desired):
        """ request report from tower """
        now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(Global.TOWER,
                                                    Global.UNKNOWN) + "/req"
        body = IoData()
        body.mqtt_message_root = Global.TOWER
        body.mqtt_node_id = self.node_name
        body.mqtt_desired = {Global.REPORT: report_desired}
        body.mqtt_respond_to = self.mqtt_config.fixed_subscribe_topics.get(
            Global.SELF) + "/res"
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        #print(">>> pub reg: " + str(body))
        #print(">>>    ... : " + str(topic))
        self.publish_message(topic, body)

    def publish_dispatcher_report_request(self, report_desired):
        """ request roster from dispatcher """
        now = Utility.now_milliseconds()
        topic = self.mqtt_config.publish_topics.get(Global.DISPATCHER,
                                                    Global.UNKNOWN) + "/req"
        body = IoData()
        body.mqtt_message_root = Global.DISPATCHER
        body.mqtt_node_id = self.node_name
        body.mqtt_desired = {Global.REPORT: report_desired}
        body.mqtt_respond_to = self.mqtt_config.fixed_subscribe_topics.get(
            Global.SELF) + "/res"
        body.mqtt_session = "REQ:" + str(now)
        body.mqtt_version = "1.0"
        body.mqtt_timestamp = now
        #print(">>> pub reg: " + str(body))
        #print(">>>    ... : " + str(topic))
        self.publish_message(topic, body)

    def publish_message(self, topic, body):
        """ publish an mqtt message """
        message = (topic, body)
        if self.log_level == Global.LOG_LEVEL_DEBUG:
            self.log_debug("Publish MQTT: " + str(topic) + str(body))
        self.mqtt_queue.put((Global.MQTT_PUBLISH_IODATA, message))

    def subscribe_to_topic(self, topic):
        """ subscribe to a topic """
        # print(">>> "+topic)
        self.mqtt_queue.put((Global.MQTT_SUBSCRIBE, topic))

    def unsubscribe_to_topic(self, topic):
        """ unsubscribe from a topic """
        self.mqtt_queue.put((Global.MQTT_UNSUBSCRIBE, topic))

    def report_inventory(self, msg_body):
        """ response to an inventory request message """
        if self.log_level == Global.LOG_LEVEL_DEBUG:
            self.log_debug("base_mqtt: Handle :report_inventory: " + str(msg_body))

        metadata = {}
        device_list = []
        if self.io_config is not None and \
                self.io_config.io_device_map is not None:
            device_list = self.__flatten_device_map(
                self.io_config.io_device_map)
        # print(">>> inventory report")
        sensors = self.build_sensors_metadata(
            device_list, stypes=[Global.SENSOR, Global.ENCODER])
        if sensors:
            metadata.update({Global.SENSOR: sensors})

        switches = self.build_switches_metadata(device_list)
        if switches:
            metadata.update({Global.SWITCH: switches})

        locators = self.build_locators_metadata(device_list)
        if locators:
            metadata.update({Global.LOCATOR: locators})

        blocks = self.build_blocks_metadata(device_list)
        if blocks:
            metadata.update({Global.BLOCK: blocks})

        signals = self.build_signals_metadata(device_list)
        if signals:
            metadata.update({Global.SIGNAL: signals})

        self.publish_response_message(reported=Global.INVENTORY,
                                      metadata={Global.INVENTORY: metadata},
                                      message_io_data=msg_body)

    def __flatten_device_map(self, device_map):
        """ create a flat list of devices and sub devices """
        dev_list = []
        for (_key, device) in device_map.items():
            dev_list.append(device)
            # print("\n\n\n>>> device flatten: "+str(device))
            if isinstance(device.io_sub_devices, dict):
                for (_key, sub_device) in device.io_sub_devices.items():
                    dev_list.append(sub_device)
        # for dev in dev_list:
        #    print("\n\n>>> dev list: "+str(dev.mqtt_port_id)\
        #        +" ... "+str(dev.io_device_type)+" ... "+str(dev.io_sub_address))
        return dev_list

    def __parse_ping_time(self, config):
        ping_time = 0
        if Global.CONFIG in config:
            if Global.IO in config[Global.CONFIG]:
                if Global.MQTT in config[Global.CONFIG][Global.IO]:
                    ping_time = config[Global.CONFIG][Global.IO][
                        Global.MQTT].get(Global.PING, 0)
        return ping_time
