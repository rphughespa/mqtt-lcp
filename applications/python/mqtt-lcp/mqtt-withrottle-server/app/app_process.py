#!/usr/bin/python3
# app_process.py
"""


app_process - the application process for mqtt-withrottle-server


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
OUT OFSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys

sys.path.append('../lib')

import time
import copy

from multiprocessing import Queue, Event

from processes.base_mqtt_process import BaseMqttProcess
from processes.socket_client_process import SocketClientProcess

from utils.global_constants import Global
from utils.utility import Utility

from structs.io_data import IoData
from structs.inventory import Inventory
from structs.sensor_states import SensorStates
from structs.sensor_states import SensorStateData
from structs.throttle_message import ThrottleMessage

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
        self.dispatcher_command_pub_topic = None
        self.respond_to_topic = None
        self.socket_child_pairs = {}
        self.check_children_delay = MAX_CHECK_CHILD_DELAY
        self.switches = []
        self.sensor_states = SensorStates()

    def initialize_process(self):
        """ iitialize this process """
        super().initialize_process()
        self.log_info("Init socket server")
        (self.dispatcher_command_pub_topic, self.respond_to_topic) \
             = self.__parse_mqtt_options_config(self.mqtt_config)
        self.publish_dispatcher_report_request(Global.ROSTER)
        self.publish_tower_report_request(Global.INVENTORY)
        self.publish_tower_report_request(Global.STATES)

    def process_message(self, new_message=None):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            (msg_type, msg_body) = new_message
            if msg_type == Global.PUBLISH:
                # print(">>> msg: " + str(new_message))
                body = msg_body[Global.BODY]
                body.mqtt_respond_to = self.respond_to_topic
                if msg_body[Global.SUB] == Global.COMMAND:
                    # publish request to command station
                    # print(">>> publish command request")
                    self.publish_request_message(\
                        topic=self.dispatcher_command_pub_topic,
                        message_io_data=body)
                    msg_consummed = True
                elif msg_body[Global.SUB] == Global.SWITCH:
                    # publish request to command station
                    # print(">>> publish command request")
                    topic = msg_body.get(Global.TOPIC,
                                         self.dispatcher_command_pub_topic)
                    self.publish_request_message(\
                        topic=topic,
                        message_io_data=body)
                    msg_consummed = True
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
        for socket_child_pair_key, socket_child_pair in\
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

    def process_response_inventory_message(self, msg_body=None):
        """ process response inventory message """
        inventory_map = None
        meta = msg_body.mqtt_metadata
        if meta is not None:
            inventory_map = meta.get(Global.INVENTORY, None)
        if inventory_map is None:
            # not a inventory response, pass it to super instance
            self.log_error(
                "base_cab: No inventory found in tower response: " +
                str(meta))
        else:
            # found an inventory
            # print(">>> inv map: " + str(inventory_map))
            inventory = Inventory({Global.INVENTORY: inventory_map})
            switch_group = inventory.inventory_groups.get(Global.SWITCH, None)
            self.switches = []
            if switch_group is not None:
                # print(">>> group map: " + str(switch_group))
                for switch in switch_group.inventory_items:
                    #print(">>> item: " + str(switch.node_id) + \
                    #    " ... " + str(switch.port_id))
                    switch_map = ThrottleMessage()
                    switch_map.name = switch.node_id + ":" + switch.port_id
                    switch_map.node_id = switch.node_id
                    switch_map.port_id = switch.port_id
                    switch_map.text = switch.command_topic
                    switch_map.mode = Global.UNKNOWN
                    self.switches.append(switch_map)


    def process_response_switch_message(self, msg_body=None):
        """ process response switch message """
        # ignore response, act on data sensor
        pass

    def process_data_sensor_message(self, msg_body=None):
        """ process data sensor message """
        self.__update_sensor_state(msg_body)

    def process_data_switch_message(self, msg_body=None):
        """ process data switch message """
        # print(">>> data switch: " + str(msg_body))
        self.__update_sensor_state(msg_body)
        # forward message to throttles for processing
        self.__forward_message_to_all_throttles((Global.SWITCH, msg_body))

    def process_data_signal_message(self, msg_body=None):
        """ process data signal message """
        self.__update_sensor_state(msg_body)

    def process_data_block_message(self, msg_body=None):
        """ process data block message """
        self.__update_sensor_state(msg_body)

    def process_data_locator_message(self, msg_body=None):
        """ process data locator message """
        # forward message to inventory process for processing
        self.__update_sensor_state(msg_body)

    def process_data_fastclock_message(self, msg_body=None):
        """ process a fastclock message"""
        self.log_info(Global.RECEIVED+": "+Global.FASTCLOCK)
        self.__forward_message_to_all_throttles((Global.FASTCLOCK, msg_body))
        return True

    def process_response_states_message(self, msg_body=None):
        """ process response inventory message """
        # print(">>> states: " + str(msg_body))
        states_map = None
        meta = msg_body.mqtt_metadata
        if meta is not None:
            states_map = meta.get(Global.SENSOR_STATES, None)
        if states_map is None:
            # not a sensor states response, pass it to super instance
            self.log_error("No Sensor States found in tower response: " +
                           str(meta))
        else:
            # found sensor state
            new_sensor_states = SensorStates(
                {Global.SENSOR_STATES: states_map})
            for group, items in self.sensor_states.sensor_state_groups.items():
                for _skey, state in items.sensor_state_items.items():
                    self.sensor_states.update_sensor_state(group, state)
        self.sensor_states = new_sensor_states

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

    #
    # private functions
    #

    def __accept_new_client(self, connection_socket):
        now = Utility.now_milliseconds()
        # identity = str(now)
        hex_id = hex(now)
        identity = hex_id[-8:].upper()
        #print(">>> id:" + str(identity) + " ... " + str(hex_id) + " ... " +
        #      str(hex_id8))
        self.__update_switch_states()
        new_client_socket_pair = ClientSocketPair(identity,
                                                  connection=connection_socket,
                                                  app_queue=self.in_queue,
                                                  log_queue=self.log_queue,
                                                  roster=self.roster,
                                                  switches=self.switches)
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
        dispatcher_topic = mqtt_config.publish_topics.get(Global.DISPATCHER,
                                                       Global.UNKNOWN) + "/req"
        respond_to_topic = mqtt_config.subscribe_topics.get(
            Global.SELF, Global.UNKNOWN)
        respond_to_topic = respond_to_topic.replace("/#", "/res")
        return (dispatcher_topic, respond_to_topic)

    def __publish_connect(self, ident):
        """ publish a throttle connect command """
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = ident
        body.mqtt_desired = Global.CONNECT
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.dispatcher_command_pub_topic,
                    message_io_data=body)

    def __publish_disconnect(self, ident):
        """ publish a throttle connect command """
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = ident
        body.mqtt_desired = Global.DISCONNECT
        body.mqtt_respond_to = self.respond_to_topic
        self.publish_request_message(\
                    topic=self.dispatcher_command_pub_topic,
                    message_io_data=body)

    def __update_sensor_state(self, msg_body):
        """ up the state of a sensor, switch, etc """
        state_data = SensorStateData()
        state_data.node_id = msg_body.mqtt_node_id
        state_data.port_id = msg_body.mqtt_port_id
        state_data.key = state_data.node_id + ":" + state_data.port_id
        state_data.reported = msg_body.mqtt_reported
        state_data.loco_id = [msg_body.mqtt_loco_id
                              ]  # state loco_id are a list
        state_data.metdata = msg_body.mqtt_metadata
        state_data.timestamp = msg_body.mqtt_timestamp
        if msg_body.mqtt_loco_id is not None:
            state_data.loco = [msg_body.mqtt_loco_id]
        #print(">>> update sensor: " + str(state_data))
        group = msg_body.mqtt_message_root
        self.sensor_states.update_sensor_state(group, state_data)

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

    def __update_switch_states(self):
        switch_group_states = \
                self.sensor_states.sensor_state_groups.get(Global.SWITCH, None)
        if switch_group_states is not None:
            for switch in self.switches:
                key = switch.node_id + ":" + switch.port_id
                state_item = switch_group_states.sensor_state_items.get(
                    key, None)
                if state_item is not None:
                    switch.mode = state_item.reported
