# warrants.py - a dictionary of warrants

"""

    warrant.py - helper class to process warrant definitions

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

class WarrantPathBlock():
    """ A class to manage a warrant path block"""

    def __init__(self, name="", state=""):
        """ Initialize"""
        self.name = name
        self.state = state

    def load(self, dict_data):
        """ load data"""
        if Global.STATE in dict_data:
            self.state = dict_data[Global.STATE]
        else:
            self.state = ""

    def dump(self):
        """ dump data """
        new_dict = {}
        new_dict[Global.NAME] = self.name
        new_dict[Global.STATE] = self.state
        return new_dict

class WarrantPathSignal():
    """ A class to manage warrant path signals"""

    def __init__(self, name="", state=""):
        """ Initialize"""
        self.name = name
        self.state = state

    def load(self, dict_data):
        """ load adat"""
        if Global.NAME in dict_data:
            self.name = dict_data[Global.NAME]
        else:
            self.name = ""
        if Global.STATE in dict_data:
            self.state = dict_data[Global.STATE]
        else:
            self.state = ""

    def dump(self):
        """ dump data"""
        new_dict = {}
        new_dict[Global.NAME] = self.name
        new_dict[Global.STATE] = self.state
        return new_dict

class WarrantPath():
    """ A class to manag a warrant path"""

    def __init__(self, block=None, signal=None, state=""):
        """ Initialize"""
        self.block = block
        self.signal = signal
        self.state = state

    def load(self, dict_data):
        """ load data"""
        if Global.BLOCK in dict_data:
            self.block = WarrantPathBlock()
            self.block.load(dict_data[Global.BLOCK])
        else:
            self.block = None
        if Global.SIGNAL in dict_data:
            self.signal = WarrantPathSignal()
            self.signal.load(dict_data[Global.SIGNAL])
        else:
            self.signal = None

    def dump(self):
        """ dump data"""
        new_dict = {}
        new_dict[Global.STATE] = self.state
        if self.block is not None:
            new_dict[Global.BLOCK] = self.block.dump()
        if self.signal is not None:
            new_dict[Global.SIGNAL] = self.signal.dump()
        return new_dict

class Warrant():
    """ A class to manage a warrant"""

    def __init__(self, name="", description="", state=""):
        """ Initialize"""
        self.name = name
        self.description = description
        self.state = state
        self.paths = []

    def load(self, dict_data):
        """ load data"""
        if Global.NAME in dict_data:
            self.name = dict_data[Global.NAME]
        else:
            self.name = ""
        if Global.DESCRIPTION in dict_data:
            self.description = dict_data[Global.DESCRIPTION]
        else:
            self.description = ""
        self.paths = []
        if Global.PATHS in dict_data:
            path_list = dict_data[Global.PATHS]
            for path in path_list:
                new_path = WarrantPath()
                new_path.load(path)
                self.paths.append(new_path)

    def dump(self):
        """ dump data"""
        new_dict = {}
        new_dict[Global.NAME] = self.name
        new_dict[Global.DESCRIPTION] = self.description
        new_dict_paths = []
        for path in self.paths:
            new_dict_path = path.dump()
            new_dict_paths.append(new_dict_path)
        new_dict[Global.PATHS] = new_dict_paths
        return new_dict

class Warrants():
    """ A class to manage a list of warrants"""
    def __init__(self, log_queue, file_path=None):
        self.items = {}
        self.file_path = file_path
        self.log_queue = log_queue
        self.load_data(self.file_path)

    def load(self, dash_dict):
        """ Load data into the dashboard"""
        self.items = {}
        if Global.WARRANTS in dash_dict:
            dash_dict = dash_dict[Global.WARRANTS]
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
                new_item = Warrant()
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
        """ load data"""
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
