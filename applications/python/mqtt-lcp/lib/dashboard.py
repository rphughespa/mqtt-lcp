# dashboard.py

"""

    dashboard.py - helper class to process dashboard panel definitions


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

class DashboardItem():
    """ Class for a item in the dashboard"""

    def __init__(self, node_id="", timestamp=0, state=""):
        self.node_id = node_id
        self.timestamp = timestamp
        self.state = state

    def load(self, data_dict):
        """ Load data into the item"""
        if Global.NODE_ID in data_dict:
            self.node_id = data_dict[Global.NODE_ID]
        else:
            self.node_id = ""
        if Global.TIMESTAMP in data_dict:
            self.timestamp = data_dict[Global.TIMESTAMP]
        else:
            self.timestamp = ""
        if Global.STATE in data_dict:
            self.state = data_dict[Global.STATE]
        else:
            self.state = ""

    def dump(self):
        """ Dump out the date in the column"""
        new_dict = {}
        new_dict[Global.NODE_ID] = self.node_id
        new_dict[Global.TIMESTAMP] = self.timestamp
        new_dict[Global.STATE] = self.state
        return new_dict

class Dashboard():
    """ Defines a dashboard"""

    def __init__(self, log_queue, file_path=None, name="", description=""):
        self.name = name
        self.description = description
        self.items = {}
        self.file_path = file_path
        self.log_queue = log_queue
        self.load_data(self.file_path)

    def load(self, dash_dict):
        """ Load data into the dashboard"""
        self.items = {}
        if Global.DASHBOARD in dash_dict:
            dash_dict = dash_dict[Global.DASHBOARD]
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
                new_item = DashboardItem()
                new_item.load(data_item)
                self.items[new_item.node_id] = new_item

    def get_timestamp(self, node_id):
        """ get timestamp of a dashboard item """
        timestamp = 0  # node_id not in dashboard
        if node_id in self.items:
            timestamp = self.items[node_id].timestamp
        return timestamp

    def update(self, node_id, timestamp, state):
        """ update data """
        if node_id is not None:
            if node_id in self.items:
                self.items[node_id].timestamp = timestamp
                self.items[node_id].state = state
            else:
                new_item = DashboardItem(node_id=node_id, timestamp=timestamp, state=state)
                self.items[node_id] = new_item

    def update_states(self, timestamp_error):
        """ check for expired timestamps"""
        # print("dashboard: "+str(timestamp_error))
        for _key, value in self.items.items():
            #print(key+" : "+str(value.timestamp))
            if value.timestamp < timestamp_error:
                value.state = Global.ERROR
            else:
                value.state = Global.RUN
            #print(" ... "+ value.state)

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
        """ Load dat into dashboard from a path"""
        if file_path is not None:
            if os.path.exists(file_path):
                with open(file_path) as json_file:
                    json_dict = json.load(json_file)
                    self.load(json_dict)

    def save_data(self, file_path):
        """ Save dashboard data to a file"""
        if file_path is not None:
            with open(file_path, 'w') as json_file:
                json.dump(self.dump(), json_file)
