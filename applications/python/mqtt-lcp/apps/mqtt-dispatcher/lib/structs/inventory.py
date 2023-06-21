#!/usr/bin/python3
# inventory.py
"""

    inventory.py - helper class to process inventory definitions of signals, blocks, etc


The MIT License (MIT)

Copyright  2023 richard p hughes

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
import copy

sys.path.append('../../lib')

from utils.global_constants import Global
from utils.utility import Utility


class InventoryData(object):
    """ status of a node """

    def __init__(self, init_map=None):
        self.key = None
        self.node_id = None
        self.port_id = None
        self.description = None
        self.loco_id = None
        self.block_id = None
        self.direction = None
        self.reported = None
        self.timestamp = None
        self.command_topic = None
        self.data_topic = None
        self.metadata = None
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a map return new class instance """
        # print(">>> item body: " + str(map_body))
        if not isinstance(map_body, dict):
            print("!!! error, bad inventory item: " + str(map_body))
        else:
            self.node_id = map_body.get(Global.NODE_ID, None)
            self.port_id = map_body.get(Global.PORT_ID, None)
            self.block_id = map_body.get(Global.BLOCK_ID,  None)
            self.direction = map_body.get(Global.DIRECTION,  None)
            self.description = map_body.get(Global.DESCRIPTION, None)
            self.timestamp = map_body.get(Global.TIMESTAMP, None)
            self.loco_id = map_body.get(Global.LOCO_ID, None)
            self.reported = map_body.get(Global.REPORTED, None)
            self.command_topic = map_body.get(Global.COMMAND_TOPIC, None)
            self.data_topic = map_body.get(Global.DATA_TOPIC, None)
            self.metadata = map_body.get(Global.METADATA, None)
            self.key = str(self.node_id) + ":" + str(self.port_id)

    def parse_mqtt_message(self, msg_body=None):
        """ parse a mqtt message return new class instance """
        # print(">>> item body: " + str(msg_body))
        self.node_id = msg_body.mqtt_node_id
        self.port_id = msg_body.mqtt_port_id
        self.block_id = msg_body.mqtt_block_id
        self.direction = msg_body.mqtt_direction
        self.description = None
        self.timestamp = msg_body.mqtt_timestamp
        self.loco_id = msg_body.mqtt_loco_id
        self.reported = msg_body.mqtt_reported
        self.command_topic = None
        self.data_topic = None
        self.metadata = msg_body.mqtt_metadata
        self.key = str(self.node_id) + ":" + str(self.port_id)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.node_id is not None:
            emap.update({Global.NODE_ID: self.node_id})
        if self.port_id is not None:
            emap.update({Global.PORT_ID: self.port_id})
        if self.description is not None:
            emap.update({Global.DESCRIPTION: self.description})
        if self.block_id is not None:
            emap.update({Global.BLOCK_ID: self.block_id})
        if self.loco_id is not None:
            emap.update({Global.LOCO_ID: self.loco_id})
        if self.timestamp is not None:
            emap.update({Global.TIMESTAMP: self.timestamp})
        if self.direction is not None:
            emap.update({Global.DIRECTION: self.direction})
        if self.reported is not None:
            emap.update({Global.REPORTED: self.reported})
        if self.command_topic is not None:
            emap.update({Global.COMMAND_TOPIC: self.command_topic})
        if self.data_topic is not None:
            emap.update({Global.DATA_TOPIC: self.data_topic})
        if self.metadata is not None:
            emap.update({Global.METADATA: self.metadata})
        return emap


class InventoryGroupData(object):
    """ a group of inventory data items"""

    def __init__(self, init_list=None):
        self.inventory_items = {}
        self.inventory_by_port_id = {}
        if init_list is not None:
            self.parse(init_list)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, list_body=None):
        """ parse a list return new class instance """
        self.inventory_items = {}
        self.inventory_by_port_id = {}
        if list_body is not None:
            for inventory_data in list_body:
                item = InventoryData(inventory_data)
                self.inventory_items.update({item.key: item})
                self.inventory_by_port_id.update({item.port_id: item.key})

    def encode(self):
        """ encode a list """
        emap = []
        if self.inventory_items is not None:
            new_inventory_items = []
            for _k, item in self.inventory_items.items():
                new_item = item.encode()
                new_inventory_items.append(new_item)
            emap = new_inventory_items
        return emap

    def add_node_inventory(self, merge_items):
        """ update current inventory with inventory from a node """
        # clear out previous inventroy items from this node
        #  for merge_key, merge_item in merge_items.inventory_items.items():
        #    copied_item = copy.deepcopy(merge_item)
        #    self.inventory_items.update({merge_key: copied_item})
        #print(">>> merge items: " + str(merge_items))
        if merge_items.inventory_items is not None:
            for _key, item in sorted(merge_items.inventory_items.items()):
                self.add_an_item(item)

    def add_an_item(self, item):
        """ add an item to this group """
        #print(">>> item: "+str(item))
        new_item = copy.deepcopy(item)
        if new_item.timestamp is  None:
            new_item.timestamp = Utility.now_milliseconds()
        #print(">>> copy: "+str(new_item))
        self.inventory_items.update({new_item.key: new_item})
        self.inventory_by_port_id.update({new_item.port_id: new_item.key})

    def remove_node_inventory(self, node_id):
        """ remove all inventory items belonging to a node """
        if self.inventory_items is not None:
            new_items = {}
            new_inventory_by_port_id = {}
            for _k, item in self.inventory_items.items():
                if item.node_id != node_id:
                    new_items.update({item.key: item})
                    new_inventory_by_port_id.update({item.port_id: item.key})
            self.inventory_items = new_items
            self.inventory_by_port_id = new_inventory_by_port_id

