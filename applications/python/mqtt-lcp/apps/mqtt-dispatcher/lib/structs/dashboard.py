#!/usr/bin/python3
# dashboard.py
"""

    dashboard.py - helper class to process dashboard panel definitions


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


class NodeData(object):
    """ status of a node """
    def __init__(self, init_map=None, node_id=None):
        self.node_id = node_id
        self.description = None
        self.timestamp = 0
        self.state = Global.ERROR
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        #return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"


    def parse(self, map_body=None):
        """ parse a map return new class instance """
        self.node_id = map_body.get(Global.NODE_ID, None)
        self.description = map_body.get(Global.DESCRIPTION, None)
        self.timestamp = map_body.get(Global.TIMESTAMP, 0)
        self.state = map_body.get(Global.STATE, Global.ERROR)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.node_id is not None:
            emap.update({Global.NODE_ID: self.node_id})
        if self.description is not None:
            emap.update({Global.DESCRIPTION: self.description})
        if self.timestamp is not None:
            emap.update({Global.TIMESTAMP: self.timestamp})
        if self.state is not None:
            emap.update({Global.STATE: self.state})
        key = self.node_id
        return (key, emap)


class Dashboard(object):
    """ dashboard of node states """
    def __init__(self, init_map=None):
        self.nodes = {}
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        #return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_map=None):
        """ parse a map return new class instance """
        map_body = map_map.get(Global.DASHBOARD, map_map)
        nodes_body = map_body.get(Global.NODES, map_body)
        self.nodes = {}
        for key, node_data in nodes_body.items():
            new_node = NodeData(node_data)
            new_node.node_id = key
            self.nodes.update({key: new_node})

    def encode(self):
        """ encode a list """
        emap = []
        if self.nodes is not None:
            new_nodes = {}
            for _node_key, node_data in self.nodes.items():
                (key, new_node) = node_data.encode()
                new_nodes.update({key: new_node})
            emap = new_nodes
        return {
            Global.DASHBOARD: {
                Global.DESCRIPTION: "Dashboard",
                Global.NODES: emap
            }
        }

    def update_node_state(self, node_id, new_state, new_timestamp):
        """ update the state of a node, add node if not present  """
        node_activated = False
        dashboard_node = self.nodes.get(node_id, None)
        if dashboard_node is None:
            dashboard_node = NodeData()
            dashboard_node.node_id = node_id
            self.nodes.update({node_id: dashboard_node})
        if dashboard_node.state != Global.ACTIVE and \
                new_state == Global.ACTIVE:
            node_activated = True
        dashboard_node.state = new_state
        dashboard_node.timestamp = new_timestamp
        return node_activated

    def timeout_nodes(self, timeout_milliseconds):
        """ mark nodes as ERROR if they have not pinged since this time """
        if self.nodes is not None:
            for _node_key, node_data in self.nodes.items():
                # print(">>> timeout: " + str(node_data.timestamp) + " ... " + str(timeout_milliseconds))
                if node_data.timestamp < timeout_milliseconds:
                    node_data.state = Global.ERROR
