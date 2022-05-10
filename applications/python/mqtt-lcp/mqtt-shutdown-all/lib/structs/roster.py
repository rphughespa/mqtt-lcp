#!/usr/bin/python3
# rosterpy
"""

    roster - class that is used when passing locodata between modules

The MIT License (MIT)

Copyright 2021 richard p hughes

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


class LocoFunctionData(object):
    """ Data class for loco functions """
    def __init__(self, init_map=None):
        self.number = None
        self.name = None
        self.label = None
        self.type = None
        self.state = None
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a map """
        self.name = map_body.get(Global.NAME, None)
        self.label = map_body.get(Global.LABEL, None)
        self.type = map_body.get(Global.TYPE, None)
        self.state = map_body.get(Global.STATE, None)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.name is not None:
            emap.update({Global.NAME: self.name})
        if self.label is not None:
            emap.update({Global.LABEL: self.label})
        if self.type is not None:
            emap.update({Global.TYPE: self.type})
        if self.state is not None:
            emap.update({Global.STATE: self.state})
        return emap


class LocoData(object):
    """ Data class for loco specific data """
    def __init__(self, init_map=None, name=None):
        self.name = name
        self.description = None
        self.dcc_id = None
        self.rfid_id = None
        self.max_speedstep = 128
        self.image = None
        self.source = "manual"
        self.functions = {}
        self.slot = -1
        # in consist loco is facing the opposite direction of lead loco
        self.is_direction_normal = True
        self.apply_functions = True
        self.speed = 0  # current speed
        self.direction_is_reversed = False  # current direction of travel
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def initialize_loco(self, loco_dict=None):
        """ parse a dictionary of parameters """
        # {dcc_id: 1234, name: "prr gg1 green 1234", direction:"reverse", function:"true"}
        self.initialize_functions()
        reported = Global.ERROR
        message = ""
        if Global.DCC_ID in loco_dict:
            self.dcc_id = loco_dict[Global.DCC_ID]
        if Global.NAME in loco_dict:
            self.name = loco_dict[Global.NAME]
        if Global.DIRECTION in loco_dict:
            direction = loco_dict[Global.DIRECTION]
            if direction == Global.REVERSE:
                self.is_direction_normal = False
        if Global.FUNCTIONS in loco_dict:
            functions = loco_dict[Global.FUNCTIONS]
            if functions == Global.FALSE:
                self.apply_functions = False
        if self.name is None:
            if self.dcc_id is not None:
                self.name = self.dcc_id
        if self.dcc_id is not None:
            reported = "ok"
        else:
            message = Global.MSG_ERROR_NO_DCC_ID + str(loco_dict)
        return reported, message

    def initialize_functions(self):
        """ initial function to off """
        self.functions = {}
        for func in range(0, 29):  # functons 0..28
            self.functions["f"+str(func)] =  LocoFunctionData()

    def parse(self, map_body=None):
        """ parse a map return new class instance """
        self.name = map_body.get(Global.NAME, None)
        self.description = map_body.get(Global.DESCRIPTION, None)
        self.dcc_id = map_body.get(Global.DCC_ID, None)
        self.rfid_id = map_body.get(Global.RFID_ID, None)
        self.max_speedstep = map_body.get(Global.MAX_SPEEDSTEP, None)
        self.image = map_body.get(Global.IMAGE)
        self.functions = {}
        functions_map = map_body.get(Global.FUNCTIONS, {})
        for function_key, function_data in functions_map.items():
            self.functions.update(
                {function_key: LocoFunctionData(function_data)})
        # print(">>>loco: "+str(self.name))

    def encode(self):
        """ encode a map """
        emap = {}
        if self.name is not None:
            emap.update({Global.NAME: self.name})
        if self.description is not None:
            emap.update({Global.DESCRIPTION: self.description})
        if self.dcc_id is not None:
            emap.update({Global.DCC_ID: self.dcc_id})
        if self.rfid_id is not None:
            emap.update({Global.RFID_ID: self.rfid_id})
        if self.max_speedstep is not None:
            emap.update({Global.MAX_SPEEDSTEP: self.max_speedstep})
        if self.image is not None:
            emap.update({Global.IMAGE: self.image})
        if self.functions is not None:
            funcs = {}
            for function_key, function_data in self.functions.items():
                funcs.update({function_key: function_data.encode()})
            emap.update({Global.FUNCTIONS: funcs})
        return emap


