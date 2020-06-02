# sensor.py

"""

    Sensor.py - helper class to process sensor reporting

The MIT License (MIT)

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

import os
import json
# import time

from global_constants import Global

class SensorItem():
    """ Class for a item in the sensor collection"""

    def __init__(self, node_id="", port_id="", reported="", stype="", timestamp=0):
        self.node_id = node_id
        self.port_id = port_id
        self.reported = reported
        self.type = stype
        self.timestamp = timestamp

    def load(self, data_dict):
        """ Load data into the item"""
        self.node_id = ""
        self.port_id = ""
        self.reported = ""
        self.type = ""
        self.timestamp = 0
        if Global.NODE_ID in data_dict:
            self.node_id = data_dict[Global.NODE_ID]
        if Global.PORT_ID in data_dict:
            self.port_id = data_dict[Global.PORT_ID]
        if Global.REPORTED in data_dict:
            self.reported = data_dict[Global.REPORTED]
        if Global.TYPE in data_dict:
            self.type = data_dict[Global.TYPE]
        if Global.TIMESTAMP in data_dict:
            self.timestamp = data_dict[Global.TIMESTAMP]

    def dump(self):
        """ Dump out the date in the column"""
        new_dict = {}
        new_dict[Global.NODE_ID] = self.node_id
        new_dict[Global.PORT_ID] = self.port_id
        new_dict[Global.REPORTED] = self.reported
        new_dict[Global.TYPE] = self.type
        new_dict[Global.TIMESTAMP] = self.timestamp
        return new_dict


class Sensors():
    """ Defines a collction of sensor sensors"""

    def __init__(self, log_queue, file_path=None, name="", description=""):
        self.name = name
        self.description = description
        self.items = {}
        self.file_path = file_path
        self.log_queue = log_queue
        self.load_data(self.file_path)

    def load(self, data_dict):
        """ Load data into the collection,replace exixting"""
        self.items = {}
        if Global.SENSORS in data_dict:
            dash_dict = data_dict[Global.SENSORS]
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
                    new_item = SensorItem()
                    new_item.load(data_item)
                    self.items[new_item.node_id+"/"+new_item.port_id] = new_item

    def update_items(self, data_items):
        """ Update list, add or change as needed """
        for data_item in data_items:
            new_item = SensorItem()
            new_item.load(data_item)
            self.update(node_id=new_item.node_id, port_id=new_item.port_id,
                    reported=new_item.reported, stype=new_item.type, timestamp=new_item.timestamp)

    def update(self, node_id, port_id, reported, stype, timestamp):
        """ update data """
        if node_id is not None and port_id is not None:
            # print("node: "+str(node_id))
            # print("port: "+str(port_id))
            key = node_id+"/"+port_id
            if key in self.items:
                item = self.items[key]
                if timestamp > item.timestamp:
                    item.timestamp = timestamp
                    item.reported = reported
            else:
                new_item = SensorItem(node_id=node_id, port_id=port_id,
                        reported=reported, stype=stype, timestamp=timestamp)
                self.items[key] = new_item

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
        """ Load dat into collection from a path"""
        if file_path is not None:
            if os.path.exists(file_path):
                with open(file_path) as json_file:
                    json_dict = json.load(json_file)
                    self.load(json_dict)

    def save_data(self, file_path):
        """ Save collection data to a file"""
        if file_path is not None:
            with open(file_path, 'w') as json_file:
                json.dump(self.dump(), json_file)
