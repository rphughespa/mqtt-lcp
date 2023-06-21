#!/usr/bin/python3
# signals_manager.py
"""

    SignalsManager.py - Class for automating signals

    None: assumes all signal ids and block ids are unique across the system

the MIT License (MIT)

Copyright © 2023 richard p hughes

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
import sys
import os

sys.path.append('../lib')

from utils.json_utils import JsonUtils
from utils.global_constants import Global
from utils.log_utils import LogUtils
from structs.signal_rules import Signal
from structs.signal_rules import SignalRule
# from structs.inventorys import SensorStates


class SignalsManager(object):
    """ Class representing a manager of signals"""
    def __init__(self, parent):
        self.parent = parent
        self.json_helper = JsonUtils()
        self.signal_rules = {}
        self.rules_by_port_id = {}
        self.__load_signal_rules()
        self.__xref_signal_rules()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def update_signals(self, _message_root, state_data):
        """ a sensor has changed, update associated signals"""
        self.parent.log_info("sensor_changed: " + \
                str(state_data.key)+" : "+str(state_data.reported))
        if self.rules_by_port_id is not None:
            ports_xref = self.rules_by_port_id.get(state_data.port_id, None)
            if ports_xref is not None:
                for key in ports_xref:
                    self.__update_a_signal(key)
            #else:
            #    print(">>> no rules for: "+str(state_data.key)+" : "+str(state_data.reported))

    def inventory_has_changed(self):
        """ inventory has been updated, rebuild some tables """
        pass  # nothing to do

    def update_signal_aspects(self):
        """ update signals aspect based on current device states """
        for key in self.signal_rules:
            self.__update_a_signal(key)

    #
    # private functions
    #

    def __update_a_signal(self, key):
        """ update a signal's aspect based on current device states """
        # evaluate clear rules, the approach
        signal_rule = self.signal_rules.get(key, None)
        #print(">>> rule: "+str(key)+" : "+str(signal_rule.node_id)+" : "+str(signal_rule.port_id))
        if signal_rule is not None:
            #print(">>> . clear rules:")
            new_aspect =  self.__evaluate_rules(signal_rule.clear_rules, Global.CLEAR)
            if new_aspect is None:
                # no clear rule match, examime approach rules
                #print(">>> . approach rules:")
                new_aspect =  self.__evaluate_rules(signal_rule.approach_rules, Global.APPROACH)
            if new_aspect is None:
                # no rule match, set signal to stop
                new_aspect = Global.STOP
            if new_aspect is not None:
                #print(">>> ... signal changed: "+str(key) +" : "+str(new_aspect))
                # only send change request if signal is not already in this aspect
                current_state_item = self.__find_inventory_item(signal_rule.group, \
                                                    signal_rule.node_id, signal_rule.port_id)
                #if current_state_item is None:
                #    print(">>> ERROR: can't find signal: "+str(signal_rule.port_id))
                if current_state_item is None or \
                            current_state_item.reported != new_aspect:
                    self.parent.log_info("Request Signal Change: "+\
                                         str(signal_rule.port_id)+ " : " + str(new_aspect))
                    inv_item = self.parent.find_signal(signal_rule.node_id, signal_rule.port_id)
                    if inv_item is None:
                        self.parent.log_error("Cannot find Inv Item: "+ \
                                              str(signal_rule.node_id) + " : "+ \
                                              str(signal_rule.port_id))
                    else:
                        self.parent.log_info("Publish Signal Change Request: " + \
                                             str(inv_item.key) +" : "+str(new_aspect))
                        self.parent.process_request_device_message(Global.SIGNAL, \
                                                                   signal_rule.node_id, \
                                                                signal_rule.port_id, \
                                                                new_aspect,
                                                                inv_item.command_topic)

    def __evaluate_rules(self, signal_rules, signal_aspect):
        """ examine rule if a match if found, return the new aspect """
        rett = None
        #print(">>> .. rules: "+str(len(signal_rules)))
        for _key, rule in sorted(signal_rules.items()):
            clauses_true = True
            for clause in rule.clauses:
                reported = None
                current_state_item = self.__find_inventory_item(clause.group, \
                                                    clause.node_id, clause.port_id)
                #print(">>> ... clause: "+str(clause.group)+" : "+str(clause.node_id)+" : "+ \
                #             str(clause.port_id)+" : "+str(clause.state)+ " : " +\
                #             str(current_state_item is not None))
                if current_state_item is not None:
                    reported = current_state_item.reported
                if reported != clause.state:
                    clauses_true = False
                    #print(">>> ... no match:"+str(clause.state)+" : "+str(reported))
                    break
                #else:
                #    print(">>> ... match:"+str(clause.state)+" : "+str(reported))
            if clauses_true:
                # we found a match
                #print(">>> ... ... rule is True")
                rett = signal_aspect
                break
            #else:
            #    print(">>> ... ... rule is False")
        return rett

    def __load_signal_rules(self):
        """ load signal rules json data from file system """
        #print(">>> loading signals")
        self.signal_rules = {}
        self.rules_by_port_id = {}
        signal_rules_path = os.path.join(self.parent.data_path, "signal-rules")
        if not os.path.exists(signal_rules_path):
            self.parent.logger.log_error(
                "!!! Error: signal rules data path does not exists: " +
                str(signal_rules_path))
        else:
            if os.path.isdir(signal_rules_path):
                for file_name  in os.listdir(signal_rules_path):
                    full_file_name = os.path.join(signal_rules_path, file_name)
                    if ".json" in full_file_name:
                        self.parent.log_info("Loading Signal Rule: "+str(file_name))
                        signal_map = self.json_helper.parse_one_json_file(full_file_name)
                        # print(">>> signal map: "+str(signal_map))
                        new_signal = Signal(signal_map)
                        # print(">>> signal: "+str(new_signal))
                        self.signal_rules.update({new_signal.key: new_signal})

    def __xref_signal_rules(self):
        """ build signal rule cross ref tab by port id """
        self.rules_by_port_id = {}
        for key, signal_rule in self.signal_rules.items():
            for _rule_key, rule in signal_rule.clear_rules.items():
                self.__xref_one_rule(key, rule)
            for _rule_key, rule in signal_rule.approach_rules.items():
                self.__xref_one_rule(key, rule)

    def __xref_one_rule(self, key, rule):
        """ cross reference clauses in a rule """
        #print(">>> xref rule: "+str(rule))
        for clause in rule.clauses:
            existing_port_xref = self.rules_by_port_id.get(clause.port_id, None)
            if existing_port_xref is None:
                existing_port_xref = []
                self.rules_by_port_id.update({clause.port_id: existing_port_xref})
            if key not in existing_port_xref:
                existing_port_xref.append(key)

    def __find_inventory_item(self, group, node, port):
        """ find a sensor state inv item by full key, or just group and port """
        inventory_item = None
        if group is not None:
            inventory_group = self.parent.inventory.inventory_groups.get(group, None)
            if inventory_group is not None:
                key = str(node) + ":" + str(port)
                inventory_item = inventory_group.inventory_items.get(key, None)
                if inventory_item is None:
                    key = inventory_group.inventory_by_port_id.get(port, None)
                    if key is not None:
                        inventory_item = inventory_group.inventory_items.get(key, None)
        return inventory_item
