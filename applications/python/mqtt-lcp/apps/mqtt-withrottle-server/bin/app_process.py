#!/usr/bin/python3
# app_process.py
"""


app_process - the application process for mqtt-withrottle-server


The MIT License (MIT)

Copyright 2023 richard p hughes

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
OUT OFSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys

sys.path.append('../lib')

import time
import copy

from multiprocessing import Queue, Event

from processes.base_mqtt_process import BaseMqttProcess
from processes.socket_client_process import SocketClientProcess

from utils.global_synonyms import Synonyms
from utils.global_constants import Global
from utils.utility import Utility

from structs.io_data import IoData
from structs.inventory import Inventory
from structs.inventory import InventoryData

from structs.gui_message import GuiMessage

from withrottle_driver import WithrottleDriver


class ClientSocketPair():
    """ data holder for socket client processes """
    def __init__(self,
                 identity,
                 connection=None,
                 address=None,
                 socket_mode=Global.TEXT,
                 app_queue=None,
                 log_queue=None,
                 roster=None,
                 switches=None):
        self.identity = identity
        # set up events for this pair of processes
        self.shutdown_event = Event()
        self.events = {Global.SHUTDOWN: self.shutdown_event}
        self.device_queue = Queue()
        self.driver_queue = Queue()
        self.socket_mode = socket_mode
        socket_client_queues = {}
        socket_client_queues[Global.DEVICE] = self.device_queue
        socket_client_queues[Global.DRIVER] = self.driver_queue
        socket_client_queues[Global.APPLICATION] = self.driver_queue
        socket_client_queues[Global.LOGGER] = log_queue
        self.socket_process_pid = SocketClientProcess(
            identity=self.identity,
            mode=Global.DEVICE,
            connection=connection,
            address=address,
            events=self.events,
            queues=socket_client_queues,
            host=None,
            port=None,
            socket_mode=self.socket_mode)
        self.socket_process_pid.start()
        server_roster = copy.deepcopy(roster)
        server_switches = copy.deepcopy(switches)
        self.client_process_pid = WithrottleDriver(
            identity=self.identity,
            mode=Global.DRIVER,
            events=self.events,
            in_queue=self.driver_queue,
            app_queue=app_queue,
            device_queue=self.device_queue,
            roster=server_roster,
            switches=server_switches,
            log_queue=log_queue)
        self.client_process_pid.start()


    def is_alive(self):
        """ are the processes alive? """
        rett = False
        if self.socket_process_pid.is_alive() and \
                self.client_process_pid.is_alive():
            rett = True
        return rett

    def shutdown(self):
        """ shutdown the processes """
        self.events[Global.SHUTDOWN].set()
        time.sleep(0.1)
        self.__kill_process(self.socket_process_pid)
        self.socket_process_pid = None
        self.__kill_process(self.client_process_pid)
        self.client_process_pid = None
        # super().shutdown()

    #
    # private functions
    #

    def __kill_process(self, process_pid):
        if process_pid is not None:
            if process_pid.is_alive():
                process_pid.terminate()
                process_pid.join()


MAX_CHECK_CHILD_DELAY = 5


class AppProcess(BaseMqttProcess):
    """ Class that waits for an event to occur """
    def __init__(self, events=None, queues=None):
        super().__init__(name="app",
                         events=events,
                         in_queue=queues[Global.APPLICATION],
                         mqtt_queue=queues[Global.MQTT],
                         log_queue=queues[Global.LOGGER])
        self.log_info("Starting")
        self.cab_topic = None
        self.respond_to_topic = None
        self.socket_child_pairs = {}
        self.check_children_delay = MAX_CHECK_CHILD_DELAY
        self.inventory = Inventory()
        self.power_topic = None
        self.traffic_control = False
        self.auto_signals = False

    def initialize_process(self):
        """ iitialize this process """
        super().initialize_process()
        self.log_info("Init socket server")
        (self.cab_topic, self.respond_to_topic, self.power_topic) \
             = self.__parse_mqtt_options_config(self.mqtt_config)
        self.publish_roster_report_request(Global.ROSTER)
        self.__publish_tower_report_requests()


    def process_message(self, new_message=None):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            (msg_type, msg_body) = new_message
            if msg_type == Global.PUBLISH:
                #print(">>> msg: " + str(new_message))
                body = msg_body[Global.BODY]
                body.mqtt_respond_to = self.respond_to_topic
                if msg_body[Global.SUB] == Global.COMMAND:
                    # publish request to command station
                    #print(">>> publish command request: "+str(self.cab_topic)+" ... "+str(body))
                    self.publish_request_message(\
                        topic=self.cab_topic,
                        message_io_data=body)
                    msg_consummed = True
                elif msg_body[Global.SUB] == Global.SWITCH:
                    # publish request to switch devices
                    #print(">>> switch: "+str(body.mqtt_port_id) + " ... "+str(body.mqtt_desired))
                    if not self.traffic_control:
                        #print(">>> publish switch request: " + str(body))
                        topic = None
                        if body.mqtt_port_id == Global.POWER:
                            topic = self.power_topic
                        else:
                            topic = msg_body[Global.TOPIC]
                        self.publish_request_message(\
                            topic=topic,
                            message_io_data=body)
                    msg_consummed = True
                elif msg_body[Global.SUB] == Global.ROUTE:
                    topic = msg_body[Global.TOPIC]
                    body.mqtt_respond_to = None
                    self.publish_request_message(\
                            topic=topic,
                            message_io_data=body)
            elif msg_type == Global.DEVICE_CONNECT:
                # new client socket connection, start a pairs of processes for in/out
                self.log_info("New Client Connection from: " +
                              str(msg_body[Global.ADDRESS]))
                self.__accept_new_client(msg_body[Global.SOCKET])
            elif msg_type == Global.DEVICE_CLOSE:
                self.log_info("Client Connection closed: " + str(msg_body))
                self.__close_socket_pair(msg_body)
            else:
                self.log_warning("Warning: Unknown Message Type: " +
                                 str(msg_type))

            msg_consummed = True
        return msg_consummed

    def process_other(self):
        """ perform other none message relared tasks """
        super().process_other()
        self.check_children_delay -= 1
        if self.check_children_delay < 1:
            self.check_children_delay = MAX_CHECK_CHILD_DELAY
            self.__check_children_processes()

    def shutdown_process(self):
        """ close client sockets """
        for _socket_child_pair_key, socket_child_pair in\
                self.socket_child_pairs.items():
            # print(">>> Shutdown socket pair: " + str(socket_child_pair_key))
            socket_child_pair.events[Global.SHUTDOWN].set()
        time.sleep(0.5)
        super().shutdown_process()

    def process_response_cab_message(self, msg_body=None):
        """ process response to cab request """
        msg_consummed = False
        if msg_body.mqtt_message_root == Global.CAB:
            throttle_id = msg_body.mqtt_throttle_id
            if throttle_id is None:
                self.log_error("Error: THROTTLE-ID required in CAB responses: \n"\
                    + " ... " + str(msg_body))
            else:
                desired = None
                if isinstance(msg_body.mqtt_desired, dict):
                    if Global.FUNCTION in msg_body.mqtt_desired:
                        desired = Global.FUNCTION
                    elif Global.SPEED in msg_body.mqtt_desired:
                        desired = Global.SPEED
                    elif Global.DIRECTION in msg_body.mqtt_desired:
                        desired = Global.DIRECTION
                    elif Global.REPORT in msg_body.mqtt_desired:
                        desired = Global.REPORT
                else:
                    desired = msg_body.mqtt_desired
                if desired in \
                        [Global.CONNECT, Global.DISCONNECT]:
                    msg_consummed = True
                elif desired in [Global.ACQUIRE, Global.STEAL]:
                    self.__forward_message_to_throttle(
                        throttle_id, (Global.ACQUIRE, msg_body))
                    msg_consummed = True
                elif desired in [Global.RELEASE]:
                    self.__forward_message_to_throttle(
                        throttle_id, (Global.RELEASE, msg_body))
                    msg_consummed = True

                elif desired in \
                        [Global.SPEED, Global.DIRECTION]:
                    self.__forward_message_to_throttle(
                        throttle_id, (Global.SPEED, msg_body))
                    msg_consummed = True
                elif desired in \
                        [Global.FUNCTION]:
                    self.__forward_message_to_throttle(
                        throttle_id, (Global.FUNCTION, msg_body))
                    msg_consummed = True
        if not msg_consummed:
            self.log_warning("Unexpected Response: " + str(msg_body.mqtt_throttle_id) + " ... " + \
                    str(msg_body.mqtt_cab_id) + " ... " +\
                    str(msg_body.mqtt_desired))

    def process_data_switch_message(self, msg_body=None):
        """ process data switch message """
        # print(">>> data switch: " + str(msg_body))
        if msg_body.mqtt_port_id == Global.TRAFFIC:
            self.traffic_control = Synonyms.is_on(msg_body.mqtt_reported)
            self.log_info("Traffic Control: " + str(self.traffic_control))
            # print(">>> traffic: " + str(self.traffic_control))
            self.publish_tower_report_request(Global.INVENTORY)
        elif msg_body.mqtt_port_id == Global.AUTO_SIGNALS:
            self.auto_signals = Synonyms.is_on(msg_body.mqtt_reported)
        else:
            self.__update_sensor_state(Global.SWITCH, msg_body)
        # forward message to throttles for processing
        # print(">>> data switch: " + str(msg_body))
        self.__forward_message_to_all_throttles((Global.SWITCH, msg_body))

    def process_data_route_message(self, msg_body=None):
        """ process data route message """
        # make a route data message look like a switch data message
        # print(">>> data route: " + str(msg_body))
        self.__update_sensor_state(Global.ROUTE, msg_body)
        # forward message to throttles for processing
        msg_body.mqtt_node_id = Global.ROUTE # replace actual node id with common "route"
        if Synonyms.is_on(msg_body.mqtt_reported):
            msg_body.mqtt_reported = Global.THROWN
        elif Synonyms.is_off(msg_body.mqtt_reported):
            msg_body.mqtt_reported = Global.CLOSED
        else:
            msg_body.mqtt_reported = Global.UNKNOWN
        # print(">>> data route: " + str(msg_body))
        self.__forward_message_to_all_throttles((Global.SWITCH, msg_body))

    def process_response_switch_message(self, msg_body=None):
        """ process response switch message """
        # ignore response, act on data sensor
        pass

    def process_data_cab_signal_message(self, msg_body=None):
        """ process a cab signal message"""
        self.log_info(Global.RECEIVED+": "+str(msg_body.mqtt_port_id) +\
                      " ... " + str(msg_body.mqtt_loco_id) + " : " +\
                        str(msg_body.mqtt_reported))
        self.__forward_message_to_all_throttles((Global.CAB_SIGNAL, msg_body))
        return True

    def process_data_sensor_message(self, msg_body=None):
        """ process data sensor message """
        self.__update_sensor_state(Global.SENSOR, msg_body)

    def process_data_roster_message(self, msg_body=None):
        """ process data roster message """
        self.log_info("roster data received: "+ \
                    str(msg_body.mqtt_port_id)+" ... "+str(msg_body.mqtt_reported))
        if msg_body.mqtt_reported == Global.CHANGED:
            # roster has changed, request the roster
            self.publish_roster_report_request(Global.ROSTER)
        else:
            self.log_unexpected_message(msg_body=msg_body)

    def process_data_signal_message(self, msg_body=None):
        """ process data signal message """
        self.__update_sensor_state(Global.SIGNAL, msg_body)

    def process_data_block_message(self, msg_body=None):
        """ process data block message """
        self.__update_sensor_state(Global.BLOCK, msg_body)

    def process_data_locator_message(self, msg_body=None):
        """ process data locator message """
        # forward message to inventory process for processing
        self.__update_sensor_state(Global.LOCATOR, msg_body)

    def process_data_fastclock_message(self, msg_body=None):
        """ process a fastclock message"""
        self.log_info(Global.RECEIVED+": "+Global.FASTCLOCK)
        self.__forward_message_to_all_throttles((Global.FASTCLOCK, msg_body))
        return True

    def process_response_inventory_message(self, msg_body=None):
        """ process inventory response message """
        self.log_info(Global.RECEIVED+": "+Global.INVENTORY)
        inventory_map = None
        meta = msg_body.mqtt_metadata
        if meta is not None:
            inventory_map = meta.get(Global.INVENTORY, None)
        if inventory_map is None:
            # not a roster response, pass it to super instance
            self.log_error("No Inventory found in tower response: " +
                           str(meta))
        else:
            # found an inventory
            self.inventory = Inventory({Global.INVENTORY: inventory_map})
            switches = self.__build_switch_route_list()
            self.__forward_message_to_all_throttles((Global.SWITCHES, switches))
        return True

    def process_data_cab_message(self, msg_body=None):
        """ process data cab message """
        if msg_body.mqtt_reported == Global.STOLEN:
            self.__forward_message_to_throttle(
                        msg_body.mqtt_throttle_id, (Global.STOLEN, msg_body))
            message = "Loco: " + str(msg_body.mqtt_cab_id) + ": " \
                    + str(msg_body.mqtt_loco_id) + ": " +str(msg_body.mqtt_reported)
            self.log_info("rcv: " + message)
        else:
            self.log_unexpected_message(msg_body=msg_body)
        return True

    def process_data_tower_message(self, msg_body=None):
        """ process data roster message """
        self.log_info("tower data received: "+ \
                      str(msg_body.mqtt_port_id)+" ... "+str(msg_body.mqtt_reported))
        if msg_body.mqtt_port_id == Global.INVENTORY and \
                msg_body.mqtt_reported == Global.CHANGED:
            # inventory has changed, request the inventory
            self.__publish_tower_report_requests()
        else:
            self.log_unexpected_message(msg_body=msg_body)
        return True


    #
    # private functions
    #

    def __publish_tower_report_requests(self):
        """ request inventory reports from tower """
        self.publish_tower_report_request(Global.INVENTORY)

    def __accept_new_client(self, connection_socket):
        now = Utility.now_milliseconds()
        # identity = str(now)
        hex_id = hex(now)
        identity = hex_id[-8:].upper()
        #print(">>> id:" + str(identity) + " ... " + str(hex_id) + " ... " +
        #      str(hex_id8))
        switches = self.__build_switch_route_list()
        new_client_socket_pair = ClientSocketPair(identity,
                                                  connection=connection_socket,
                                                  app_queue=self.in_queue,
                                                  log_queue=self.log_queue,
                                                  roster=self.roster,
                                                  switches=switches)
        self.socket_child_pairs[identity] = new_client_socket_pair
        self.__publish_connect(identity)

    def __check_children_processes(self):
        child_pair_keys = list(self.socket_child_pairs.keys())
        for child_pair_key in child_pair_keys:
            if not self.socket_child_pairs[child_pair_key].is_alive():
               # print(">>> # oops, one of the processes has crashed, clean up")
                self.log_warning(
                    "A child socket process has crashed, cleaning up")
                self.__close_socket_pair(child_pair_key)

    def __close_socket_pair(self, child_pair_key):
        self.socket_child_pairs[child_pair_key].shutdown()
        del self.socket_child_pairs[child_pair_key]
        self.__publish_disconnect(child_pair_key)

    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse time options section of config file """
        #print(">>> pub topics: "+str( mqtt_config.publish_topics))
        cab_topic = mqtt_config.publish_topics.get(Global.CAB,
                                                       Global.UNKNOWN) + "/req"
        power_topic = mqtt_config.publish_topics.get(Global.POWER,
                                                       Global.UNKNOWN) + "/req"
        respond_to_topic = mqtt_config.subscribe_topics.get(
            Global.SELF, Global.UNKNOWN)
        respond_to_topic = respond_to_topic.replace("/#", "/res")
        return (cab_topic, respond_to_topic, power_topic)

    def __publish_connect(self, ident):
        """ publish a throttle connect command """
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = ident
        body.mqtt_desired = Global.CONNECT
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.cab_topic,
                    message_io_data=body)

    def __publish_disconnect(self, ident):
        """ publish a throttle connect command """
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = ident
        body.mqtt_desired = Global.DISCONNECT
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.cab_topic,
                    message_io_data=body)

    def __build_switch_route_list(self):
        """ build a list of switches and routes"""
        switches = []
        switches = self.__build_switch_list(switches)
        switches = self.__build_route_list(switches)
        return switches

    def __build_route_list(self, switches):
        """ build a list of routes """
        route_group = self.inventory.inventory_groups.get(Global.ROUTE, None)
        if route_group is not None:
            # print(">>> group map: " + str(switch_group))
            for _k, route in route_group.inventory_items.items():
                #print(">>> item: " + str(switch.node_id) + \
                    #   " ... " + str(switch.port_id))
                route_map = GuiMessage()
                route_map.node_id = Global.ROUTE  # replace actual node id with a common "route"
                route_map.port_id = route.port_id
                route_map.name = route_map.node_id +":"+route_map.port_id
                route_map.command_topic = route.command_topic
                reported = Global.UNKNOWN
                if Synonyms.is_on(route.reported):
                    reported = Global.THROWN
                elif Synonyms.is_off(route.reported):
                    reported = Global.CLOSED
                route_map.mode =  reported
                switches.append(route_map)
        return switches

    def __build_switch_list(self, switches):
        """ build a list of switches """
        switch_group = self.inventory.inventory_groups.get(Global.SWITCH, None)
        if switch_group is not None:
            # print(">>> group map: " + str(switch_group))
            for _k, switch in switch_group.inventory_items.items():
                #print(">>> item: " + str(switch.node_id) + \
                    #   " ... " + str(switch.port_id))
                switch_map = GuiMessage()
                switch_map.name = switch.key
                switch_map.node_id = switch.node_id
                switch_map.port_id = switch.port_id
                switch_map.command_topic = switch.command_topic
                switch_map.mode = switch.reported
                switches.append(switch_map)
        return switches


    def __update_sensor_state(self, group_id, msg_body):
        """ update the state of a sensor, switch, etc """
        item = InventoryData()
        item.parse_mqtt_message(msg_body)
        self.inventory.update_sensor_state(group_id, item)

    def __forward_message_to_all_throttles(self, message):
        """ forward a message to all throttles """
        child_pair_keys = list(self.socket_child_pairs.keys())
        for child_pair_key in child_pair_keys:
            self.__forward_message_to_throttle(child_pair_key, message)

    def __forward_message_to_throttle(self, identity, message):
        """ forward message to the throttle process """
        if identity in self.socket_child_pairs:
            child = self.socket_child_pairs[identity]
            queue = child.driver_queue
            queue.put(message)
        else:
            self.log_debug("Message for client not deliverable: " + \
                str(identity) + " ... " + str(message))
