#!/usr/bin/python3
# withrottle_driver.py
"""

        withrottle_driver - process class for a wi throttle server connection
            Client socket passed to it from a socker server
            Assumes message traffic is text based and delimited by "\n"

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
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import sys
import time

sys.path.append('../../lib')
from utils.utility import Utility
from utils.global_constants import Global
from utils.global_synonyms import Synonyms

from utils.withrottle_const import WithrottleConst
from structs.gui_message import GuiMessage
from structs.io_data import IoData

# from multiprocessing import _SemaphoreType
from decoders.withrottle_encoder import WithrottleEncoder
from decoders.withrottle_decoder import WithrottleDecoder

from processes.base_process import SendAfterMessage
from processes.base_process import BaseProcess






BUFFER_LENGTH = 4096


class CabLoco(object):
    """ informatio about a loco acquired by a cab """

    def __init__(self):
        self.loco_ident = None
        self.dcc_id = None
        self.address_type = None
        self.loco_direction = Global.FORWARD
        self.loco_speed = 0
        self.function_states = {}
        self.function_types = {}
        for f in range(0, 29):
            self.function_states[f] = Global.OFF
            self.function_types[f] = Global.TOGGLE
        self.function_types[2] = Global.BUTTON  # normlly "horn" function

    def __repr__(self):
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"


class ThrottleCab(object):
    """ objext that encapsulate info about a throttle cabs """

    def __init__(self):
        self.cab_id = None
        self.cab_locos = {}

    def __repr__(self):
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"


class WithrottleDriver(BaseProcess):
    """
       process wi throttle protocol for one connected throttle device
    """

    def __init__(self,
                 identity=None,
                 mode=None,
                 events=None,
                 in_queue=None,
                 app_queue=None,
                 device_queue=None,
                 roster=None,
                 switches=None,
                 log_queue=None):
        super().__init__(name=mode + ":" + identity,
                         events=events,
                         in_queue=in_queue,
                         app_queue=app_queue,
                         log_queue=log_queue)
        self.identity = identity
        self.mode = mode
        self.device_queue = device_queue
        self.init_info_sent = False
        self.fastclock_seconds = Utility.now_seconds()
        self.fastclock_ratio = 1
        self.roster = roster
        self.switches = switches
        self.decoder = WithrottleDecoder(log_queue=log_queue)
        self.encoder = WithrottleEncoder(log_queue=log_queue)
        self.fastclock_send_after_message = None
        self.roster_locos = []
        self.roster_locos_by_name = {}
        self.cabs = {}
        self.loco_cab_signals = {}
        self.traffic_control = False
        self.auto_signals = False

    def initialize_process(self):
        """ iitialize this process """
        super().initialize_process()
        self.log_info("Init withrottle server process")
        self.__parse_roster_names()
        self.fastclock_send_after_message = \
            SendAfterMessage(Global.SEND + "-" + Global.FASTCLOCK, None, 10000)
        self.send_after(self.fastclock_send_after_message)

    def process_message(self, new_message=None):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            (msg_type, msg_body) = new_message
            if msg_type == Global.DEVICE_INPUT:
                # data read from socket client
                self.__process_input_from_client(msg_body)
                msg_consummed = True
            elif msg_type == Global.DEVICE_CLOSE:
                self.send_to_application(new_message)
            elif msg_type == Global.FASTCLOCK:
                # receved updated fastclock from tower
                self.__update_fastclock(msg_body)
            elif msg_type == Global.CAB_SIGNAL:
                self.__update_cab_signal(msg_body)
            elif msg_type == Global.SWITCHES:
                # update the list of switches
                self.switches = msg_body
                self.__send_turnouts()
            elif msg_type == Global.SEND + "-" + Global.FASTCLOCK:
                # send fastclock to throttle
                self.send_after(self.fastclock_send_after_message)
                self.__send_fastclock()
            elif msg_type == Global.ACQUIRE:
                self.__send_acquire_response(msg_body)
                msg_consummed = True
            elif msg_type == Global.RELEASE:
                self.__send_release_response(msg_body)
                msg_consummed = True
            elif msg_type == Global.STOLEN:
                self.__send_stolen_response(msg_body)
                msg_consummed = True
            elif msg_type == Global.SPEED:
                # ignore,don't send speed response
                # self.__send_speed_response(msg_body)
                msg_consummed = True
            elif msg_type == Global.DIRECTION:
                self.__send_direction_response(msg_body)
                msg_consummed = True
            elif msg_type == Global.REPORT:
                self.__send_report_response(msg_body)
                msg_consummed = True
            elif msg_type == Global.FUNCTION:
                self.__send_function_response(msg_body)
                msg_consummed = True
            elif msg_type == Global.SWITCH:
                self.__send_switch_response(msg_body)
                msg_consummed = True
        return msg_consummed

    def process_other(self):
        """ perform other none message relared tasks """
        super().process_other()
        pass

    def shutdown_process(self):
        """ close client socket"""
        # print(">>> closing socket_client_process")
        super().shutdown_process()
        pass

    #
    # private functions
    #

    def __send_acquire_response(self, msg_body):
        """ process response from acquire command """
        sub_command = Global.ACQUIRE
        if msg_body.mqtt_reported == Global.ACQUIRED:
            sub_command = Global.ACQUIRE
        elif msg_body.mqtt_reported in [Global.ERROR]:
            sub_command = Global.RELEASE
        elif msg_body.mqtt_reported == Global.STEAL_NEEDED:
            sub_command = Global.STEAL
        cab_id = msg_body.mqtt_cab_id
        cab = self.cabs[cab_id]
        loco_ident = self.__find_loco_ident(cab_id, msg_body.mqtt_loco_id)
        cab_loco = cab.cab_locos[loco_ident]
        new_message = GuiMessage()
        new_message.command = Global.THROTTLE
        new_message.sub_command = sub_command
        new_message.cab_id = cab_id
        new_message.name = loco_ident
        self.__send_to_client(new_message)
        if sub_command == Global.ACQUIRE:
            self.__send_initial_loco_function_info(cab_id, loco_ident,
                                                   cab_loco)
            self.__send_direction(cab_id, loco_ident, Global.FORWARD)
            self.__send_speed(cab_id, loco_ident, 0)
            self.__send_speed_step(cab_id, loco_ident, 1)

    def __send_release_response(self, msg_body):
        """ process response from release command """
        sub_command = Global.RELEASE
        if msg_body.mqtt_reported in [Global.RELEASED, Global.ERROR]:
            sub_command = Global.RELEASE
        cab_id = msg_body.mqtt_cab_id
        loco_ident = self.__find_loco_ident(cab_id, msg_body.mqtt_loco_id)
        new_message = GuiMessage()
        new_message.command = Global.THROTTLE
        new_message.sub_command = sub_command
        new_message.cab_id = cab_id
        new_message.dcc_id = msg_body.mqtt_loco_id
        new_message.name = loco_ident
        self.__send_to_client(new_message)

    def __send_stolen_response(self, msg_body):
        """ process response from acquire/release command """
        message = "Alert: Loco " + \
            str(msg_body.mqtt_loco_id) + \
            " has been stolen by aother throttle !!!"
        self.__send_alert(message)

        cab_id = msg_body.mqtt_cab_id
        loco_ident = self.__find_loco_ident(cab_id, msg_body.mqtt_loco_id)
        new_message = GuiMessage()
        new_message.command = Global.THROTTLE
        new_message.sub_command = Global.RELEASE
        new_message.cab_id = cab_id
        new_message.dcc_id = msg_body.mqtt_loco_id
        new_message.name = loco_ident
        self.__send_to_client(new_message)

    #def __send_speed_response(self, msg_body):
    #    """ send response to throttle for speed commands """
    #    # reported is a dictionary, may contains speed
    #    cab_id = msg_body.mqtt_cab_id
    #    loco_ident = self.__find_loco_ident(cab_id, msg_body.mqtt_loco_id)
    #    for key, value in msg_body.mqtt_reported.items():
    #        if key == Global.SPEED:
    #            self.__send_speed(cab_id, loco_ident, value)

    def __send_direction_response(self, msg_body):
        """ send response to throttle for direction commands """
        # reported is a dictionary, may contains direction
        cab_id = msg_body.mqtt_cab_id
        loco_ident = self.__find_loco_ident(cab_id, msg_body.mqtt_loco_id)
        for key, value in msg_body.mqtt_reported.items():
            if key == Global.DIRECTION:
                self.__send_direction(cab_id, loco_ident, value)

    def __send_report_response(self, msg_body):
        """ send response to report (query) commands """
        # reported is a dictionary, may contains speed or direction
        cab_id = msg_body.mqtt_cab_id
        loco_ident = self.__find_loco_ident(cab_id, msg_body.mqtt_loco_id)
        for key, value in msg_body.mqtt_reported.items():
            if key == Global.SPEED:
                self.__send_query_speed(cab_id, loco_ident, value)
            if key == Global.DIRECTION:
                self.__send_query_direction(cab_id, loco_ident, value)

    def __send_function_response(self, msg_body):
        """ send response to throttle for function commands """
        # reported is a dictionary, contains function id and mode
        cab_id = msg_body.mqtt_cab_id
        loco_ident = self.__find_loco_ident(cab_id, msg_body.mqtt_loco_id)
        reported = msg_body.mqtt_reported
        if isinstance(reported, dict):
            func = msg_body.mqtt_reported.get(Global.FUNCTION, 0)
            mode = msg_body.mqtt_reported.get(Global.STATE, Global.OFF)
            self.__send_function(cab_id, loco_ident, func, mode)

    def __send_switch_response(self, msg_body):
        """ send response to throttle for turnout switch commands """
        # print(">>> \n\n\n ...turnout switch: " + str(msg_body))
        node_id = msg_body.mqtt_node_id
        port_id = msg_body.mqtt_port_id
        new_message = GuiMessage()
        if port_id == Global.POWER:
            new_message.command = Global.POWER
        elif msg_body.mqtt_port_id == Global.TRAFFIC:
            self.traffic_control = Synonyms.is_on(msg_body.mqtt_reported)
        elif msg_body.mqtt_port_id == Global.AUTO_SIGNALS:
            self.auto_signals = Synonyms.is_on(msg_body.mqtt_reported)
        else:
            new_message.command = Global.SWITCH
            switch = self.__find_switch(node_id, port_id)
            if switch is not None:
                port_id = switch.port_id
                node_id = switch.node_id
                switch.mode = msg_body.mqtt_reported
        new_message.port_id = port_id
        new_message.node_id = node_id
        new_message.mode = msg_body.mqtt_reported
        # print(">>> turnout switch 2: " + str(new_message))
        self.__send_to_client(new_message)

    def __find_loco_ident(self, cab_id, dcc_id):
        """ find a loco ident given cab and dcc_id """
        loco_ident = None
        throttle_cab = self.cabs.get(cab_id, None)
        if throttle_cab is not None:
            for _key, loco in throttle_cab.cab_locos.items():
                if loco.dcc_id == dcc_id:
                    loco_ident = loco.loco_ident
                    break
        return loco_ident

    def __process_input_from_client(self, msg_body):
        """ process inpute from client socket """
        self.log_debug("Rcvd from Client: " + str(msg_body))
        #print(">>> before decode: " + str(msg_body))
        decoded_message = self.decoder.decode_message(
            msg_body, source="client")
        #print(">>> after decode: " + str(decoded_message))
        command = decoded_message.command
        sub = decoded_message.sub_command
        if command is not None:
            if command == Global.NAME:
                self.__send_version()
                if not self.init_info_sent:
                    self.__send_server_name()
                    self.__send_roster()
                    self.__send_power_status()
                    self.__send_turnouts()
                    self.__send_routes()
                    self.__send_consists()
                    self.__send_heartbeat_setting()
                    self.__send_fastclock()
                    self.init_info_sent = True
            elif command == Global.THROTTLE:
                if sub == Global.ACQUIRE:
                    self.__publish_acquire(decoded_message)
                elif sub == Global.STEAL:
                    self.__publish_acquire(decoded_message, steal_mode=True)
                elif sub == Global.RELEASE:
                    self.__publish_release(decoded_message)
                elif sub == Global.SPEED:
                    self.__publish_speed(decoded_message)
                elif sub == Global.DIRECTION:
                    self.__publish_direction(decoded_message)
                elif sub == Global.FUNCTION:
                    self.__publish_function(decoded_message)
            elif command == Global.SWITCH:
                self.__publish_turnout_switch(decoded_message)
            elif command == Global.POWER:
                self.__publish_power(decoded_message)

    def __send_consists(self):
        """ send consist message """
        if self.roster is not None:
            consists = self.roster.consists
            # print(">>> consists: " + str(consists))
            consist_len = len(consists)
            new_message = GuiMessage()
            new_message.command = Global.CONSIST
            new_message.sub_command = Global.COUNT
            new_message.value = consist_len
            self.__send_to_client(new_message)
            for _key, consist in consists.items():
                # print(">>> consist: " + str(consist))
                loco_list = []
                for loco in consist.locos:
                    new_loco = GuiMessage()
                    new_loco.dcc_id = loco.dcc_id
                    new_loco.address_type = \
                        self.__address_type_from_dcc_id(loco.dcc_id)
                    new_loco.mode = loco.direction
                    loco_list.append(new_loco)
                new_consist_message = GuiMessage()
                new_consist_message.command = Global.CONSIST
                new_consist_message.sub_command = Global.LIST
                new_consist_message.name = consist.name
                new_consist_message.dcc_id = consist.dcc_id
                new_consist_message.address_type = \
                    self.__address_type_from_dcc_id(consist.dcc_id)
                new_consist_message.items = loco_list
                self.__send_to_client(new_consist_message)

    def __send_fastclock(self):
        """ send power message """
        new_message = GuiMessage()
        new_message.command = Global.FASTCLOCK
        new_message.value = self.fastclock_seconds
        new_message.items = {Global.RATIO: str(self.fastclock_ratio)}
        self.__send_to_client(new_message)

    def __send_heartbeat_setting(self):
        """ send heartbeat setting"""
        new_message = GuiMessage()
        new_message.command = Global.PING
        new_message.value = 10
        self.__send_to_client(new_message)

    def __send_power_status(self):
        """ send power message """
        new_message = GuiMessage()
        new_message.command = Global.POWER
        new_message.mode = Global.ON
        self.__send_to_client(new_message)

    def __send_roster(self):
        """ send roster message """
        new_message = GuiMessage()
        new_message.command = Global.ROSTER
        new_message.items = self.roster_locos
        self.__send_to_client(new_message)

    def __send_routes(self):
        """ send route message """
        new_message = GuiMessage()
        new_message.command = Global.ROUTE
        new_message.sub_command = Global.LABEL
        new_message.name = "Routes"
        new_message.items = \
            {
                Global.ON: WithrottleConst.ACTIVATED,
                Global.OFF: WithrottleConst.DEACTIVATED
            }
        self.__send_to_client(new_message)

        new_message = GuiMessage()
        new_message.command = Global.ROUTE
        new_message.sub_command = Global.LIST
        new_message.items = []
        self.__send_to_client(new_message)

    def __send_server_name(self):
        """ send server id info message """
        new_message = GuiMessage()
        new_message.command = Global.INFO
        new_message.sub_command = Global.SERVER
        new_message.text = "MQTT-LCP"
        # lie to withrottle client
        # it wont show roster unless we are say we are JMRI
        #new_message.text = "JMRI"
        self.__send_to_client(new_message)

        new_message = GuiMessage()
        new_message.command = Global.INFO
        new_message.sub_command = Global.ADD
        new_message.text = "MQTT-LCP-WITHROTTLE-SERVER, version 1.0"
        self.__send_to_client(new_message)

    def __send_turnouts(self):
        """ send turnout """
        new_message = GuiMessage()
        new_message.command = Global.TURNOUT
        new_message.sub_command = Global.LABEL
        new_message.name = "Turnouts"
        new_message.items = \
            {
                Global.CLOSE: "Closed",
                Global.THROW: "Thrown"
            }
        self.__send_to_client(new_message)

        new_message = GuiMessage()
        new_message.command = Global.TURNOUT
        new_message.sub_command = Global.LIST
        new_message.items = self.switches
        self.__send_to_client(new_message)

    def __send_version(self):
        """ send verion message """
        new_message = GuiMessage()
        new_message.command = Global.VERSION
        new_message.text = "2.0"
        self.__send_to_client(new_message)

    def __send_initial_loco_function_info(self, cab_id, loco_ident, cab_loco):
        """ send loco function info """
        #print(">>> cab_loco: " + str(cab_loco))
        if self.roster is not None:
            roster_loco = self.roster.locos.get(str(cab_loco.dcc_id), None)
            labels = []
            if roster_loco is None:
                labels.append("Light")
            else:
                for _key, func in roster_loco.functions.items():
                    if func.type == Global.BUTTON:
                        if func.name in range(0, 29):
                            cab_loco.function_types[func.name] = Global.BUTTON
                    labels.append(func.label)
            #print(">>> labels: " + str(labels))
            list_len = len(labels)
            if list_len < 29:  # 0-28
                for _i in range(list_len, 29):
                    labels.append("")
            self.__send_function_labels(cab_id, loco_ident, labels)
            if roster_loco is None:
                for func in range(29):  # 0-28
                    self.__send_function(cab_id, loco_ident, func, Global.OFF)
            else:
                count = 0
                for _key, func in roster_loco.functions.items():
                    count += 1
                    self.__send_function(
                        cab_id, loco_ident, func.name, Global.OFF)
                if count < 29:  # 0-28
                    for _i in range(count, 29):
                        self.__send_function(cab_id, loco_ident, func.name,
                                             Global.OFF)

    def __send_function(self, cab_id, loco_ident, func, mode):
        """ send loco function change to client """
        new_message = GuiMessage()
        new_message.command = Global.THROTTLE
        new_message.sub_command = Global.FUNCTION
        new_message.cab_id = cab_id
        new_message.name = loco_ident
        new_message.function = func
        new_message.mode = mode
        self.__send_to_client(new_message)

    def __send_function_labels(self, cab_id, loco_ident, labels):
        """ send loco function change to client """
        #print(">>> labels: " + str(len(labels)))
        new_message = GuiMessage()
        new_message.command = Global.THROTTLE
        new_message.sub_command = Global.LABEL
        new_message.cab_id = cab_id
        new_message.name = loco_ident
        new_message.items = labels
        self.__send_to_client(new_message)

    def __send_speed(self, cab_id, loco_ident, speed):
        """ send loco speed to client """
        new_message = GuiMessage()
        new_message.command = Global.THROTTLE
        new_message.sub_command = Global.SPEED
        new_message.cab_id = cab_id
        new_message.name = loco_ident
        new_message.speed = speed
        self.__send_to_client(new_message)

    def __send_direction(self, cab_id, loco_ident, direction):
        """ send loco direction to client """
        new_message = GuiMessage()
        new_message.command = Global.THROTTLE
        new_message.sub_command = Global.DIRECTION
        new_message.cab_id = cab_id
        new_message.name = loco_ident
        new_message.direction = direction
        self.__send_to_client(new_message)

    def __send_query_speed(self, cab_id, loco_ident, speed):
        """ send loco direction to client """
        new_message = GuiMessage()
        new_message.command = Global.THROTTLE
        new_message.sub_command = Global.REPORT
        new_message.cab_id = cab_id
        new_message.name = loco_ident
        new_message.speed = speed
        new_message.mode = Global.SPEED
        self.__send_to_client(new_message)

    def __send_query_direction(self, cab_id, loco_ident, direction):
        """ send loco direction to client """
        new_message = GuiMessage()
        new_message.command = Global.THROTTLE
        new_message.sub_command = Global.REPORT
        new_message.cab_id = cab_id
        new_message.name = loco_ident
        new_message.direction = direction
        new_message.mode = Global.DIRECTION
        self.__send_to_client(new_message)

    def __send_alert(self, message):
        """ send alert message to client """
        new_message = GuiMessage()
        new_message.command = Global.ALERT
        new_message.text = message
        self.__send_to_client(new_message)

    #def __send_info(self, message):
    #    """ send info message to client """
    #    new_message = GuiMessage()
    #    new_message.command = Global.INFO
    #    new_message.text = message
    #    self.__send_to_client(new_message)

    def __send_speed_step(self, cab_id, loco_ident, step):
        """ send loco speed to client """
        new_message = GuiMessage()
        new_message.command = Global.THROTTLE
        new_message.sub_command = Global.STEP
        new_message.cab_id = cab_id
        new_message.name = loco_ident
        new_message.mode = step
        self.__send_to_client(new_message)

    def __send_direction(self, cab_id, loco_ident, direction):
        """ send loco direction to client """
        new_message = GuiMessage()
        new_message.command = Global.THROTTLE
        new_message.sub_command = Global.STEP
        new_message.cab_id = cab_id
        new_message.name = loco_ident
        new_message.mode = direction
        self.__send_to_client(new_message)

    def __send_to_client(self, new_message):
        """ encode and send a command to client """
        #print(">>> new message to send: " + str(new_message))
        encoded_message = self.encoder.encode_message(new_message)
        self.log_debug("Send to Client: " + str(encoded_message))
        self.device_queue.put(
            (
                Global.DEVICE_SEND,
                encoded_message
            ))

    def __publish_acquire(self, message, steal_mode=False):
        """ throttle request to acquire a new loco """
        # print(">>> acquire: " + str(message))
        cab_id = message.cab_id
        cab = self.cabs.get(cab_id, ThrottleCab())
        cab.cab_id = cab_id
        cab_loco = CabLoco()
        cab_loco.loco_ident = message.name
        if message.dcc_id is not None:
            cab_loco.dcc_id = message.dcc_id
        elif message.text:
            roster_loco = self.roster.locos.get(str(message.text), None)
            if roster_loco is not None:
                cab_loco.dcc_id = roster_loco.dcc_id
        # print(">>> cab dcc_id: "+ str(cab_loco.dcc_id))
        cab_loco.address_type = message.address_type
        cab_loco.loco_direction = Global.FORWARD
        cab_loco.loco_speed = 0
        cab.cab_locos[cab_loco.loco_ident] = cab_loco
        # print(">>> cab_locos: " + str(cab.cab_locos))
        self.cabs[cab_id] = cab
        body = IoData()
        body.mqtt_message_root = Global.CAB
        body.mqtt_throttle_id = self.identity
        body.mqtt_cab_id = cab.cab_id
        body.mqtt_loco_id = cab_loco.dcc_id
        if steal_mode:
            body.mqtt_desired = Global.STEAL
        else:
            body.mqtt_desired = Global.ACQUIRE
        self.app_queue.put((Global.PUBLISH,
                            {
                                Global.SUB: Global.COMMAND,
                                Global.BODY: body
                            }))

    def __publish_release(self, message):
        """ throttle request to release a new loco """
        cab_id = message.cab_id
        loco_ident = message.name
        cab = self.cabs.get(cab_id, ThrottleCab())
        dcc_ids = []
        if loco_ident != "*":
            # a single loco
            cab_loco = cab.cab_locos[loco_ident]
            dcc_ids = [cab_loco.dcc_id]
        else:
            for _key, loco in cab.cab_locos.items():
                dcc_ids.append(loco.dcc_id)
        for dcc_id in dcc_ids:
            body = IoData()
            body.mqtt_message_root = Global.CAB
            body.mqtt_throttle_id = self.identity
            body.mqtt_cab_id = cab.cab_id
            body.mqtt_loco_id = dcc_id
            body.mqtt_desired = Global.RELEASE
            self.app_queue.put((Global.PUBLISH,
                                {
                                    Global.SUB: Global.COMMAND,
                                    Global.BODY: body
                                }))
        self.__remove_locos_from_cab_locos(cab, dcc_ids)

    def __remove_locos_from_cab_locos(self, cab, dcc_id_list):
        """ move released locos from list of locos in use """
        new_cab_locos = {}
        for key, loco in cab.cab_locos.items():
           # print(">>> cab loco: " + str(loco))
            if loco.dcc_id not in dcc_id_list:
                new_cab_locos[key] = loco
        cab.cab_locos = new_cab_locos

    def __publish_speed(self, message):
        """ throttle request loco speed  """
        cab_id = message.cab_id
        loco_ident = message.name
        cab = self.cabs.get(cab_id, ThrottleCab())
        dcc_ids = []
        if loco_ident != "*":
            # a single loco
            cab_loco = cab.cab_locos[loco_ident]
            dcc_ids = [cab_loco.dcc_id]
        else:
            for _key, loco in cab.cab_locos.items():
                dcc_ids.append(loco.dcc_id)
        for dcc_id in dcc_ids:
            body = IoData()
            body.mqtt_message_root = Global.CAB
            body.mqtt_throttle_id = self.identity
            body.mqtt_cab_id = cab.cab_id
            body.mqtt_loco_id = dcc_id
            body.mqtt_desired = {Global.SPEED: message.speed}
            self.app_queue.put((Global.PUBLISH,
                                {
                                    Global.SUB: Global.COMMAND,
                                    Global.BODY: body
                                }))

    def __publish_direction(self, message):
        """ throttle request loco direction  """
        # print(">>> direction: " + str(message))
        cab_id = message.cab_id
        loco_ident = message.name
        cab = self.cabs.get(cab_id, ThrottleCab())
        dcc_ids = []
        if loco_ident != "*":
            # a single loco
            cab_loco = cab.cab_locos[loco_ident]
            dcc_ids = [cab_loco.dcc_id]
        else:
            for _key, loco in cab.cab_locos.items():
                dcc_ids.append(loco.dcc_id)
        for dcc_id in dcc_ids:
            body = IoData()
            body.mqtt_message_root = Global.CAB
            body.mqtt_throttle_id = self.identity
            body.mqtt_cab_id = cab.cab_id
            body.mqtt_loco_id = dcc_id
            body.mqtt_desired = {Global.DIRECTION: message.direction}
            self.app_queue.put((Global.PUBLISH,
                                {
                                    Global.SUB: Global.COMMAND,
                                    Global.BODY: body
                                }))

    def __publish_function(self, message):
        """
            throttle request loco function

            Function on/off sent by withrottle are really
            button pressed(down) or released (up).
            How they impact the loco depends on whether the button up/down
            is treated asa toggle or monentary switch.

            A toggle, such as the LIGHT function , are treated as follows:
                withrtottle ON: send turn function ON to command station
                withrottle OFF: ignore
                withrtootle ON: send turn function OFF to command station
                withrottle OFF: ignore

            A monentary button, such as the HORN function, are treated as follows
                withrottle ON:  send  function ON to the command station
                withrottle OFF: send funcyion OFF to the command station
        """
        cab_id = message.cab_id
        loco_ident = message.name
        cab = self.cabs.get(cab_id, ThrottleCab())
        locos = []
        if loco_ident != "*":
            # a single loco
            cab_loco = cab.cab_locos[loco_ident]
            locos.append(cab_loco)
        else:
            for _key, loco in cab.cab_locos.items():
                locos.append(loco)
        for loco in locos:
            mode = message.mode
            func = message.function
            publish = False
            ftype = loco.function_types.get(func, None)
            # print(">>> type: " + str(func) + " ... " + str(ftype))
            if ftype is not None:
                # print(">>> types: " + str(loco.function_types))
                if ftype == Global.TOGGLE:
                    # only act on ON, ignore OFF
                    if message.mode == Global.ON:
                        publish = True
                        # flip function states
                        if loco.function_states[func] == Global.ON:
                            loco.function_states[func] = Global.OFF
                        else:
                            loco.function_states[func] = Global.ON
                        mode = loco.function_states[func]
                else:
                    publish = True
                    loco.function_states[func] = mode
            if publish:
                body = IoData()
                body.mqtt_message_root = Global.CAB
                body.mqtt_throttle_id = self.identity
                body.mqtt_cab_id = cab.cab_id
                body.mqtt_loco_id = loco.dcc_id
                body.mqtt_desired = \
                    {
                        Global.FUNCTION: func,
                        Global.STATE: mode
                    }
                self.app_queue.put((Global.PUBLISH,
                                    {
                                        Global.SUB: Global.COMMAND,
                                        Global.BODY: body
                                    }))

    def __publish_turnout_switch(self, message):
        """ publish a switch request command """
        #print(">>> switch req: " + str(message))
        switch_parts = message.port_id.split(WithrottleConst.PORT_SEP)
        if len(switch_parts) > 1:
            node_id = switch_parts[0]
            port_id = switch_parts[1]
            switch = self.__find_switch(node_id, port_id)
            if switch is not None and \
                    switch.command_topic is not None:
                #print(">>> toggle: " + str(message.mode) + " ... " +
                #   str(switch))
                desired = message.mode
                #print(">>> desired: "+str(desired) + " : " + str(switch.mode))
                if desired == Global.TOGGLE:
                    if switch.mode == Global.CLOSED:
                        desired = Global.THROW
                    else:
                        desired = Global.CLOSE
                group = Global.SWITCH
                if node_id ==  Global.ROUTE:
                    group = Global.ROUTE
                    if Synonyms.is_off(desired):
                        desired = Global.OFF
                    else:
                        desired = Global.ON
                # print(">>> switch 2: " + str(switch))
                topic = switch.command_topic
                body = IoData()
                body.mqtt_message_root = group
                body.mqtt_node_id = self.__get_topic_node_id(topic)
                body.mqtt_port_id = port_id
                body.mqtt_desired = desired
                #print(">>> switch 5: "+str(body))
                self.app_queue.put((Global.PUBLISH,
                                    {
                                        Global.SUB: group,
                                        Global.TOPIC: topic,
                                        Global.BODY: body
                                    }))

    def __publish_power(self, message):
        """ publish a power request command """
        body = IoData()
        body.mqtt_message_root = Global.SWITCH
        body.mqtt_port_id = Global.POWER
        body.mqtt_desired = message.mode
        self.app_queue.put((Global.PUBLISH,
                            {
                                Global.SUB: Global.SWITCH,
                                Global.BODY: body
                            }))

    def __parse_roster_names(self):
        """ parse roster locos and build a name list """
        # print(">>> roster: " + str(self.roster))
        self.roster_locos = []
        self.roster_locos_by_name = {}
        # print(">>> roster: " + str(self.roster))
        if self.roster is not None:
            for (_key, loco) in self.roster.locos.items():
               # print(">>> roster loco: " + str(loco))
                dcc_id = loco.dcc_id
                name = loco.name
                address_type = self.__address_type_from_dcc_id(dcc_id)
                loco = GuiMessage()
                loco.name = name
                loco.dcc_id = dcc_id
                loco.address_type = address_type
                self.roster_locos.append(loco)
                self.roster_locos_by_name[name] = dcc_id
            #print(">>> roster locos: " + str(self.roster_locos))
            # print(">>> roster locos by dcc_id: " +

    def __address_type_from_dcc_id(self, dcc_id):
        """ determine address type """
       # print(">>> dccid: " + str(dcc_id))
        address_type = "L"
        if int(dcc_id) < 128:
            address_type = "S"
        return address_type

    def __find_switch(self, node_id, port_id):
        """ find a switch in the list """
        rett = None
        for switch in self.switches:
            if switch.node_id == node_id and \
                    switch.port_id == port_id:
                rett = switch
                break
        return rett

    def __update_cab_signal(self, msg_body):
        """ send cab signal to withthrottle device """
        last_signal = self.loco_cab_signals.get(msg_body.mqtt_loco_id, None)
        if last_signal != msg_body.mqtt_reported:
            # only process changes in signal aspect for any given loco
            self.loco_cab_signals.update({msg_body.mqtt_loco_id: msg_body.mqtt_reported})
            if self.cabs is not None:
                for _cab_id, cab in self.cabs.items():
                    if cab.cab_locos is not None:
                        for _loco_id, loco in cab.cab_locos.items():
                            if loco.dcc_id == msg_body.mqtt_loco_id:
                                message = "Cab Signal for Loco " + \
                                    str(msg_body.mqtt_loco_id) + \
                                        " is " + msg_body.mqtt_reported.upper()
                                self.__send_alert(message)

    def __update_fastclock(self, msg_body):
        """ update fastclock with data from tower """
        print("... update fastclock")
        if msg_body.mqtt_message_root == Global.FASTCLOCK:
            if msg_body.mqtt_metadata is not None:
                if Global.FASTCLOCK in msg_body.mqtt_metadata:
                    fastclock = msg_body.mqtt_metadata[Global.FASTCLOCK]
                    seconds = fastclock.get(Global.EPOCH, None)
                    # tower published epoch based on UTC, convert it to local
                    utc_obj = time.localtime(seconds)
                    # get the timezone offset
                    local_offset = utc_obj.tm_gmtoff
                    # convert utc epoch to locla time zone
                    seconds += local_offset
                    ratio = msg_body.mqtt_metadata.get(Global.RATIO, 1)
                    if seconds is None:
                        seconds = Utility.now_seconds()
                    self.fastclock_seconds = int(seconds)
                    self.fastclock_ratio = int(ratio)

    def __get_topic_node_id(self, topic):
        """ parse out node id from topic """
        node_id = Global.UNKNOWN
        if topic is not None:
            topic_parts = topic.split("/")
            if len(topic_parts) > 3:
                node_id = topic_parts[3]
        return node_id
