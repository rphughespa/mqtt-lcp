#!/usr/bin/python3
# signal_rules.py
"""

    SignalRules.py - helper class to process rules for setting signals

    Stores the last reported  state of a sensor, switch, signal, etc.
    Note:  The state from "momentary" devices (rfid locator, buttons, etc) is not saved.
        Only the state of "persistant" devices (switches, signals, railcom locator, block, etc) are saved.


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

class SignalRuleClause(object):
    """ current state """

    def __init__(self, init_map=None):
        self.key = None
        self.node_id = None
        self.port_id = None
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
        self.node_id = map_body.get(Global.NODE_ID, None)
        self.port_id = map_body.get(Global.PORT_ID, None)
        self.state = map_body.get(Global.STATE, None)
        self.key = str(self.node_id) + ":" + str(self.port_id)

    def encode(self):
        """ encode a map """
        emap = {}
        if self.node_id is not None:
            emap.update({Global.NODE_ID: self.node_id})
        if self.port_id is not None:
            emap.update({Global.PORT_ID: self.port_id})
        if self.state is not None:
            emap.update({Global.STATE: self.state})
        return (self.key, emap)


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
        self.key = None
        self.node_id = None
        self.port_id = None
        self.block_node_id = None
        self.block_port_id = None
        self.block_direction = None
        self.clear_rules = None  # a list of rules
        self.stop_rules = None  # a list of rules
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_body=None):
        """ parse a list return new class instance """
        self.node_id = map_body.get(Global.NODE_ID, None)
        self.port_id = map_body.get(Global.PORT_ID, None)
        block = map_body.get(Global.BLOCK, None)
        if block is None:
            self.block_node_id = None
            self.block_port_id = None
            self.block_direction = None
        else:
            self.block_node_id = block.get(Global.NODE_ID, None)
            self.block_port_id = block.get(Global.PORT_ID, None)
            self.block_direction = block.get(Global.DIRECTION, None)
        clear_rules = map_body.get(Global.CLEAR, None)
        if clear_rules is None:
            self.clear_rules = None
        else:
            self.clear_rules = []
            for rule in clear_rules:
                self.clear_rules.append(SignalRule(rule))
        stop_rules = map_body.get(Global.STOP, None)
        if stop_rules is None:
            self.stop_rules = None
        else:
            self.stop_rules = []
            for rule in stop_rules:
                self.stop_rules.append(SignalRule(rule))
        self.key = str(self.node_id) + ":" + str(self.port_id)

    def encode(self):
        """ encode a list """
        emap = {}
        if self.node_id is not None:
            emap.update({Global.NODE_ID: self.node_id})
        if self.port_id is not None:
            emap.update({Global.PORT_ID: self.port_id})
        if self.block_node_id is not None or \
                self.block_port_id is not None or \
                self.block_direction is not None:
            block_map = {}
            if self.block_node_id is not None:
                block_map.update({Global.NODE_ID: self.block_node_id})
            if self.block_port_id is not None:
                block_map.update({Global.NODE_ID: self.block_port_id})
            if self.block_direction is not None:
                block_map.update({Global.NODE_ID: self.block_direction})
            emap.update({Global.BLOCK: block_map})
        if self.clear_rules is not None:
            rules = []
            for rule in self.clear_rules:
                rules.append(rule.encode)
            emap.update({Global.CLEAR: rules})
        if self.stop_rules is not None:
            rules = []
            for rule in self.stop_rules:
                rules.append(rule.encode)
            emap.update({Global.STOP: rules})
        return emap


class SignalRules(object):
    """ a groups of sensor state data items"""

    def __init__(self, init_map=None):
        self.signals = None
        self.block_signals = {}
        self.sensor_signals = {}
        if init_map is not None:
            self.parse(init_map)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def parse(self, map_map=None):
        """ parse a map return new class instance """
        # print("\n\n>>> signals map: " + str(map_map))
        signal_rules_map = map_map.get(Global.SIGNAL_RULES, None)
        if signal_rules_map is not None:
            signals_list = signal_rules_map.get(Global.SIGNALS, None)
            # print("\n\n>>> signals list: " + str(signals_list))
            if signals_list is not None:
                self.signals = {}
                for sig in signals_list:
                    signal = Signal(sig)
                    self.signals.update({signal.key: signal})

    def encode(self):
        """ encode a map """
        emap = {}
        if self.signals is not None:
            sigs = []
            for _sig_key, sig in self.signals.items():
                sig_map = sig.encode()
                sigs.append(sig_map)
            emap.update({Global.SIGNAL_RULES: sigs})
        # print(">>> sensor state groups encoded: " + str(emap))
        return emap

    def build_block_signals(self):
        """ build map of block and the signals they contain """
        self.block_signals = {}
        if self.signals is not None:
            for signal_key, signal in self.signals.items():
                if signal.block_node_id is not None and \
                        signal.block_port_id is not None and \
                        signal.block_direction is not None:
                    block_key = str(signal.block_node_id) + \
                        ":" + str(signal.block_port_id)
                    block_signal = self.block_signals.get(block_key, None)
                    if block_signal is None:
                        block_signal = {Global.NODE_ID: signal.block_node_id,
                                        Global.PORT_ID: signal.block_port_id}
                    block_signal.update({signal.block_direction: signal_key})
                    self.block_signals.update({block_key: block_signal})

    def build_sensor_signals(self):
        """ build map of sensors and the signals they impact """
        self.sensor_signals = {}
        if self.signals is not None:
            for signal_key, signal in self.signals.items():
                self.sensor_signals = self.__build_sensors_from_rules(
                    signal_key, self.sensor_signals, signal.clear_rules)
                self.sensor_signals = self.__build_sensors_from_rules(
                    signal_key, self.sensor_signals, signal.stop_rules)

    #
    # private functions
    #

    def __build_sensors_from_rules(self, signal_key, sensor_signals, rules):
        """ build sensor data from a set or rules """
        if rules is not None:
            for rule in rules:
                for clause in rule.clauses:
                    sensor_key = str(clause.port_id) + ":" + str(clause.node_id)
                    sensor_signal_list = self.sensor_signals.get(sensor_key, None)
                    if sensor_signal_list is None:
                        sensor_signal_list = []
                    if sensor_key not in sensor_signal_list:
                        sensor_signal_list.append(signal_key)
                    self.sensor_signals.update({signal_key: sensor_signal_list})
        return sensor_signals