class ConsistLoco(object):
    """data class for a loco in a consist"""
    def __init__(self, init_map=None):
        self.dcc_id = None
        self.direction = None
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a consist loco """
        self.dcc_id = map_body.get(Global.DCC_ID, None)
        self.direction = map_body.get(Global.DIRECTION, None)

    def encode(self):
        """ encode a consist loco """
        emap = {}
        if self.dcc_id is not None:
            emap.update({Global.DCC_ID: self.dcc_id})
        if self.direction is not None:
            emap.update({Global.DIRECTION: self.direction})
        return emap


class ConsistData(object):
    """ Data class for consist specific data """
    def __init__(self, init_map=None, name=None):
        self.name = name
        self.description = None
        self.dcc_id = None
        self.locos = []
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
        self.dcc_id = map_body.get(Global.DCC_ID, None)
        self.locos = []
        locos_list = map_body.get(Global.LOCOS, [])
        for loco_data in locos_list:
            loco = ConsistLoco(loco_data)
            self.locos.append(loco)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.name is not None:
            emap.update({Global.NAME: self.name})
        if self.description is not None:
            emap.update({Global.DESCRIPTION: self.description})
        if self.dcc_id is not None:
            emap.update({Global.DCC_ID: self.dcc_id})
        if self.locos is not None:
            locos = []
            for loco in self.locos:
                loco_map = loco.encode()
                locos.append(loco_map)
            emap.update({Global.LOCOS: locos})
        return emap


class CabData(object):
    """ class representing a cab: one or mor loces manipulated as one """
    def __init__(self, cab_id=None):
        self.cab_id = cab_id
        self.locos = {}
        self.locos_by_seq = []

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def add_loco(self, loco_data=None):
        """ initilaize a loco """
        self.locos[loco_data.name] = loco_data
        if not loco_data.name in self.locos_by_seq:
            self.locos_by_seq.append(loco_data.name)

    def remove_a_loco(self, name=None):
        """ remove a loco from cab  """
        self.locos_by_seq.remove(name)
        del self.locos[name]


class ThrottleData(object):
    """ Data class for throtle specific data """
    def __init__(self, throttle_id=None):
        self.name = throttle_id
        self.description = None
        self.throttle_id = throttle_id
        self.timestamp = 0
        self.cabs = {}

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"


class Roster(object):
    """ Data class for roster specific data """
    def __init__(self, init_map=None):
        self.name = None
        self.description = None
        self.locos = {}
        self.consists = {}
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_map=None):
        """ parse a map return new class instance """
        # print(">>> roster map: " + str(map_map))
        map_body = map_map
        #if isinstance(map_map, dict):
        #    root_key = list(map_map.keys())[0]
        #    map_body = map_map.get(root_key, [])
        map_body = map_map.get(Global.ROSTER, {})
        self.name = map_body.get(Global.NAME, None)
        self.description = map_body.get(Global.DESCRIPTION, None)
        self.locos = {}
        locos_map = map_body.get(Global.LOCOS, {})
        for loco_key, loco_data in locos_map.items():
            self.locos.update({loco_key: LocoData(loco_data)})
        self.consists = {}
        consists_map = map_body.get(Global.CONSISTS, {})
        for consist_key, consist_data in consists_map.items():
            self.consists.update({consist_key: ConsistData(consist_data)})

    def encode(self):
        """ encode a map """
        emap = {}
        if self.name is not None:
            emap.update({Global.NAME: self.name})
        if self.description is not None:
            emap.update({Global.DESCRIPTION: self.description})
        if self.locos is not None:
            locos_map = {}
            for loco_key, loco_data in self.locos.items():
                locos_map.update({loco_key: loco_data.encode()})
            emap.update({Global.LOCOS: locos_map})
        if self.consists is not None:
            consists_map = {}
            for consist_key, consist_data in self.consists.items():
                consists_map.update({consist_key: consist_data.encode()})
            emap.update({Global.CONSISTS: consists_map})
        return {Global.ROSTER: emap}
