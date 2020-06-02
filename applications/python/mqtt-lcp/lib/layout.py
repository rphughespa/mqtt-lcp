# layout.py

"""

    layout.py - helper class to process layout panel definitions


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
import time

from global_constants import Global

class PanelCol():
    """ Class for a panel column in the layout"""

    def __init__(self, col_number="", col_id="", image="", ctype="", state=""):
        """ Initialize """
        self.col_number = col_number
        self.col_id = col_id
        self.image = image
        self.ctype = ctype
        self.state = state

    def load(self, data_dict):
        """ Load data into the column"""
        if Global.COL in data_dict:
            self.col_number = data_dict[Global.COL]
        else:
            self.col_number = ""
        if Global.ID in data_dict:
            self.col_id = data_dict[Global.ID]
        else:
            self.col_id = ""
        if Global.IMAGE in data_dict:
            self.image = data_dict[Global.IMAGE]
        else:
            self.image = ""
        if Global.TYPE in data_dict:
            self.ctype = data_dict[Global.TYPE]
        else:
            self.ctype = ""
        if Global.STATE in data_dict:
            self.state = data_dict[Global.STATE]
        else:
            self.state = ""

    def dump(self):
        """ Dump out the date in the column"""
        new_dict = {}
        new_dict[Global.COL] = self.col_number
        new_dict[Global.ID] = self.col_id
        new_dict[Global.IMAGE] = self.image
        new_dict[Global.TYPE] = self.ctype
        new_dict[Global.STATE] = self.state
        return new_dict

class PanelRow():
    """ CLas that define a row in the panel"""
    def __init__(self, row_number=""):
        self.row_number = row_number
        self.cols = []

    def load(self, dict_data):
        """ Load data into the row"""
        if Global.ROW in dict_data:
            self.row_number = dict_data[Global.ROW]
        else:
            self.row_number = ""
        self.cols = []
        if Global.COLS in dict_data:
            for col in dict_data['cols']:
                new_col = PanelCol()
                new_col.load(col)
                self.cols.append(new_col)

    def dump(self):
        """ Dump the data in the row"""
        new_dict = {}
        new_dict[Global.ROW] = self.row_number
        new_dict_cols = []
        for col in self.cols:
            new_dict_col = col.dump()
            new_dict_cols.append(new_dict_col)
        new_dict[Global.COLS] = new_dict_cols
        return new_dict

class Panel():
    """ Defines a panel for the layout"""

    def __init__(self, name="", description=""):
        self.name = name
        self.description = description
        self.rows = []

    def load(self, data_dict):
        """ Load data into the panel"""
        if Global.NAME in data_dict:
            self.name = data_dict[Global.NAME]
        else:
            self.description = ""
        if Global.DESCRIPTION in data_dict:
            self.description = data_dict[Global.DESCRIPTION]
        else:
            self.description = ""
        self.rows = []
        if Global.ROWS in data_dict:
            data_rows = data_dict[Global.ROWS]
            for data_row in data_rows:
                new_row = PanelRow()
                new_row.load(data_row)
                self.rows.append(new_row)

    def dump(self):
        """ Dump data from the panel"""
        new_dict = {}
        new_dict[Global.NAME] = self.name
        new_dict[Global.DESCRIPTION] = self.description
        new_dict_rows = []
        for row in self.rows:
            dict_row = row.dump()
            new_dict_rows.append(dict_row)
        new_dict[Global.ROWS] = new_dict_rows
        return new_dict


class Layout():
    """ Clas that defines the layout"""

    def __init__(self, log_queue, file_path=None, col_max="0", row_max="0"):
        self.items = {}
        self.name = ""
        self.description = ""
        self.col_max = col_max
        self.row_max = row_max
        self.file_path = file_path
        self.log_queue = log_queue
        self.load_data(self.file_path)

    def load(self, dash_dict):
        """ Load data into the layouts"""
        self.items = {}
        if Global.LAYOUT in dash_dict:
            dash_dict = dash_dict[Global.LAYOUT]
        if Global.NAME in dash_dict:
            self.name = dash_dict[Global.NAME]
        else:
            self.name = ""
        if Global.DESCRIPTION in dash_dict:
            self.description = dash_dict[Global.DESCRIPTION]
        else:
            self.description = ""
        if Global.COLS in dash_dict:
            self.max_cols = dash_dict[Global.COLS]
        else:
            self.max_cols = 0
        if Global.ROWS in dash_dict:
            self.max_rows = dash_dict[Global.ROWS]
        else:
            self.max_rows = 0
        if Global.ITEMS in dash_dict:
            data_items = dash_dict[Global.ITEMS]
            for data_item in data_items:
                new_item = Panel()
                new_item.load(data_item)
                self.items[new_item.name] = new_item

    def dump(self):
        """ Dump data from the panel"""
        new_dict = {}
        new_dict[Global.NAME] = self.name
        new_dict[Global.DESCRIPTION] = self.description
        new_dict[Global.COLS] = self.max_cols
        new_dict[Global.ROWS] = self.max_rows
        new_dict_items = []
        for _key, value in self.items.items():
            dict_item = value.dump()
            new_dict_items.append(dict_item)
        new_dict[Global.ITEMS] = new_dict_items
        return new_dict

    def load_data(self, file_path):
        """ Load dat into layout from a path"""
        if file_path is not None:
            if os.path.exists(file_path):
                with open(file_path) as json_file:
                    json_dict = json.load(json_file)
                    self.load(json_dict)

    def save_data(self, file_path):
        """ Save layout data to a file"""
        if file_path is not None:
            with open(file_path, 'w') as json_file:
                json.dump(self.dump(), json_file)