class Inventory(object):
    """ a groups of inventory data items"""

    def __init__(self, init_map=None):
        self.description = None
        self.inventory_groups = self.__init_group_map()
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_map=None):
        """ parse a map return new class instance """
        # print(">>> inc: " + str(map_map))
        map_body = map_map.get(Global.INVENTORY, map_map)
        group_body = map_body.get(Global.INVENTORY, map_body)
        # print(">>> inc2: " + str(group_body))
        self.inventory_groups = self.__init_group_map()
        for inventory_group_key, inventory_group_data in \
                group_body.items():
            # print(">>> inv group: " + str(inventory_group_key))
            self.inventory_groups.update({
                inventory_group_key:
                InventoryGroupData(inventory_group_data)
            })
        # print(">>> inventory groups parsed : " + str(self.inventory_groups))

    def encode(self, requested_group=None):
        """ encode a map """
        # print(">>> inv encode: "+str(requested_group))
        emap = {}
        if self.inventory_groups is not None:
            new_inventory_groups = {}
            if requested_group is not None:
                new_inventory_groups = {requested_group: InventoryGroupData()}
            else:
                new_inventory_groups = self.__init_group_map()
            for inventory_group_key, inventory_group in \
                    self.inventory_groups.items():
                # print(">>> inv group: "+str(requested_group) +
                #      " ... "+str(inventory_group_key))
                if (requested_group is None) or (requested_group == inventory_group_key):
                    new_inventory_group = inventory_group.encode()
                    new_inventory_groups.update(
                        {inventory_group_key: new_inventory_group})
            emap = new_inventory_groups
        #  print(">>> inventory groups encoded: " + str(emap))
        return {
            Global.INVENTORY: {
                Global.DESCRIPTION: "Inventory",
                Global.INVENTORY: emap
            }
        }

    def add_node_inventory(self, node_id, node_inventory):
        """ update current inventory with inventory from a node """
        # print(">>> node inventory: " + str(node_id) + "...\n" +
        #      str(node_inventory))
        # clear out previous inventroy item from this node
        self.remove_node_inventory(node_id)
        # print(">>> node inv: " + str(node_inventory))
        for merge_group, merge_group_items in \
                node_inventory.inventory_groups.items():
            if merge_group_items:
                # print(">>> merge1: " + str(merge_group) + " ... " +
                #      str(merge_group_items))
                group = self.inventory_groups.get(merge_group, None)
                if group is not None:
                    group.add_node_inventory(merge_group_items)

    def remove_node_inventory(self, node_id):
        """ remove all inventory items belonging to a node """
        for _inventory_group_key, inventory_group in \
                self.inventory_groups.items():
            inventory_group.remove_node_inventory(node_id)

    def build_node_item_list(self, node_id):
        """ build a list of all inventory items for a node """
        node_item_list = []
        for inventory_group_key, inventory_group in \
                self.inventory_groups.items():
            for _key, item in inventory_group.inventory_items.items():
                if item.node_id == node_id:
                    node_item_list.append(inventory_group_key + ":" + item.key)
        return node_item_list

    def update_sensor_state(self, group_id, new_sensor_state):
        """ update / add a new state for a sensor """

        # Global.DETECTED
        # Global.DATA: str(return_counter)
        # Global.CLICKED
        # Global.ENTERED
        # Global.EXITED
        # Global.CLEAR
        # Global.OCCUPIED
        # Global.CLEAR
        # Global.APPROACH
        if group_id == Global.LOCATOR:
            # railcom type locator device, needs special handling
            self.__update_locator_state(group_id, new_sensor_state)
        else:
            self.__update_simple_state(group_id, new_sensor_state)

    def sensor_data_momentary(self, group_id, new_sensor_state):
        """ sensor data for monentary switch """
        momentary = False
        if group_id == Global.LOCATOR:
            if new_sensor_state.reported == Global.DETECTED:
                # RFID tag read, don't record state
                momentary = True
        elif group_id == Global.SENSOR:
            if new_sensor_state.reported == Global.CLICKED:
                # push button read, don't record state
                momentary = True
        return momentary

    #
    # private functions
    #

    def __update_locator_state(self, group_id, new_sensor_state):
        """ update the state of a locator type sensor """
        # there may be multiple locos per locator
        inventory_group = self.inventory_groups.get(group_id, None)
        if inventory_group is None:
            inventory_group = InventoryGroupData()
            self.inventory_groups.update({group_id: inventory_group})
        existing_item = inventory_group.inventory_items.get(
            new_sensor_state.key)
        if existing_item is None:
            # not current state, add it
            new_item = None
            if isinstance(new_sensor_state, InventoryData):
                new_item = copy.deepcopy(new_sensor_state)
            else:
                new_item = InventoryData(new_sensor_state)
            print("!!! warning: Sensor reported but Inventory Item does not exist: "+str(new_sensor_state))
            inventory_group.inventory_items.update(
                {new_sensor_state.key: new_item})
            inventory_group.inventory_by_port_id.update(
                {new_item.port_id: new_item.key})
        else:
            if existing_item.command_topic is None:
                # item create by sensor report befor inventory loaded
                existing_item.command_topic = new_sensor_state.command_topic
                existing_item.data_topic = new_sensor_state.data_topic
            if existing_item.timestamp is None or \
                    new_sensor_state.timestamp > existing_item.timestamp:
                existing_item.timestamp = new_sensor_state.timestamp
                existing_item.metadata = new_sensor_state.metadata

                # special handling of loco id's
                if new_sensor_state.loco_id:
                    # get first loco in list
                    loco = new_sensor_state.loco_id
                    if isinstance(loco, list):
                        loco = loco[0]
                    # print(">>> loco id: " + str(loco))
                    # print(">>> loco2: " + str(existing_item.loco_id))
                    if new_sensor_state.reported == Global.ENTERED:
                        # new loco reported, add to loco list
                        if existing_item.loco_id is None:
                            existing_item.loco_id = [loco]
                        elif not isinstance(existing_item.loco_id, list):
                            if existing_item.loco_id != loco:
                                existing_item.loco_id = [existing_item.loco_id, loco]
                        else:
                            if loco not in existing_item.loco_id:
                                existing_item.loco_id.append(loco)
                    elif new_sensor_state.reported == Global.EXITED:
                        # loco left, remove from list
                        if existing_item.loco_id is not None:
                            if isinstance(existing_item.loco_id, list):
                                if loco in existing_item.loco_id:
                                    existing_item.loco_id.remove(loco)
                            elif existing_item.loco_id == loco:
                                existing_item.loco_id = None
                    # print(">>> loco3: " + str(existing_item.loco_id))

    def __update_simple_state(self, inventory_group_id, new_sensor_state):
        """ update the state of a simple device """
        #print(">>> update: "+str(new_sensor_state))
        inventory_group = self.inventory_groups.get(inventory_group_id, None)
        if inventory_group is None:
            inventory_group = InventoryGroupData()
            self.inventory_groups.update({inventory_group_id: inventory_group})
        existing_item = inventory_group.inventory_items.get(
            new_sensor_state.key, None)
        #print(">>> ... found: "+str(existing_item))
        if existing_item is None:
            # not current state, add it
            new_item = None
            if isinstance(new_sensor_state, InventoryData):
                new_item = copy.deepcopy(new_sensor_state)
            else:
                new_item = InventoryData(new_sensor_state)
            print("!!! warning: Sensor reported but Inventory Item does not exist: "+\
                  str(inventory_group)+" : "+str(new_sensor_state))
            inventory_group.inventory_items.update(
                {new_item.key: new_item})
            inventory_group.inventory_by_port_id.update(
                {new_item.port_id: new_item.key})
        else:
            if existing_item.command_topic is None:
                # item create by sensor report befor inventory loaded
                existing_item.command_topic = new_sensor_state.command_topic
                existing_item.data_topic = new_sensor_state.data_topic
            if existing_item.timestamp is None or \
                    new_sensor_state.timestamp > existing_item.timestamp:
                existing_item.timestamp = new_sensor_state.timestamp
                existing_item.reported = new_sensor_state.reported
            #print(">>> after: "+str(existing_item))
        self.inventory_groups.update({inventory_group_id: inventory_group})
        # print(">>> inventory_group: "+str(inventory_group_id) + " : "+ str(inventory_group))

    def __init_group_map(self):
        """ init groups """
        rett = {}
        for stype in Global.MQTT_SENSOR_TYPES:
            rett.update({stype: InventoryGroupData()})
        # print(">>> sensor types: " + str(rett))
        return rett
