#!/usr/bin/python3
# routes_manager.py
"""

    RoutesManager.py - Class for controlling routes

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
import copy

sys.path.append('../lib')

from utils.json_utils import JsonUtils
from utils.global_constants import Global
from utils.global_synonyms import Synonyms
from utils.log_utils import LogUtils

from structs.routes import Route
from structs.inventory import InventoryData
from structs.io_data import IoData

class RoutesManager(object):
    """ Class representing a manager of routes"""
    def __init__(self, parent):
        self.parent = parent
        self.json_helper = JsonUtils()
        self.routes = {}
        self.routes_xref = {}

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def initialize_routes(self):
        """ load and initialize route informarion """
        self.__load_routes()
        self.__xref_routes()
        self.__add_routes_to_inventory()

    def update_routes(self, message_root, state_data):
        """ process output message """
        if message_root == Global.SWITCH:
            self.__process_switch_change(state_data)

    def set_route_switches(self, msg_body):
        """ process a request to set a route's switches message"""
        error_msg = None
        route_key = msg_body.mqtt_node_id + ":" + msg_body.mqtt_port_id
        route = self.routes.get(route_key, None)
        if route is None:
            error_msg = "Error: route not found"
        else:
            if not Synonyms.is_on(msg_body.mqtt_desired) and \
                    not Synonyms.is_off(msg_body.mqtt_desired):
                error_msg = "Error: invalid value for desired"
            else:
                reverse = False
                if Synonyms.is_off(msg_body.mqtt_desired):
                    reverse = True
                for _swkey, switch in route.switches.items():
                    desired = switch.desired
                    if reverse:
                        desired = Synonyms.reverse(desired)
                    self.parent.log_info("Publish Switch Change Request: " +str(switch.key) +" : "+str(desired))
                    self.parent.process_request_device_message(Global.SWITCH, \
                            switch.node_id, switch.port_id, \
                            desired, switch.command_topic)
        meta = None
        reported = Synonyms.desired_to_reported(msg_body.mqtt_desired)
        data_reported = Global.UNKNOWN
        if error_msg is not None:
            reported = Global.ERROR
            meta = {Global.MESSAGE: str(error_msg)}
            data_reported = None
        self.parent.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.RESPONSE,
                                             Global.REPORTED: reported, Global.DATA: data_reported,
                                             Global.METADATA: meta, Global.BODY: msg_body}))


