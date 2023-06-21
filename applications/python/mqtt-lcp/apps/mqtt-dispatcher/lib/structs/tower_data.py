#!/usr/bin/python3
# tower_data.py
"""

TowerData - store the state of track side devices.

the MIT License (MIT)

Copyright © 2023 richard p hughes

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

import sys
import copy

sys.path.append('../../lib')

from utils.global_constants import Global
from utils.compass_points import CompassPoints

class TowerData(object):
    """ tower data shared by multiple processes """

    def __init__(self):
        """ initialize """
        self.switches = {}
        self.signals = {}
        self.routes = {}
        self.blocks = {}
        self.block_signals = {}
        self.loco_locations = {}

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def initialize(self):
        """ initilaize all data maps"""
        self.switches = {}
        self.signals = {}
        self.routes = {}
        self.blocks = {}
        self.block_signals = {}
        self.loco_locations = {}

    def process_output_message(self, message):
        """ process output message """
        if message.msg_type == Global.LOCATOR:
            self.__process_location_message(copy.deepcopy(message.msg_data))
        if message.msg_type == Global.SIGNAL:
            self.__process_signal_message(copy.deepcopy(message.msg_data))
        if message.msg_type == Global.SWITCH:
            self.__process_switch_message(copy.deepcopy(message.msg_data))
        if message.msg_type == Global.ROUTE:
            self.__process_route_message(copy.deepcopy(message.msg_data))
        if message.msg_type == Global.BLOCK:
            self.__process_block_message(copy.deepcopy(message.msg_data))

    def get_current_loco_status(self, loco_id, throttle_direction=Global.CLEAR):
        """ return current loco block location """
        print(">>> get location: "+ str(self.loco_locations.keys()))
        loco_current_block_id = None
        loco_current_direction = None
        loco_cab_signal_key = None
        location = self.loco_locations.get(loco_id, None)
        if location is not None:
            loco_current_block_id = location.block_id
            loco_current_direction = location.direction
            print(" ... "+str(loco_current_block_id))
            print(" ... "+str(loco_current_direction))
            if throttle_direction != Global.CLEAR:
                if throttle_direction == Global.REVERSE:
                    loco_current_direction = CompassPoints.reverse_direction(loco_current_direction)
                block_signal_key = str(location.block_id) + ":" + str(loco_current_direction)
                # print(">>> block signals: "+str(self.block_signals))
                loco_cab_signal_key = self.block_signals.get(block_signal_key, None)
                # print(">>> signal key: "+str(loco_cab_signal_key))
        return (loco_current_block_id, loco_current_direction, loco_cab_signal_key)

    def get_signal_aspect(self, signal_key):
        """ get current aspect of a signal by key, node:port """
        aspect = None
        if signal_key is not None:
            cab_signal = self.signals.get(signal_key, None)
            if cab_signal is not None:
                aspect = cab_signal.mode
        return aspect

#
# private functions
#

    def __process_location_message(self, msg_data):
        """ process a location message, build map of all loco locations """
        if msg_data is None:
            # clear out current data
            self.loco_locations = {}
        else:
            if msg_data.dcc_id is not None:
                current_location = self.loco_locations.get(msg_data.dcc_id, None)
                if current_location is None and \
                        msg_data.mode != Global.EXITED:
                    # loco not in map, add it
                    self.loco_locations.update({msg_data.dcc_id: msg_data})
                    self.__add_loco_to_block(msg_data)
                else:
                    if current_location.block_id == msg_data.block_id and \
                            msg_data.mode == Global.EXITED:
                        # loco reported exited from block. remove it from list
                        del self.loco_locations[msg_data.dcc_id]
                        self.__remove_loco_from_block(current_location)
                    else:
                        self.loco_locations.update(
                            {msg_data.dcc_id: msg_data})
                        self.__add_loco_to_block(msg_data)

    def __process_signal_message(self, msg_data):
        """ process a signal message """
        if msg_data is None:
            self.signals = {}
            self.block_signals = {}
        else:
            key = msg_data.node_id + ":"+ msg_data.port_id
            if msg_data.sub_command == Global.INVENTORY:
                self.signals.update({key: msg_data})
                direction_key = str(msg_data.block_id) + ":" + str(msg_data.direction)
                print(">>> ... new dir key:" +str(direction_key)+" : "+str(key))
                self.block_signals.update({direction_key: key})
            else:
                # print(">>> signal change: "+str(key)+" : "+str(msg_data.mode))
                signal = self.signals.get(key, None)
                if signal is None:
                    self.signals.update({key: msg_data})
                else:
                    signal.mode = msg_data.mode

    def __process_switch_message(self, msg_data):
        """ process a switch message """
        if msg_data is None:
            # clear out tables
            self.switches = {}
        else:
            key = msg_data.node_id + ":"+ msg_data.port_id
            if msg_data.sub_command == Global.INVENTORY:
                self.switches.update({key: msg_data})
            else:
                switch = self.switches.get(key, None)
                if switch is None:
                    self.switches.update({key: msg_data})
                else:
                    switch.mode = msg_data.mode

    def __process_route_message(self, msg_data):
        """ process a route message """
        if msg_data is None:
            # clear out tables
            self.routes = {}
        else:
            key = msg_data.node_id + ":"+ msg_data.port_id
            if msg_data.sub_command == Global.INVENTORY:
                self.routes.update({key: msg_data})
            else:
                route = self.routes.get(key, None)
                if route is None:
                    self.routes.update({key: msg_data})
                else:
                    route.mode = msg_data.mode

    def __process_block_message(self, msg_data):
        """ process a block message """
        if msg_data is None:
            # clear out tables
            self.blocks = {}
        else:
            msg_data.dcc_id = [] # more than one loco can be in a block
            key = msg_data.node_id + ":"+ msg_data.port_id
            if msg_data.sub_command == Global.INVENTORY:
                self.blocks.update({key: msg_data})
            else:
                block = self.blocks.get(key, None)
                if block is None:
                    self.blocks.update({key: msg_data})
                else:
                    block.mode = msg_data.mode

    def __remove_loco_from_block(self, msg_body):
        """ remove a loco id from a block """
        for _key, block in self.blocks.items():
            if block.block_id == msg_body.block_id:
                block.dcc_id.remove(msg_body.dcc_id)

    def __add_loco_to_block(self, msg_body):
        """ add a loco to a block """
        for _key, block in self.blocks.items():
            if block.block_id == msg_body.block_id:
                if msg_body.dcc_id not in block.dcc_id:
                    block.dcc_id.append(msg_body.dcc_id)
