#!/usr/bin/python3
# panels.py
"""

    panels.py - helper class to process panel definitions


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


class PanelColData(object):
    """ a column instance of layout panel """
    def __init__(self, init_map=None, col=0):
        self.col = col
        self.node = None
        self.port = None
        self.image = None
        self.type = None
        self.label = None
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a map return new class instance """
        self.col = map_body.get(Global.COL, 0)
        self.node = map_body.get(Global.NODE, None)
        self.port = map_body.get(Global.PORT, None)
        self.image = map_body.get(Global.IMAGE, None)
        self.type = map_body.get(Global.TYPE, None)
        self.label = map_body.get(Global.LABEL, None)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.col is not None:
            emap.update({Global.COL: self.col})
        if self.node is not None:
            emap.update({Global.NODE: self.node})
        if self.port is not None:
            emap.update({Global.PORT: self.port})
        if self.image is not None:
            emap.update({Global.IMAGE: self.image})
        if self.type is not None:
            emap.update({Global.TYPE: self.type})
        if self.label is not None:
            emap.update({Global.LABEL: self.label})
        return emap


class PanelRowData(object):
    """ a row of columns in a layout panel """
    def __init__(self, init_map=None, row=0):
        self.row = row
        self.cols = []
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a map return new class instance """
        self.row = map_body.get(Global.ROW, 0)
        self.cols = []
        for new_col in map_body.get(Global.COLS, []):
            new_col_data = PanelColData(new_col)
            self.cols.append(new_col_data)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.row is not None:
            emap.update({Global.ROW: self.row})
        if self.cols is not None:
            new_cols = []
            for col in self.cols:
                new_col = col.encode()
                new_cols.append(new_col)
            emap.update({Global.COLS: new_cols})
        return emap


class PanelData(object):
    """ a layout panel """
    def __init__(self, init_map=None, name=None):
        self.name = name
        self.description = None
        self.rows = []
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a map return new class instance """
        self.name = map_body.get(Global.NAME, None)
        self.description = map_body.get(Global.DESCRIPTION, None)
        self.rows = []
        for new_row in map_body.get(Global.ROWS, []):
            new_row_data = PanelRowData(new_row)
            self.rows.append(new_row_data)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.name is not None:
            emap.update({Global.NAME: self.name})
        if self.description is not None:
            emap.update({Global.DESCRIPTION: self.description})
        if self.rows is not None:
            new_rows = []
            for row in self.rows:
                new_row = row.encode()
                new_rows.append(new_row)
            emap.update({Global.ROWS: new_rows})
        return emap


class Panels(object):
    """ a layout """
    def __init__(self, init_map=None, name=None):
        self.name = name
        self.description = None
        self.rows = 0
        self.cols = 0
        self.panels = {}
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_map=None):
        """ parse a map return new class instance """
        map_body = map_map
        if isinstance(map_map, dict):
            root_key = list(map_map.keys())[0]
            map_body = map_map.get(root_key, [])
        self.name = map_body.get(Global.NAME, None)
        self.description = map_body.get(Global.DESCRIPTION, None)
        self.rows = map_body.get(Global.ROWS, 0)
        self.cols = map_body.get(Global.COLS, 0)
        self.panels = {}
        panels_list = map_body.get(Global.PANELS, [])
        for new_panel in panels_list:
            new_panel_data = PanelData()
            new_panel_data.parse(new_panel)
            # print(">>> panel: " + str(new_panel))
            self.panels.update({new_panel_data.name: new_panel_data})

    def encode(self):
        """ encode a map """
        emap = {}
        if self.name is not None:
            emap.update({Global.NAME: self.name})
        if self.description is not None:
            emap.update({Global.DESCRIPTION: self.description})
        if self.rows is not None:
            emap.update({Global.ROWS: self.rows})
        if self.cols is not None:
            emap.update({Global.COLS: self.cols})
        if self.panels is not None:
            new_panels = []
            for _key, panel_data in self.panels.items():
                new_panel = panel_data.encode()
                new_panels += [new_panel]
            emap.update({Global.PANELS: new_panels})
        return {Global.PANELS: emap}
