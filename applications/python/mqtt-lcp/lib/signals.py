# signals.py - a dictionary of signals

"""

    signals.py - helper class to process layout signal definitions

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

class SignalBlock():
    """ A block of signals"""

    def __init__(self, name="", stype=""):
        self.name = name
        self.type = stype

    def load(self, dict_data):
        """ load a signal block"""
        if Global.NAME in dict_data:
            self.name = dict_data[Global.NAME]
        else:
            self.name = ""
        if Global.TYPE in dict_data:
            self.type = dict_data[Global.TYPE]
        else:
            self.type = ""

    def dump(self):
        """ dump signal block"""
        new_dict = {}
        new_dict[Global.BLOCK] = self.name
        new_dict[Global.TYPE] = self.type
        return new_dict

class Signal():
    """ A signal"""

    def __init__(self, name="", description="", stype="",
            message_command="", message_state="", state=""):
        self.name = name
        self.description = description
        self.message_command = message_command
        self.message_state = message_state
        self.state = state
        self.type = stype
        self.blocks = []

    def load(self, dict_data):
        """ load a signal"""
        if Global.NAME in dict_data:
            self.name = dict_data[Global.NAME]
        else:
            self.description = ""
        if Global.DESCRIPTION in dict_data:
            self.description = dict_data[Global.DESCRIPTION]
        else:
            self.description = ""
        if Global.TYPE in dict_data:
            self.type = dict_data[Global.TYPE]
        else:
            self.type = ""
        if Global.STATE in dict_data:
            self.state = dict_data[Global.STATE]
        else:
            self.state = ""
        if Global.MESSAGES in dict_data:
            msg_data = dict_data[Global.MESSAGES]
            if Global.COMMAND in msg_data:
                self.message_command = msg_data[Global.COMMAND]
            if Global.STATE in msg_data:
                self.message_state = msg_data[Global.STATE]
        self.blocks = []
        if Global.BLOCKS in dict_data:
            dict_blocks = dict_data[Global.BLOCKS]
            for block in dict_blocks:
                new_block = SignalBlock()
                new_block.load(block)
                self.blocks.append(new_block)

    def dump(self):
        """ dump a signal"""
        new_dict = {}
        new_dict[Global.NAME] = self.name
        new_dict[Global.DESCRIPTION] = self.description
        new_dict[Global.TYPE] = self.type
        new_dict[Global.STATE] = self.state
        new_dict_msg = {}
        new_dict_msg[Global.COMMAND] = self.message_command
        new_dict_msg[Global.STATE] = self.message_state
        new_dict[Global.MESSAGES] = new_dict_msg
        new_dict_blocks = []
        for block in self.blocks:
            dict_block = block.dump()
            new_dict_blocks.append(dict_block)
        new_dict['blocks'] = new_dict_blocks
        return new_dict

class Signals():
    """ A list of signals"""
    def __init__(self, log_queue, file_path=None):
        self.items = {}
        self.file_path = file_path
        self.log_queue = log_queue
        self.load_data(self.file_path)

    def load(self, dash_dict):
        """ Load data into the signals collection"""
        self.items = {}
        if Global.SIGNALS in dash_dict:
            dash_dict = dash_dict[Global.SIGNALS]
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
                new_item = Signal()
                new_item.load(data_item)
                self.items[new_item.name] = new_item

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
        """ Load  a list of signals"""
        if file_path is not None:
            if os.path.exists(file_path):
                with open(file_path) as json_file:
                    json_dict = json.load(json_file)
                    self.load(json_dict)

    def save_data(self, file_path):
        """ save signal list"""
        if file_path is not None:
            with open(file_path, 'w') as json_file:
                json.dump(self.dump(), json_file)
