#!/usr/bin/python3
# sensor_states.py
"""

    sensor_states.py - helper class to process last reported state of sensors

    Stores the last reported  state of a sensor, switch, signal, etc.
    Note:  The state from "momentary" devices (rfid locator, buttons, etc) is not saved.
        Only the state of "persistant" devices (switches, signals, railcom locator, block, etc) are saved.


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

from utils.global_constants import Global


class SensorStateData(object):
    """ current state """
    def __init__(self, init_map=None):
        self.key = None
        self.loco_id = None
        self.node_id = None
        self.port_id = None
        self.reported = None
        self.timestamp = 0
        self.metadata = None
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a map return new class instance """
        # print(">>> sensor: " + str(map_body))
        self.loco_id = map_body.get(Global.LOCO_ID, None)
        self.node_id = map_body.get(Global.NODE_ID, None)
        self.port_id = map_body.get(Global.PORT_ID, None)
        self.reported = map_body.get(Global.REPORTED, None)
        self.timestamp = map_body.get(Global.TIMESTAMP, 0)
        self.metadata = map_body.get(Global.METADATA, None)
        self.key = str(self.node_id) + ":" + str(self.port_id)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.loco_id:
            emap.update({Global.LOCO_ID: self.loco_id})
        if self.node_id is not None:
            emap.update({Global.NODE_ID: self.node_id})
        if self.port_id is not None:
            emap.update({Global.PORT_ID: self.port_id})
        if self.reported is not None:
            emap.update({Global.REPORTED: self.reported})
        if self.timestamp is not None:
            emap.update({Global.TIMESTAMP: self.timestamp})
        if self.metadata is not None:
            emap.update({Global.METADATA: self.metadata})
        return (self.key, emap)


class SensorStatesGroupData(object):
    """ a group of sensor states data items"""
    def __init__(self, init_list=None):
        self.sensor_state_items = {}
        if init_list is not None:
            self.parse(init_list)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, list_body=None):
        """ parse a list return new class instance """
        self.sensor_state_items = {}
        if list_body is not None:
            for sensor_state_data in list_body:
                item = SensorStateData(sensor_state_data)
                key = item.key
                self.sensor_state_items.update({key: item})

    def encode(self):
        """ encode a list """
        emap = []
        if self.sensor_state_items is not None:
            new_sensor_state_items = []
            for _inventorysensor_state_item_key, sensor_state_data in \
                    self.sensor_state_items.items():
                (_key, new_item) = sensor_state_data.encode()
                new_sensor_state_items.append(new_item)
            emap = new_sensor_state_items
        return emap

    def sync_node_states(self, group_id, node_id, node_item_list):
        """ remove all inventory items belonging to a node """
        if self.sensor_state_items is not None:
            keys = list(self.sensor_state_items.keys())
            for key in keys:
                item = self.sensor_state_items.get(key, None)
                if item is not None and \
                    item.node_id == node_id:
                    match_key = group_id + ":" + item.key
                    # print(">>> match key: " + str(match_key))
                    if not match_key in node_item_list:
                        self.sensor_state_items.pop(key)


