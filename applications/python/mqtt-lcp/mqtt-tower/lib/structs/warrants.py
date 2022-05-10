#!/usr/bin/python3
# warrants.py
"""

    warrants.py - helper class to process warrants definitions


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


class WarrantBlockData(object):
    """ a block in a warrant """
    def __init__(self, init_map=None):
        self.switch = None
        self.state = None
        self.block = None
        self.signal = None
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a map return new class instance """
        self.switch = map_body.get(Global.SWITCH, None)
        self.state = map_body.get(Global.STATE, None)
        self.block = map_body.get(Global.BLOCK, None)
        self.signal = map_body.get(Global.SIGNAL, None)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.switch is not None:
            emap.update({Global.SWITCH: self.switch})
        if self.state is not None:
            emap.update({Global.STATE: self.state})
        if self.block is not None:
            emap.update({Global.BLOCK: self.block})
        if self.signal is not None:
            emap.update({Global.SIGNAL: self.signal})
        return emap


class WarrantData(object):
    """ status of a Warrant """
    def __init__(self, init_map=None):
        self.name = None
        self.description = None
        self.reported = None
        self.command_topic = None
        self.data_topic = None
        self.blocks = []
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
        self.reported = map_body.get(Global.REPORTED, None)
        self.command_topic = map_body.get(Global.COMMAND_TOPIC, None)
        self.data_topic = map_body.get(Global.DATA_TOPIC, None)
        self.blocks = []
        block_map = map_body.get(Global.BLOCKS, [])
        for new_block in block_map:
            new_block_data = WarrantBlockData(new_block)
            self.blocks.append(new_block_data)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.name is not None:
            emap.update({Global.NAME: self.name})
        if self.description is not None:
            emap.update({Global.DESCRIPTION: self.description})
        if self.reported is not None:
            emap.update({Global.REPORTED: self.reported})
        if self.command_topic is not None:
            emap.update({Global.COMMAND_TOPIC: self.command_topic})
        if self.data_topic is not None:
            emap.update({Global.DATA_TOPIC: self.data_topic})
        if self.blocks is not None:
            block_list = []
            for block in self.blocks:
                block_data = block.encode()
                block_list.append(block_data)
            emap.update({Global.BLOCKS: block_list})
        return emap


class Warrants(object):
    """ a group of warrants """
    def __init__(self, init_map=None):
        self.name = None
        self.description = None
        self.warrants = {}
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
        self.warrants = {}
        warrants_list = map_body.get(Global.WARRANTS, [])
        for warrant_data in warrants_list:
            new_warrant_data = WarrantData(warrant_data)
            self.warrants.update({new_warrant_data.name: new_warrant_data})

    def encode(self):
        """ encode a map """
        emap = {}
        if self.name is not None:
            emap.update({Global.NAME: self.name})
        if self.description is not None:
            emap.update({Global.DESCRIPTION: self.description})
        if self.warrants is not None:
            new_warrants = []
            for _warrant_key, warrant_data in self.warrants.items():
                new_warrants+= [warrant_data.encode()]
            emap.update({Global.WARRANTS: new_warrants})
        return {Global.WARRANTS: emap}
