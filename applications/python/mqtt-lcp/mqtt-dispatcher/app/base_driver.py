#!/usr/bin/python3
# base_driver.py
"""

        base_driver - base process class for driver processings



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
# from turtle import end_fill

sys.path.append('../lib')
import copy

# import time

from structs.throttle_message import ThrottleMessage
from structs.mqtt_config import MqttConfig
from structs.io_data import IoData


from utils.global_constants import Global

from processes.base_process import BaseProcess

from command_slot_manager import CommandSlotManager

MAX_BUFFER = 120


class BaseDriver(BaseProcess):
    """ Process  Messages to/from Device """
    def __init__(self, name="driver", events=None, queues=None):
        super().__init__(name=name,
                         events=events,
                         in_queue=queues[Global.DRIVER],
                         app_queue=queues[Global.APPLICATION],
                         log_queue=queues[Global.LOGGER])
        self.queues = queues
        self.cab_queue = queues[Global.CAB]
        self.response_queue_name = Global.DRIVER + ":" + Global.RESPONSE
        self.device_queue = queues[Global.DEVICE]
        self.response_queue = queues[self.response_queue_name]
        self.decoder = None
        self.encoder = None
        self.mqtt_config = None
        self.cab_pub_topic = None
        self.slot_manager = None
        self.max_locos = 32

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        self.max_locos = self.__parse_config(self.config)
        self.slot_manager = \
                CommandSlotManager(slot_count=self.max_locos, log_queue = self.queues[Global.LOGGER])
        self.mqtt_config = MqttConfig(self.config, self.node_name,
                                      self.host_name, self.log_queue)
        # print(">>> mqtt_config: " + str(self.mqtt_config))
        (self.cab_pub_topic) \
             = self.__parse_mqtt_options_config(self.mqtt_config)

    def process_message(self, new_message):
        """ process messages from async message queue """
        # self.log_warning("driver message: " + str(new_message))
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            msg_type = None
            msg_body = None
            msg_device_identity = None
             # message are in either (type,message) or (type, message, identity) format
            if len(new_message) == 3:
                (msg_type, msg_body, msg_device_identity) = new_message
            else:
                (msg_type, msg_body) = new_message
            if (msg_type in [Global.DRIVER_SEND_AND_RESPOND, \
                    Global.DRIVER_SEND]) and \
                    not isinstance(msg_body, ThrottleMessage):
                self.log_error("Dcc++ Driver messages must in ThrottleMessage format: " + \
                    str(msg_body))
                msg_consummed = True
            else:
                if msg_type == Global.DRIVER_SEND_AND_RESPOND:
                    #print(">>> commands: " + str(msg_body.command) + " ... " + str(msg_body.sub_command))
                    if msg_body.command == Global.THROTTLE and \
                            msg_body.sub_command == Global.CONNECT:
                        self.connect_throttle(msg_body)
                        msg_body.reported = Global.CONNECTED
                        self.publish_response(msg_body, msg_body.response_queue)
                        msg_consummed = True
                    elif msg_body.command == Global.THROTTLE and \
                            msg_body.sub_command == Global.DISCONNECT:
                        self.disconnect_throttle(msg_body)
                        msg_body.reported = Global.DISCONNECTED
                        self.publish_response(msg_body, msg_body.response_queue)
                        msg_consummed = True
                    elif msg_body.command == Global.THROTTLE and \
                            msg_body.sub_command == Global.ACQUIRE:
                        resp_message = self.acquire_loco(msg_body)
                        # msg_body.reported = Global.ACQUIRED
                        self.publish_response(resp_message, msg_body.response_queue)
                        msg_consummed = True
                    elif msg_body.command == Global.THROTTLE and \
                            msg_body.sub_command == Global.STEAL:
                        resp_message = self.steal_loco(msg_body)
                        msg_body.reported = Global.ACQUIRED
                        self.publish_response(msg_body, msg_body.response_queue)
                        msg_consummed = True
                    elif msg_body.command == Global.THROTTLE and \
                            msg_body.sub_command == Global.RELEASE:
                        self.release_loco(msg_body)
                        msg_body.reported = Global.RELEASED
                        self.publish_response(msg_body, msg_body.response_queue)
                        msg_consummed = True
                    elif msg_body.command == Global.THROTTLE and \
                            msg_body.sub_command == Global.REPORT:
                        response_message = self.__get_loco_status(msg_body)
                        #print(">>> dcc response: " + str(dcc_response))
                        self.publish_response(response_message, msg_body.response_queue)
                        msg_consummed = True
                    elif msg_body.command == Global.THROTTLE and \
                            msg_body.sub_command == Global.SET_LEAD:
                        self.__set_lead(msg_body)
                        msg_body.reported = Global.LEAD_SET
                        self.publish_response(msg_body, msg_body.response_queue)
                        msg_consummed = True
                    elif msg_body.command == Global.THROTTLE and \
                            msg_body.sub_command == Global.SPEED:
                        self.slot_manager.set_loco_speed(msg_body)
                        self.__execute_throttle_message(msg_body)
                        msg_consummed = True
                    elif msg_body.command == Global.THROTTLE and \
                            msg_body.sub_command == Global.DIRECTION:
                        self.slot_manager.set_loco_direction(msg_body)
                        self.__execute_throttle_message(msg_body)
                        msg_consummed = True
                    elif msg_body.command == Global.THROTTLE and \
                            msg_body.sub_command == Global.FUNCTION:
                        self.slot_manager.set_loco_function(msg_body)
                        self.__execute_throttle_message(msg_body)
                        msg_consummed = True
                    else:
                        self.process_non_throttle_message(msg_body)
                        # non throttle: " + str(msg_body))
                        # response_message = self.send_and_wait_throttle_message(msg_body)
                        #print(">>> non throttle device response: " + str(response_message))
                        #self.publish_response(response_message, msg_body.response_queue)
                        msg_consummed = True
                elif msg_type == Global.DRIVER_SEND:
                    adjusted_message_to_send = self.adjust_device_message_before_send(msg_body)
                    device_queue = self.find_device_queue(msg_body)
                    dcc_message = self.encode_message(adjusted_message_to_send, Global.CLIENT)
                    self.__driver_send_message(device_queue, dcc_message)
                    msg_consummed = True
                elif msg_type == Global.DEVICE_INPUT:
                    self.log_info("Rcvd from Device: " + str(msg_device_identity) + ": "+ str(msg_body))
                    self.process_unsolicited_device_input_message(msg_body, msg_device_identity)
                    msg_consummed = True
        return msg_consummed

    def process_non_throttle_message(self, msg_body):
        """ process messages not related to throttles """
        # print(">>> non throttle: " + str(msg_body))
        response_message = self.send_and_wait_throttle_message(msg_body)
        #print(">>> device response: " + str(response_message))
        self.publish_response(response_message, msg_body.response_queue)

    def process_unsolicited_device_input_message(self, msg_body, _msg_device_identity):
        """ received unsolicted input from device """
        self.log_warning("Unexpected device input: " + str(msg_body))

    def encode_message(self, msg_body, source):
        """ encode a message """
        return self.encoder.encode_message(msg_body, source)

    def decode_message(self, msg_body, source):
        """ decode a message """
        return self.decoder.decode_message(msg_body, source)

    def send_and_wait_throttle_message(self, throttle_message):
        """ send throttle message and wait for response"""
        adjusted_message = self.adjust_device_message_before_send(throttle_message)
        device_queue_name = self.find_device_queue(adjusted_message)
        dcc_message = self.encode_message(adjusted_message, Global.CLIENT)
        # print(">>> send dcc message: " + str(device_queue_name) + " ... " + str(dcc_message))
        dcc_response =  \
            self.__device_send_message_and_wait_response(device_queue_name, dcc_message)
        return self.__process_device_input(dcc_response)

    def send_throttle_message(self, throttle_message):
        """ send throttle message, DO NOT wait for response"""
        adjusted_message_to_be_sent =self.adjust_device_message_before_send(throttle_message)
        device_queue_name = self.find_device_queue(adjusted_message_to_be_sent)
        dcc_message = self.encode_message(adjusted_message_to_be_sent, Global.CLIENT)
        # print(">>> send dcc message: " + str(dcc_message))
        self.__device_send_message(device_queue_name, dcc_message)

    def publish_response(self, response_data, response_queue):
        """ publish serial input """
        # print(">>> response to: " + str(response_queue) + " ... " + str(response_data))
        message = (Global.DRIVER_RESPONSE, response_data)
        resp_queue = self.queues.get(response_queue, None)
        if resp_queue is not None:
            resp_queue.put(message)

    def find_device_queue(self, _throttle_message):
        """ determine which device queue to use for sending messages """
        return Global.DEVICE

    def connect_throttle(self, throttle_message):
        """ connect a new throttle """
        # a new throttle connection, clear out any old info from a prev connection
        connected_throttle_message = self.slot_manager.connect_throttle(throttle_message)
        return connected_throttle_message

    def disconnect_throttle(self, throttle_message):
        """ disconnect a throttle"""
        disconnected_throttle_message = self.slot_manager.disconnect_throttle(throttle_message)
        return disconnected_throttle_message

    def adjust_device_message_after_read(self, throttle_message):
        """ make any needed adjustment to a throtle message after it is read """
        return throttle_message

    def adjust_device_message_before_send(self, throttle_message):
        """ make any needed adjustment to a throtle message before it is sent """
        return throttle_message

    def steal_loco(self, throttle_message):
        """ steal a loco """
        # first release it from current throttle
        steal_message = copy.deepcopy(throttle_message)
        slot_locos = self.slot_manager.find_loco_slot(steal_message)
        if slot_locos:
            (_slot_id, slot_loco) = slot_locos[0]
            #print(">>> steal loco: "+ str(slot_loco))
            steal_message.node_id = slot_loco.node_id
            steal_message.throttle_id = slot_loco.throttle_id
            steal_message.cab_id = slot_loco.cab_id
            steal_message.sub_command = Global.RELEASE
            #print(">>> steal release: " + str(steal_message))
            self.release_loco(steal_message)
            self.__send_steal_message(steal_message)
        # ... then acquire it
        throttle_message.sub_command = Global.ACQUIRE
        return self.acquire_loco(throttle_message)

    def acquire_loco(self, throttle_message):
        """ acquire a loco """
        acquired_throttle_message = \
                self.slot_manager.acquire_loco(throttle_message)
        # print(">>> acquire return: " + str(acquired_throttle_message))
        return acquired_throttle_message

    def release_loco(self, throttle_message):
        """ release a loco, remove from slot table """
        # stop the loco
        released_throttle_message = throttle_message
        slot_locos = self.slot_manager.find_loco_slot(throttle_message)
        if slot_locos:
            for loco in slot_locos:
                (slot_id, _slot_loco) = loco
                if slot_id is not None:
                    estop_message = copy.deepcopy(throttle_message)
                    estop_message.sub_command = Global.SPEED
                    estop_message.slot_id = slot_id
                    estop_message.speed = -1  # estop
                    estop_message.direction = Global.FORWARD
                    self.send_and_wait_throttle_message(estop_message)
                released_throttle_message = self.slot_manager.release_loco(throttle_message)
        # self.__dump_slots("release")
        return released_throttle_message

    #
    # private functions
    #

    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse time options section of config file """
        cab_topic = mqtt_config.publish_topics.get(Global.CAB, Global.UNKNOWN)
        # print(">>> cab topic: " + str(cab_topic))
        return (cab_topic)

    def __get_loco_status(self, throttle_message):
        """ report loco state: speed or direction """
        response_message = copy.deepcopy(throttle_message)

        slot_locos = self.slot_manager.find_loco_slot(throttle_message)
        if not slot_locos:
            response_message.reported = Global.ERROR
        else:
            (_slot_id, slot_loco) = slot_locos[0]
            if slot_loco is None:
                response_message.reported = Global.ERROR
            else:
                if throttle_message.mode == Global.SPEED:
                    response_message.speed = slot_loco.current_speed
                else:
                    response_message.direction = slot_loco.current_direction
        return response_message

    def __set_lead(self, throttle_message):
        """ set the lead loco is a cab consist """
        #  set lead: " + str(throttle_message.dcc_id))
        func_messages = []
        slot_list = self.slot_manager.find_loco_slot(throttle_message)
        if slot_list:
            old_lead_loco = self.slot_manager.get_lead_loco(slot_list)
            self.slot_manager.set_lead(throttle_message)
            slot_list = self.slot_manager.find_loco_slot(throttle_message)
            new_lead_loco = self.slot_manager.get_lead_loco(slot_list)
            if new_lead_loco.slot_id != old_lead_loco.slot_id:
                # move func setting for light, bell, horn
                func_message = ThrottleMessage()
                func_message.command = Global.THROTTLE
                func_message.sub_command = Global.FUNCTION
                for f in range(3):
                    func_message.function = f
                    if old_lead_loco.function_states[f] == 1:
                        func_message.mode = Global.ON
                    else:
                        func_message.mode = Global.OFF
                    func_message.dcc_id = new_lead_loco.dcc_id
                    func_messages += [copy.deepcopy(func_message)]
                    func_message.mode = Global.OFF
                    func_message.dcc_id = old_lead_loco.dcc_id
                    func_messages += [copy.deepcopy(func_message)]
        for func_message in func_messages:
            self.slot_manager.set_loco_function(func_message)
            updated_messages = self.__generate_updated_throttle_mesages(throttle_message)
            for updated_message in updated_messages:
                _response_message = self.send_and_wait_throttle_message(updated_message)

    def __execute_throttle_message(self, throttle_message):
        """ execute a list of throttle_messages """
        response_message = copy.deepcopy(throttle_message)
        #print(">>> throttle_message: " + str(throttle_message))
        updated_messages = self.__generate_updated_throttle_mesages(throttle_message)
        #print(">>> updatesd_messages:" + str(updated_messages))
        for updated_message in updated_messages:
            response_message = self.send_and_wait_throttle_message(updated_message)
        # print(">>> res msg: " + str(response_message))
        if isinstance(response_message, list):
            if response_message:
                response_message = response_message[0]
            else:
                response_message = throttle_message
        response_message.dcc_id = throttle_message.dcc_id
        self.publish_response(response_message, throttle_message.response_queue)

    def __generate_updated_throttle_mesages(self, throttle_message):
        """ create one or more updated throttle messages, one per each loco in cab """
        updated_messages = []
        slot_locos = self.slot_manager.find_loco_slot(throttle_message)
        # print(">>> slot_locos: " + str(slot_locos))
        if slot_locos:
            for temp_loco in slot_locos:
                (_slot_id, slot_loco) = temp_loco
                if slot_loco is not None:
                    updated_message = self.__update_throttle_message(throttle_message, slot_loco)
                    adjusted_message = self.adjust_device_message_after_read(updated_message)
                    updated_messages += [adjusted_message]
                    # print(">>> function message: " + str(throttle_message))

        return updated_messages

    def __update_throttle_message(self, throttle_message, slot_loco):
        """ update throttle message with values from slot_loco """
        # print(">>> slot loco: " + str(slot_loco))
        updated_message = copy.deepcopy(throttle_message)
        updated_message.slot_id = slot_loco.slot_id
        updated_message.dcc_id = slot_loco.dcc_id
        updated_message.speed = slot_loco.current_speed
        updated_message.direction = slot_loco.current_direction
        updated_message.items = copy.deepcopy(slot_loco.function_states)
        return updated_message

    def __parse_config(self, _config):
        """ parse options from config dict """
        max_locos=32
        if Global.OPTIONS in self.config[Global.CONFIG]:
            if Global.MAX_LOCOS in self.config[Global.CONFIG][Global.OPTIONS]:
                max_locos = self.config[Global.CONFIG][Global.OPTIONS][
                    Global.MAX_LOCOS]
        return max_locos

    def __process_device_input(self, message):
        """ decode dcc++ message """
        msg_list = message
        if not isinstance(message, list):
            msg_list = [message]
        rett = []
        for msg in msg_list:
            if msg is not None and msg != "":
                decoded_message = self.decode_message(msg, Global.SERVER)
                adjusted_message = self.adjust_device_message_after_read(decoded_message)
                rett += [adjusted_message]

        return rett

    def __device_send_message(self, device_queue_name, send_message):
        """ put a message in device_queue, wait for a reply """
        self.log_info("Sent to Device: " + str(self.name) + ": "+ str(send_message))
        dev_queue = self.queues[device_queue_name]
        send_message_map = {Global.TEXT: send_message, Global.RESPONSE_QUEUE: self.response_queue_name}
        dev_queue.put(
            (Global.DEVICE_SEND, send_message_map))

    def __device_send_message_and_wait_response(self, device_queue_name, send_message):
        """ put a message in device_queue, wait for a reply """
        self.log_info("Sent to Device: " + str(device_queue_name) + ": "+ str(send_message))
        send_message_map = {Global.TEXT: send_message, Global.RESPONSE_QUEUE: self.response_queue_name}
        # print(">>> driver response: " + str(self.response_queue))
        dev_queue = self.queues[device_queue_name]
        dev_queue.put(
            (Global.DEVICE_SEND_AND_RESPOND, send_message_map))
        response = None
        try:
            (Global.DEVICE_INPUT,
             response) = self.response_queue.get(True, 2.0)
        except Exception as _error:
            # ignore exception from timeout on get
            pass
        self.log_info("Rcvd from Device: " + str(device_queue_name) + ": "+ str(response))
        # print(">>> sync response: " + str(response))
        return response

    def __driver_send_message(self, device_queue_name, send_message):
        """ put a message in device_queue """
        self.log_debug("serial send: " + str(send_message))
        device_queue = self.queues[device_queue_name]
        device_queue.put(
            (Global.DEVICE_SEND, send_message))

    #def __dump_slots(self, ident):
    #    for _slot_id, loco in self.slot_manager.slots.items():
    #        if loco is not None:
    #            print(">>> Slot Loco: "+ str(ident) + ": [" + \
    #                str(loco.throttle_id) + "] [" + \
    #                str(loco.cab_id) + "] [" + \
    #                str(loco.dcc_id) + "] [" + \
    #                str(loco.slot_id) + "]")

    def __send_steal_message(self, steal_message):
        """ publish a data message anouncing loco stolen """
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_port_id = steal_message.port_id
        body.mqtt_throttle_id = steal_message.throttle_id
        body.mqtt_cab_id = steal_message.cab_id
        body.mqtt_loco_id = steal_message.dcc_id
        body.mqtt_reported = Global.STOLEN
        topic = self.cab_pub_topic + "/" + steal_message.node_id
        self.__publish_data_message(topic, body)

    def __publish_data_message(self, msg_topic, msg_body):
        """ format and publish responses """
        # print(">>> pub data : " + str(msg_body))
        message = (Global.PUBLISH, { \
            Global.TYPE: Global.DATA,
            Global.TOPIC: msg_topic,
            Global.BODY: msg_body
        })
        self.app_queue.put(message)