class SensorStates(object):
    """ a groups of sensor state data items"""
    def __init__(self, init_map=None):
        self.sensor_state_groups = self.__init_group_map()
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_map=None):
        """ parse a map return new class instance """
        map_body = map_map.get(Global.SENSOR_STATES, map_map)
        group_body = map_body.get(Global.GROUPS, map_body)
        self.sensor_state_groups = self.__init_group_map()
        for sensor_state_group_key, sensor_state_group_data in \
                group_body.items():
            self.sensor_state_groups.update({
                sensor_state_group_key:
                SensorStatesGroupData(sensor_state_group_data)
            })
        # print(">>> sensor state groups parsed : " + str(self.sensor_state_groups))

    def encode(self):
        """ encode a map """
        emap = {}
        if self.sensor_state_groups is not None:
            new_sensor_state_groups = self.__init_group_map()
            for sensor_state_group_key, sensor_state_group in \
                    self.sensor_state_groups.items():
                new_sensor_state_group = sensor_state_group.encode()
                new_sensor_state_groups.update(
                    {sensor_state_group_key: new_sensor_state_group})
            emap = new_sensor_state_groups
        # print(">>> sensor state groups encoded: " + str(emap))
        return {
            Global.SENSOR_STATES: {
                Global.DESCRIPTION: "Sensor States",
                Global.GROUPS: emap
            }
        }

    def sync_node_states(self, node_id, node_item_list):
        """ remove any sensor state for an item not in the inventory list """
        #print(">>> node items:" + str(node_id) + " .. " + str(node_item_list))
        for sensor_group_key, sensor_state_group in \
                    self.sensor_state_groups.items():
            sensor_state_group.sync_node_states(sensor_group_key, node_id,
                                                node_item_list)

    def update_sensor_state(self, sensor_group_id, new_sensor_state):
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
        if not self.__sensor_data_momentary(sensor_group_id, new_sensor_state):
            if sensor_group_id == Global.LOCATOR:
                # railcom type locator device, needs special handling
                self.__update_locator_state(sensor_group_id, new_sensor_state)
            else:
                self.__update_simple_state(sensor_group_id, new_sensor_state)

    #
    # private functions
    #

    def __update_locator_state(self, sensor_group_id, new_sensor_state):
        """ update the state of a locator type sensor """
        sensor_group = self.sensor_state_groups.get(sensor_group_id, None)
        if sensor_group is not None:
            exisiting_sensor_state = sensor_group.sensor_state_items.get(
                new_sensor_state.key)
            if exisiting_sensor_state is None:
                # not current state, add it
                sensor_group.sensor_state_items.update(
                    {new_sensor_state.key: new_sensor_state})
            else:
                if new_sensor_state.timestamp > exisiting_sensor_state.timestamp:
                    exisiting_sensor_state.timestamp = new_sensor_state.timestamp
                    # special handling of loco id's
                    if new_sensor_state.loco_id:
                        # get first loco in list
                        loco = new_sensor_state.loco_id[0]
                        #print(">>> loco id: " + str(loco))
                        #print(">>> loco2: " + str(exisiting_sensor_state.loco_id))
                        if new_sensor_state.reported == Global.ENTERED:
                            # new loc reported, add to loco listif
                            if exisiting_sensor_state.loco_id.count(loco) == 0:
                                exisiting_sensor_state.loco_id.append(loco)
                        elif new_sensor_state.reported == Global.EXITED:
                            # loco left, remove from list
                            if exisiting_sensor_state.loco_id.count(loco) > 0:
                                exisiting_sensor_state.loco_id.remove(loco)
                        #print(">>> loco3: " + str(exisiting_sensor_state.loco_id))

    def __update_simple_state(self, sensor_group_id, new_sensor_state):
        """ update the state of a simple device """
        sensor_group = self.sensor_state_groups.get(sensor_group_id, None)
        if sensor_group is not None:
            exisiting_sensor_state = sensor_group.sensor_state_items.get(
                new_sensor_state.key)
            if exisiting_sensor_state is None:
                # not current state, add it
                sensor_group.sensor_state_items.update(
                    {new_sensor_state.key: new_sensor_state})
            else:
                if new_sensor_state.timestamp > exisiting_sensor_state.timestamp:
                    exisiting_sensor_state.timestamp = new_sensor_state.timestamp
                    exisiting_sensor_state.reported = new_sensor_state.reported

    def __sensor_data_momentary(self, sensor_group_id, new_sensor_state):
        momentary = False
        if sensor_group_id == Global.LOCATOR:
            if new_sensor_state.reported == Global.DETECTED:
                # RFID tag read, don't record state
                momentary = True
        elif sensor_group_id == Global.SENSOR:
            if new_sensor_state.reported == Global.CLICKED:
                # push button read, don't record state
                momentary = True
        return momentary

    def __init_group_map(self):
        """ init groups """
        rett = {}
        for stype in Global.MQTT_SENSOR_TYPES:
            rett.update({stype: SensorStatesGroupData()})
        # print(">>> sensor types: " + str(rett))
        return rett
