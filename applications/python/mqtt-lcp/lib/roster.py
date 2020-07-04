# roster.py - manages a dictionary of locos


"""

    roster.py - helper class to process loco roster definitions

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
#import time

from global_constants import Global

class LocoFunction():
    """ Loco functios class"""

    def __init__(self, name="", label="", ftype="", state=""):
        self.name = name
        self.label = label
        self.type = ftype
        self.state = state

    def load(self, dict_data):
        """ Load functions """
        if Global.LABEL in dict_data:
            self.label = dict_data[Global.LABEL]
        else:
            self.label = ""
        if Global.TYPE in dict_data:
            self.type = dict_data[Global.TYPE]
        else:
            self.type = ""
        if Global.STATE in dict_data:
            self.state = dict_data[Global.STATE]
        else:
            self.state = "unknown"

    def dump(self):
        """ Dump functions"""
        new_dict = {}
        new_dict[Global.LABEL] = self.label
        new_dict[Global.TYPE] = self.type
        new_dict["state"] = self.state
        return new_dict


class Loco():
    """ Class  to store infor about locos"""

    def __init__(self, name="", description="", id_dcc="", id_rfid="", image=None, max_speedstep=""):
        self.name = name
        self.description = description
        self.id_dcc = id_dcc
        self.id_rfid = id_rfid
        self.max_speedstep = max_speedstep
        self.image = image
        self.functions = {}

    def add_function(self, name, label, ftype, state):
        """ Add a function to loco"""
        new_func = {Global.LABEL: label, Global.TYPE: ftype, Global.STATE: state}
        self.functions[name] = new_func

    def get_function(self, name):
        """ Get loco functions"""
        func = None
        if name in self.functions:
            func = self.functions[name]
        return func

    def set_function_state(self, name, new_state):
        """ set function state"""
        if name in self.functions:
            self.functions[name][Global.STATE] = new_state

    def load(self, dict_data):
        """ Load locos"""
        self.functions = {}
        self.name = ""
        self.description = ""
        self.max_speedstep = ""
        if Global.NAME in dict_data:
            self.name = dict_data[Global.NAME]
        if Global.DESCRIPTION in dict_data:
            self.description = dict_data[Global.DESCRIPTION]
        if Global.MAX_SPEEDSTEP in dict_data:
            self.max_speedstep = dict_data[Global.MAX_SPEEDSTEP]
        self.id_dcc = ""
        self.id_rfid = ""
        if Global.IDS in dict_data:
            for id_key, id_value in dict_data[Global.IDS].items():
                if id_key == Global.DCC:
                    self.id_dcc = id_value
                if id_key == Global.RFID:
                    self.id_rfid = id_value
        self.functions = {}
        for fkey, fvalue in dict_data[Global.FUNCTIONS].items():
            new_function = LocoFunction(name=fkey)
            new_function.load(fvalue)
            self.functions[fkey] = new_function

    def dump(self):
        """ Dump Loco"""
        new_dict = {}
        new_dict[Global.NAME] = self.name
        new_dict[Global.DESCRIPTION] = self.description
        new_dict[Global.MAX_SPEEDSTEP] = self.max_speedstep
        new_dict_ids = {}
        new_dict_ids[Global.DCC] = self.id_dcc
        new_dict_ids[Global.RFID] = self.id_rfid
        new_dict[Global.IDS] = new_dict_ids
        new_functions = {}
        for fkey, fvalue in self.functions.items():
            new_function_dict = fvalue.dump()
            new_functions[fkey] = new_function_dict
        new_dict[Global.FUNCTIONS] = new_functions
        return new_dict

class Roster():
    """ Mainitain a list roster of locoa"""

    def __init__(self, log_queue, file_path=None):
        self.items = {}
        self.name = ""
        self.description = ""
        self.file_path = file_path
        self.log_queue = log_queue
        self.load_data(self.file_path)

    def load(self, dash_dict):
        """ Load roster"""
        self.items = {}
        if Global.ROSTER in dash_dict:
            dash_dict = dash_dict[Global.ROSTER]
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
                new_item = Loco()
                new_item.load(data_item)
                self.items[new_item.name] = new_item

    def dump(self):
        """ Dump locos"""
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
        """ Save data"""
        if file_path is not None:
            with open(file_path, 'w') as json_file:
                json.dump(self.dump(), json_file)
