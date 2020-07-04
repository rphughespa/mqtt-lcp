# switches.py - manages a dictionary of switches

"""

    Switches.py - helper class to process turnout definitions

the MIT License (MIT)

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

import os.path
import json
# import time

from global_constants import Global

class Switch():
    """ A class to maange switches"""

    def __init__(self, node_id="", port_id="", description="", reported="",
            block_entry="", block_continue="", block_diverge="",
            message_command="", message_sensor=""):
        self.node_id = node_id
        self.port_id = port_id
        self.description = description
        self.block_entry = block_entry
        self.block_through = block_continue
        self.block_diverge = block_diverge
        self.message_command = message_command
        self.message_sensor = message_sensor
        self.reported = reported


    def load(self, dict_data):
        """ Load data"""
        if Global.NODE_ID in dict_data:
            self.node_id = dict_data[Global.NODE_ID]
        else:
            self.node_id = ""
        if Global.PORT_ID in dict_data:
            self.port_id = dict_data[Global.PORT_ID]
        else:
            self.port_id = ""
        if Global.DESCRIPTION in dict_data:
            self.description = dict_data[Global.DESCRIPTION]
        else:
            self.description = ""
        if Global.BLOCKS in dict_data:
            block_data = dict_data[Global.BLOCKS]
            if Global.ENTRY in block_data:
                self.block_entry = block_data[Global.ENTRY]
            if Global.THROUGH in block_data:
                self.block_through = block_data[Global.THROUGH]
            if Global.DIVERGE in block_data:
                self.block_diverge = block_data[Global.DIVERGE]
        if Global.MESSAGES in dict_data:
            msg_data = dict_data[Global.MESSAGES]
            if Global.COMMAND in msg_data:
                self.message_command = msg_data[Global.COMMAND]
            if Global.SENSOR in msg_data:
                self.message_sensor = msg_data[Global.SENSOR]

    def dump(self):
        """ Dump data"""
        new_dict = {}
        new_dict[Global.NODE_ID] = self.node_id
        new_dict[Global.PORT_ID] = self.port_id
        new_dict[Global.DESCRIPTION] = self.description
        new_dict_blocks = {}
        new_dict_blocks[Global.ENTRY] = self.block_entry
        new_dict_blocks[Global.THROUGH] = self.block_through
        new_dict_blocks[Global.DIVERGE] = self.block_diverge
        new_dict[Global.BLOCKS] = new_dict_blocks
        new_dict_msg = {}
        new_dict_msg[Global.COMMAND] = self.message_command
        new_dict_msg[Global.STATE] = self.message_sensor
        new_dict[Global.MESSAGES] = new_dict_msg
        return new_dict

class Switches():
    """ List of switches"""

    def __init__(self, log_queue, file_path=None):
        self.items = {}
        self.name = ""
        self.description = ""
        self.file_path = file_path
        self.log_queue = log_queue
        self.load_data(self.file_path)

    def load(self, dash_dict):
        """ Load data into the dashboard"""
        self.items = {}
        if Global.SWITCHES in dash_dict:
            dash_dict = dash_dict[Global.SWITCHES]
        if Global.NAME in dash_dict:
            self.name = dash_dict[Global.NAME]
        else:
            self.name = ""
        if Global.DESCRIPTION in dash_dict:
            self.description = dash_dict[Global.DESCRIPTION]
        else:
            self.description = ""
        if Global.ITEMS in dash_dict:
            data_items = dash_dict[Global.ITEMS]
            for data_item in data_items:
                new_item = Switch()
                new_item.load(data_item)
                self.items[new_item.node_id+"/"+new_item.port_id] = new_item

    def dump(self):
        """ Dump data from the panel"""
        new_dict = {}
        new_dict[Global.NAME] = self.name
        new_dict[Global.DESCRIPTION] = self.description
        new_dict_items = []
        for _key, value in self.items.items():
            dict_item = value.dump()
            new_dict_items.append(dict_item)
        new_dict[Global.ITEMS] = new_dict_items
        return new_dict

    def load_data(self, file_path):
        """ Load data"""
        if file_path is not None:
            if os.path.exists(file_path):
                with open(file_path) as json_file:
                    json_dict = json.load(json_file)
                    self.load(json_dict)

    def save_data(self, file_path):
        """ save data"""
        if file_path is not None:
            with open(file_path, 'w') as json_file:
                json.dump(self.dump(), json_file)