#
# private functions
#

    def __load_routes(self):
        """ load route info from json files """
        self.routes = {}
        routes_path = os.path.join(self.parent.data_path, Global.ROUTE)
        if not os.path.exists(routes_path):
            self.parent.log_error("!!! Error: routes data path does not exists: " +
                           str(routes_path))
        else:
            if os.path.isdir(routes_path):
                for file_name in os.listdir(routes_path) :
                    full_file_name = os.path.join(routes_path, file_name)
                    if ".json" in full_file_name:
                        self.parent.log_info("Loading Route: " +str(file_name))
                        route_map = self.json_helper.parse_one_json_file(
                            full_file_name)
                        if route_map is not None:
                            for route in route_map:
                                node_id = route.get(Global.NODE_ID, None)
                                port_id = route.get(Global.PORT_ID, None)
                                switches = route.get(Global.SWITCH, None)
                                if node_id is None:
                                    self.parent.log_error("Error: Route: "+ \
                                                          str(file_name)+" : is missing 'node-id' parameter")
                                elif port_id is None:
                                    self.parent.log_error("Error: Route: "+ \
                                                          str(file_name)+" : is missing 'port-id' parameter")
                                elif switches is None:
                                    self.parent.log_error("Error: Route: "+ \
                                                          str(file_name)+" : is missing 'switch' parameter")
                                else:
                                    route_item = Route(route)
                                    self.routes.update({route_item.key: route_item})
    def __xref_routes(self):
        """ crossref routes by switch node/port """
        self.routes_xref = {}
        for route_key, route in self.routes.items():
            for _sw_key, switch in route.switches.items():
                switch_xref = self.routes_xref.get(switch.key, None)
                if switch_xref is None:
                    switch_xref = []
                if not route_key in switch_xref:
                    switch_xref.append(route_key)
                self.routes_xref.update({switch.key: switch_xref})

    def __add_routes_to_inventory(self):
        """ add route data to inventory """
        for _route_key, route in self.routes.items():
            new_item = InventoryData()
            new_item.node_id = route.node_id
            new_item.port_id = route.port_id
            new_item.key = str(new_item.node_id) + ":" + str(new_item.port_id)
            new_item.description = route.description
            new_item.reported = Global.UNKNOWN
            new_item.command_topic = self.parent.route_topic + "/" + str(route.port_id) + "/req"
            new_item.data_topic = self.parent.route_data_topic + "/" + str(route.port_id)
            self.parent.inventory.update_sensor_state(Global.ROUTE, new_item)

    def __process_switch_change(self, switch_change):
        """ update any route impacted by a switch chnage """
        route_group = self.parent.inventory.inventory_groups.get(Global.ROUTE, None)
        if route_group is not None:
            route_xref = self.routes_xref.get(switch_change.key, None)
            if route_xref:
                # this switch referenced in some routes, evaluate them
                for route_key in route_xref:
                    #print(">>> route key: "+str(route_key))
                    route = self.routes.get(route_key, None)
                    if route is not None:
                        new_route_state = self.__evaluate_route_state(route_key)
                        if new_route_state is not None:
                            #print(">>> get route inv: "+str(route.key))
                            #print(">>> new route_state: "+str(new_route_state))
                            inv_route = route_group.inventory_items.get(route.key, None)
                            if inv_route is not None and \
                                        inv_route.reported != new_route_state:
                                #print(" ... "+str(inv_route.reported))
                                inv_route.reported = new_route_state
                                self.__report_route_data(route.port_id, new_route_state)

    def __evaluate_route_state(self, route_key):
        """ evaluate the state of a route by comparing its switch states"""
        new_state = Global.UNKNOWN
        is_active = True
        is_inactive = True
        route = self.routes.get(route_key, None)
        if route is not None:
            switch_group = self.parent.inventory.inventory_groups.get(Global.SWITCH, None)
            if switch_group is not None:
                for key, route_switch in route.switches.items():
                    # chnage desired to past tense reported
                    #print(">>> switch: "+str(key))
                    inv_switch = switch_group.inventory_items.get(key, None)
                    if inv_switch is None:
                        is_active = False
                        is_inactive = False
                    else:
                        #print(" ... reported: "+str(inv_switch.reported) + \
                        #        ", desired: " + str(route_switch.desired))
                        reported_on = Synonyms.is_on(inv_switch.reported)
                        desired_on = Synonyms.is_on(route_switch.desired)
                        reversed_desired_on = Synonyms.is_on(Synonyms.reverse(route_switch.desired))
                        if reported_on == desired_on:
                            #print(">>> ... ... match")
                            is_inactive = False
                        elif reported_on == reversed_desired_on:
                            #print(">>> ... ... reverse match")
                            is_active = False
                        else:
                            #print(">>> ... ... no match")
                            is_active = False
                            is_inactive = False
        if is_active:
            new_state = Global.ON
        elif is_inactive:
            new_state = Global.OFF
        #print(">>> new state: "+str(new_state))
        return new_state

    def __report_route_data(self, port_id, reported):
        """ send a route data message data"""
        msg_body = IoData()
        msg_body.mqtt_reported = reported
        msg_body.mqtt_message_root = Global.ROUTE
        msg_body.mqtt_port_id = port_id
        msg_body.mqtt_respond_to = None  # ignore response, monitor data message
        self.parent.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.DATA, \
                                             Global.TOPIC: self.parent.route_data_topic, \
                                                Global.BODY: msg_body}))
