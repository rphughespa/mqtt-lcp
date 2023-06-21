#!/usr/bin/python3
# routes.py
"""

    Routeses.py - helper class to process routes


The MIT License (MIT)

Copyright  2023 richard p hughes

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

class RouteSwitch(object):
    """ switches related to a route """

    def __init__(self, init_map=None):
        self.node_id = None
        self.port_id = None
        self.command_topic = None
        self.desired =  None
        self.key = None
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a map return new class instance """
        # print(">>> sensor: " + str(map_body))
        self.node_id = map_body.get(Global.NODE_ID, None)
        self.port_id = map_body.get(Global.PORT_ID, None)
        self.command_topic = map_body.get(Global.COMMAND_TOPIC, None)
        self.desired = map_body.get(Global.DESIRED, None)
        self.key = str(self.node_id) + ":" + str(self.port_id)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.node_id is not None:
            emap.update({Global.NODE_ID: self.node_id})
        if self.port_id is not None:
            emap.update({Global.PORT_ID: self.port_id})
        if self.command_topic is not None:
            emap.update({Global.COMMAND_TOPIC: self.command_topic})
        if self.desired is not None:
            emap.update({Global.DESIRED: self.desired})
        return (emap)

class Route(object):
    """ a group of sensor states data items"""

    def __init__(self, init_map=None):
        self.port_id = None
        self.description = None
        self.switches = {}
        self.state = Global.UNKNOWN
        self.key = None
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    @classmethod
    def build_key(cls, node_id, port_id):
        """ build route key """
        return str(node_id)+ ":" + str(port_id)

    def parse(self, map_body=None):
        """ parse a list return new class instance """
        self.node_id = map_body.get(Global.NODE_ID, None)
        self.port_id = map_body.get(Global.PORT_ID, None)
        self.description = map_body.get(Global.DESCRIPTION, None)
        self.key = Route.build_key(self.node_id, self.port_id)
        self.switches = {}
        switches = map_body.get(Global.SWITCH, None)
        if switches is not None:
            for sw in switches:
                switch = RouteSwitch(sw)
                self.switches.update({switch.key: switch})

    def encode(self):
        """ encode a route """
        emap = {}
        if self.node_id is  not None:
            emap.update({Global.NODE_ID: self.node_id})
        if self.port_id is  not None:
            emap.update({Global.PORT_ID: self.port_id})
        if self.description is  not None:
            emap.update({Global.DESCRIPTION: self.description})
        if self.switches is not None and \
                len(self.switches) > 0:
            switch_list = []
            for _key, switch in self.switches:
                eswitch = switch.encode()
                switch_list.append(eswitch)
            emap.update({Global.SWITCH: switch_list})

        return emap


    #
    # private functions
    #
