#!/usr/bin/python3
# invenroty_process.py
"""


inventory_process - maintains a list and reports the list of inventory reported by applications for mqtt-tower



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

import sys

sys.path.append('../lib')
import os

from utils.global_constants import Global
from utils.json_utils import JsonUtils

from structs.mqtt_config import MqttConfig
from structs.io_data import IoData
from structs.inventory import Inventory
from structs.sensor_states import SensorStates
from structs.sensor_states import SensorStateData

from processes.base_process import BaseProcess


class InventoryProcess(BaseProcess):
    """ Class that generates inventory and states reports """
    def __init__(self, events=None, queues=None):
        super().__init__(name="inventory",
                         events=events,
                         in_queue=queues[Global.INVENTORY],
                         log_queue=queues[Global.LOGGER])

        self.events = events
        self.mqtt_config = None
        self.self_topic = None
        self.node_topic = None
        self.app_queue = queues[Global.APPLICATION]
        self.data_path = None
        self.json_helper = JsonUtils()
        self.inventory = None
        self.sensor_states = None
        # self.signal_rules = None

    def initialize_process(self):
        """ load data from file system """
        super().initialize_process()
        self.mqtt_config = MqttConfig(self.config, self.node_name,
                                      self.host_name, self.log_queue)
        (self.node_topic, self.self_topic) \
             = self.__parse_mqtt_options_config(self.mqtt_config)
        self.self_topic = self.self_topic.replace("/#", "/res")
        (self.data_path, _backup_path) \
            = self.__parse_path_options_config(self.config)
        if self.data_path is None or \
                not os.path.exists(self.data_path):
            self.log_error("!!! Error: data path does not exists: " +
                           str(self.data_path))
        else:
            self.__load_inventory()
            self.__load_sensor_states()
            # self.__load_signal_rules()

    def process_message(self, new_message):
        """ process received messages """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            (msg_type, msg_body) = new_message
            if msg_type == Global.REQUEST:
                self.__process_request(msg_body)
                msg_consummed = True
            elif msg_type == Global.RESPONSE:
                report_desired = \
                    msg_body.get_desired_value_by_key(Global.REPORT)
                if report_desired == Global.INVENTORY:
                    self.__process_inventory_response(msg_body)
                    msg_consummed = True
            elif msg_type == Global.ACTIVATED:
                print(">>> node: "+str(msg_body))
                if msg_body != self.node_name and \
                    msg_body.lower().find(Global.TOWER.lower()) == -1:
                    # request inventory for activated nodes except ourselves
                    self.__request_inventory(msg_body)
            elif msg_type == Global.STATE:
                # record a change of state of a sensor,switch, etc
                self.__update_sensor_state(msg_body)
                msg_consummed = True
        return msg_consummed

    #
    # private functions
    #

    def __process_request(self, msg_body):
        """ process request to send inventory reports """
        report_desired = msg_body.get_desired_value_by_key(Global.REPORT)
        self.log_info("report desired: " + str(report_desired))
        reported = report_desired
        metadata = None
        if report_desired == Global.INVENTORY:
            metadata = self.__generate_inventory_report()
        elif report_desired == Global.STATES:
            metadata = self.__generate_sensor_states_report()
        else:
            self.log_unexpected_message(msg_body=msg_body)
            metadata = {Global.ERROR: "Unknown report requested"}
            reported = Global.ERROR
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.RESPONSE, \
            Global.REPORTED: reported, Global.METADATA: metadata, Global.BODY: msg_body}))

    def __request_inventory(self, node_id):
        """ request inventory from a node """
        #print(">>> node activated: " + str(node_id))
        msg_body = IoData()
        msg_body.mqtt_desired = {Global.REPORT: Global.INVENTORY}
        msg_body.mqtt_message_root = Global.TOWER
        msg_body.mqtt_port_id = Global.TOWER
        msg_body.mqtt_respond_to = self.self_topic
        topic = self.node_topic + "/" + node_id + "/" + Global.REPORT + "/" + Global.REQ
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.REQUEST, \
            Global.TOPIC: topic, Global.BODY: msg_body}))

    def __process_inventory_response(self, msg_body):
        """ received inventory response, add info to current inventory """
        #  print(">>> inventory response: " + str(msg_body.mqtt_node_id))
        node_inventory = Inventory(msg_body.mqtt_metadata)
        # print(">>>\n\n inv a: " + str(node_inventory))
        self.inventory.remove_node_inventory(msg_body.mqtt_node_id)
        self.inventory.add_node_inventory(msg_body.mqtt_node_id,
                                          node_inventory)
        # remove any old state for items no longer served by this node
        node_item_list = self.inventory.build_node_item_list(
            msg_body.mqtt_node_id)
        # print(">>> node items:" + str(node_item_list))
        if self.sensor_states is not None:
            self.sensor_states.sync_node_states(msg_body.mqtt_node_id,
                                                node_item_list)

    def __load_inventory(self):
        """ load inventory json data from file system """
        inventory_path = self.data_path + "/inventory.json"
        if not os.path.exists(inventory_path):
            self.log_error("!!! Error: inventory data path does not exists: " +
                           str(inventory_path))
        else:
            inventory_map = self.json_helper.load_and_parse_file(
                inventory_path)
            #print("\n\n>>> inventory 1: "+str(inventory_map))
            self.inventory = Inventory(inventory_map)
            #print("\n\n>>> inventory 2: "+str(self.inventory))
            #inventory_map_2 = self.inventory.encode()
            #print("\n\n>>>inventory 3: "+str(inventory_map_2))

    def __generate_inventory_report(self):
        """ generate report data for panels """
        #print(">>> generate inventory")
        rett = None
        if self.inventory is not None:
            rett = self.inventory.encode()
        return rett

    def __generate_sensor_states_report(self):
        """ generate report data for sensor states """
        rett = None
        if self.sensor_states is not None:
            rett = self.sensor_states.encode()
        return rett

    def __update_sensor_state(self, msg_body):
        """ up the state of a sensor, switch, etc """
        state_data = SensorStateData()
        state_data.node_id = msg_body.mqtt_node_id
        state_data.port_id = msg_body.mqtt_port_id
        state_data.key = state_data.node_id + ":" + state_data.port_id
        state_data.reported = msg_body.mqtt_reported
        state_data.loco_id = [msg_body.mqtt_loco_id
                              ]  # state loco_id are a list
        state_data.metdata = msg_body.mqtt_metadata
        state_data.timestamp = msg_body.mqtt_timestamp
        if msg_body.mqtt_loco_id is not None:
            state_data.loco = [msg_body.mqtt_loco_id]
        #print(">>> update sensor: " + str(state_data))
        self.sensor_states.update_sensor_state(msg_body.mqtt_message_root,
                                               state_data)

    def __load_sensor_states(self):
        """ load sensor_states json data from file system """
        sensor_states_path = self.data_path + "/sensor-states.json"
        if not os.path.exists(sensor_states_path):
            self.log_error(
                "!!! Error: sensor_states data path does not exists: " +
                str(sensor_states_path))
        else:
            sensor_states_map = self.json_helper.load_and_parse_file(
                sensor_states_path)
            #print("\n\n>>> sensor_states 1: "+str(sensor_states_map))
            self.sensor_states = SensorStates(sensor_states_map)
            #print("\n\n>>> sensor_states 2: "+str(self.sensor_states))
            #sensor_states_map_2 = self.sensor_states.encode()
            #print("\n\n>>>sensor_states 3: "+str(sensor_states_map_2))

#    def __load_signal_rules(self):
#        """ load signal rules json data from file system """
#        signal_rules_path = self.data_path + "/signal-rules.json"
#        if not os.path.exists(signal_rules_path):
#            self.log_error(
#                "!!! Error: signal rules data path does not exists: " +
#                str(signal_rules_path))
#        else:
#            signal_rules_map = self.json_helper.load_and_parse_file(
#                signal_rules_path)
#            #print("\n\n>>> sensor_states 1: "+str(sensor_states_map))
#            self.signal_rules = SignalRules(signal_rules_map)
#            #print("\n\n>>> sensor_states 2: "+str(self.sensor_states))
#            #sensor_states_map_2 = self.sensor_states.encode()
#            #print("\n\n>>>sensor_states 3: "+str(sensor_states_map_2))

    def __parse_path_options_config(self, config):
        """ parse path options section of config file """
        data_path = None
        backup_path = None
        if Global.CONFIG in config:
            if Global.OPTIONS in config[Global.CONFIG]:
                data_path = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.DATA_PATH, None)
                backup_path = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.BACKUP_PATH, None)
        return (data_path, backup_path)

    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse pub topics of config file """
        node_topic = mqtt_config.publish_topics.get(Global.NODE,
                                                    Global.UNKNOWN)
        self_topic = mqtt_config.subscribe_topics.get(Global.SELF,
                                                      Global.UNKNOWN)
        return (node_topic, self_topic)
