#!/usr/bin/python3
# signal_rules.py
"""

    SignalRules.py - helper class to process rules for setting signals

    Stores the last reported  state of a sensor, switch, signal, etc.
    Note:  The state from "momentary" devices (rfid locator, buttons, etc) is not saved.
        Only the state of "persistant" devices (switches, signals,
            railcom locator, block, etc) are saved.


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

class SignalRuleClause(object):
    """ current state """

    def __init__(self, init_map=None):
        self.group = None
        self.node_id = None
        self.port_id = None
        self.key = None
        self.state = None
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a map return new class instance """
        # print(">>> sensor: " + str(map_body))
        self.group = map_body.get(Global.GROUP, None)
        self.node_id = map_body.get(Global.NODE_ID, None)
        self.port_id = map_body.get(Global.PORT_ID, None)
        self.key = SignalRule.build_key(self.group, self.node_id, self.port_id)
        self.state = map_body.get(Global.STATE, None)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.group is not None:
            emap.update({Global.GROUP: self.group})
        if self.node_id is not None:
            emap.update({Global.NODE_ID: self.node_id})
        if self.port_id is not None:
            emap.update({Global.PORT_ID: self.port_id})
        if self.state is not None:
            emap.update({Global.STATE: self.state})
        return (emap)

class SignalRule(object):
    """ a group of sensor states data items"""

    def __init__(self, init_list=None):
        self.clauses = []
        if init_list is not None:
            self.parse(init_list)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    @classmethod
    def build_key(cls, group, node, port):
        """ build a signale rule key """
        key = ""
        if group is not None:
            key += str(group)
        key += ":"
        if node is not None:
            key += str(node)
        key += ":"
        if port is not None:
            key += str(port)
        return key

    def parse(self, list_body=None):
        """ parse a list return new class instance """

        if list_body is not None:
            for signal_clause in list_body:
                item = SignalRuleClause(signal_clause)
                self.clauses.append(item)

    def encode(self):
        """ encode a list """
        emap = []
        if self.clauses is not None:
            new_signal_rule_clause_items = []
            for signal_rule_clause in self.clauses:
                new_item = signal_rule_clause.encode()
                new_signal_rule_clause_items.append(new_item)
            emap = new_signal_rule_clause_items
        return emap

class Signal(object):
    """ a signal """

    def __init__(self, init_map=None):
        self.node_id = None
        self.port_id = None
        self.key = None
        self.block_id = None
        self.block_direction = None
        self.clear_rules = None  # a list of rules
        self.approach_rules = None  # a list of rules
        if init_map is not None:
            self.parse(init_map)
            # signal rule: "+str(self.node_id)+" : "+str(self.port_id))
            #print(">>> ... clear: " +str(self.clear_rules))
            #print(">>> ... approach: " +str(self.approach_rules))

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a list return new class instance """
        self.group = map_body.get(Global.GROUP, None)
        self.node_id = map_body.get(Global.NODE_ID, None)
        self.port_id = map_body.get(Global.PORT_ID, None)
        self.key = SignalRule.build_key(self.group, self.node_id, self.port_id)
        self.block_id = map_body.get(Global.BLOCK_ID, None)
        self.block_direction = map_body.get(Global.DIRECTION, None)
        rules = map_body.get(Global.RULES, None)
        if rules is not None:
            clear_rules = rules.get(Global.CLEAR, None)
            if clear_rules is None:
                self.clear_rules = None
            else:
                self.clear_rules = {}
                for rule_id, rule in clear_rules.items():
                    self.clear_rules.update({rule_id: SignalRule(rule)})
            approach_rules = rules.get(Global.APPROACH, None)
            if approach_rules is None:
                self.approach_rules = None
            else:
                self.approach_rules = {}
                for rule_id, rule in approach_rules.items():
                    self.approach_rules.update({rule_id: SignalRule(rule)})

    def encode(self):
        """ encode a list """
        emap = {}
        if self.group is not None:
            emap.update({Global.GROUP: self.group})
        if self.node_id is not None:
            emap.update({Global.NODE_ID: self.node_id})
        if self.port_id is not None:
            emap.update({Global.PORT_ID: self.port_id})
        if self.block_id is not None:
            emap.update({Global.BLOCK_ID: self.block_id})
        if self.block_direction is not None:
            emap.update({Global.DIRECTION: self.block_direction})
        signal_rules = {}
        if self.clear_rules is not None:
            rules = {}
            for rule_id, rule in self.clear_rules.items():
                rules.update({rule_id: rule.encode})
            signal_rules.update({Global.CLEAR: rules})
        if self.approach_rules is not None:
            rules = {}
            for rule_id, rule in self.approach_rules.items():
                rules.update({rule_id: rule.encode})
            signal_rules.update({Global.APPROACH: rules})
        emap.update({Global.RULES: signal_rules})
        return emap


    #
    # private functions
    #
