#!/usr/bin/python3
# inventory.py
"""

    inventory.py - helper class to process inventory definitions of signals, nlocks, etc


The MIT License (MIT)

Copyright  2021 richard p hughes

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

sys.path.append('../../lib')

import copy

from utils.global_constants import Global


class InventoryData(object):
    """ status of a node """
    def __init__(self, init_map=None):
        self.key = None
        self.node_id = None
        self.port_id = None
        self.description = None
        self.command_topic = None
        self.data_topic = None
        self.metadata = None
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        #return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a map return new class instance """
        # print(">>> item body: " + str(map_body))
        self.node_id = map_body.get(Global.NODE_ID, None)
        self.port_id = map_body.get(Global.PORT_ID, None)
        self.description = map_body.get(Global.DESCRIPTION, None)
        self.command_topic = map_body.get(Global.COMMAND_TOPIC, None)
        self.data_topic = map_body.get(Global.DATA_TOPIC, None)
        self.metadata = map_body.get(Global.METADATA, None)
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
        self.inventory_items = []
        if init_list is not None:
            self.parse(init_list)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, list_body=None):
        """ parse a list return new class instance """
        self.inventory_items = []
        if list_body is not None:
            for inventory_data in list_body:
                item = InventoryData(inventory_data)
                self.inventory_items.append(item)

    def encode(self):
        """ encode a list """
        emap = []
        if self.inventory_items is not None:
            new_inventory_items = []
            for item in self.inventory_items:
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
        # print(">>> merge items: " + str(merge_items))
        if merge_items.inventory_items is not None:
            for item in merge_items.inventory_items:
                new_item = copy.deepcopy(item)
                self.inventory_items.append(new_item)

    def remove_node_inventory(self, node_id):
        """ remove all inventory items belonging to a node """
        if self.inventory_items is not None:
            new_items = []
            for item in self.inventory_items:
                if item.node_id != node_id:
                    new_items.append(item)
            self.inventory_items = new_items


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
        #print(">>> inc: " + str(map_map))
        map_body = map_map.get(Global.INVENTORY, map_map)
        group_body = map_body.get(Global.GROUPS, map_body)
        #print(">>> inc2: " + str(group_body))
        self.inventory_groups = self.__init_group_map()
        for inventory_group_key, inventory_group_data in \
                group_body.items():
            # print(">>> inv group: " + str(inventory_group_key))
            self.inventory_groups.update({
                inventory_group_key:
                InventoryGroupData(inventory_group_data)
            })
        # print(">>> inventory groups parsed : " + str(self.inventory_groups))

    def encode(self):
        """ encode a map """
        emap = {}
        if self.inventory_groups is not None:
            new_inventory_groups = self.__init_group_map()
            for inventory_group_key, inventory_group in \
                    self.inventory_groups.items():
                new_inventory_group = inventory_group.encode()
                new_inventory_groups.update(
                    {inventory_group_key: new_inventory_group})
            emap = new_inventory_groups
        #  print(">>> inventory groups encoded: " + str(emap))
        return {
            Global.INVENTORY: {
                Global.DESCRIPTION: "Inventory",
                Global.GROUPS: emap
            }
        }

    def add_node_inventory(self, node_id, node_inventory):
        """ update current inventory with inventory from a node """
        #print(">>> node inventory: " + str(node_id) + "...\n" +
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
            for item in inventory_group.inventory_items:
                if item.node_id == node_id:
                    node_item_list.append(inventory_group_key + ":" + item.key)
        return node_item_list

    #
    # private functions
    #

    def __init_group_map(self):
        """ init groups """
        rett = {}
        for stype in Global.MQTT_SENSOR_TYPES:
            rett.update({stype: InventoryGroupData()})
        # print(">>> sensor types: " + str(rett))
        return rett
