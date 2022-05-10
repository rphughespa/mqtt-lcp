#!/usr/bin/python3
# withrottle_encoder.py
"""

	withrottle_encoder.py - helper class to encode withrottle messages
    Encodes withrottle messages from dictionaries of values.
    Tested with WiThrottle v3.4.2, Engine Driver v2.29.127


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

sys.path.append('../../lib')

from utils.global_constants import Global
from utils.utility import Utility
from structs.withrottle_const import WithrottleConst


class WithrottleEncoder:
    """ encode withrottle messages """
    def __init__(self, log_queue=None):
        self.log_queue = log_queue

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def encode_message(self, message, source=Global.CLIENT):
        """ parse a withtottle command """
        self.log_queue.put(
            (Global.LOG_LEVEL_DEBUG,
             "Encode: [" + str(message) + "]"))
        rett = {Global.COMMAND: Global.UNKNOWN, Global.TEXT: str(message)}
        if message:
            command = message.command
            sub_command = message.sub_command
            if command == Global.VERSION:
                rett = self.encode_version_command(message)
            elif command == Global.ALERT:
                rett = self.encode_alert_command(message)
            elif command == Global.INFO:
                rett = self.encode_message_command(message)
            elif command == Global.ROSTER:
                rett = self.encode_roster_list_command(message)
            elif command == Global.FASTCLOCK:
                rett = self.encode_fastclock_command(message)
            elif command == Global.POWER:
                rett = self.encode_track_power_command(message)
            elif command == Global.TURNOUT and sub_command == Global.LABEL:
                rett = self.encode_turnouts_command(message)
            elif command == Global.TURNOUT and sub_command == Global.LIST:
                rett = self.encode_turnouts_list_command(message)
            elif command == Global.SWITCH:
                rett = self.encode_turnouts_switch_command(message)
            elif command == Global.ROUTE and sub_command == Global.LABEL:
                rett = self.encode_routes_command(message)
            elif command == Global.ROUTE and sub_command == Global.SWITCH:
                rett = self.encode_routes_switch_command(message)
            elif command == Global.ROUTE and sub_command == Global.LIST:
                rett = self.encode_routes_list_command(message)
            elif command == Global.CONSIST and sub_command == Global.LIST:
                rett = self.encode_consists_entry_command(message)
            elif command == Global.CONSIST and sub_command == Global.COUNT:
                rett = self.encode_consists_count_command(message)
            elif command == Global.ADDRESS:
                rett = self.encode_web_address_command(message)
            elif command == Global.THROTTLE:
                rett = self.encode_throttle_command(message)
            elif command == Global.INFO:
                rett = self.encode_info_command(message)
            elif command == Global.HEX:
                rett = self.encode_hex_command(message)
            elif command == Global.PING:
                rett = self.encode_heartbeat_command(message)
            elif command == Global.NAME:
                rett = self.encode_name_command(message)
            elif command == Global.DISCONNECT:
                rett = self.encode_quit_command(message)
            else:
                self.log_queue.put(
                    (Global.LOG_LEVEL_WARNING,
                     "!!! Unrecognized Command[" + str(command)))
        self.log_queue.put(
            (Global.LOG_LEVEL_DEBUG, " .. : [" + str(rett) + "]"))
        return rett

    def encode_roster_list_command(self, message):
        """ deocde roster """
        # RL2]\[RGS 41}|{41}|{L]\[Test Loco}|{1234}|{L
        roster_list = message.items
        rett = "RL"
        rett += str(len(roster_list))
        for roster_entry in roster_list:
            address_type = "L"
            if roster_entry.dcc_id < 128:
                address_type = "S"
            rett +=  \
                WithrottleConst.MAJOR_SEP + \
                roster_entry.name + WithrottleConst.MINOR_SEP + \
                str(roster_entry.dcc_id) + WithrottleConst.MINOR_SEP + \
                address_type
        return rett

    def encode_track_power_command(self, message):
        """ encode track power """
        # PPA1
        track_power = message.mode
        rett = "PPA2"
        if track_power == Global.ON:
            rett = "PPA1"
        elif track_power == Global.OFF:
            rett = "PPA0"
        return rett

    def encode_turnouts_command(self, message):
        """ encode turnouts """
        #PTT]\[Turnouts}|{Turnout]\[Closed}|{2]\[Thrown}|{4
        rett = "PTT" + WithrottleConst.MAJOR_SEP
        rett += message.name
        rett += WithrottleConst.MINOR_SEP + "Turnout"
        rett += WithrottleConst.MAJOR_SEP + message.items.get(Global.CLOSE, "")
        rett += WithrottleConst.MINOR_SEP + str(WithrottleConst.CLOSED)
        rett += WithrottleConst.MAJOR_SEP + message.items.get(Global.THROW, "")
        rett += WithrottleConst.MINOR_SEP + str(WithrottleConst.THROWN)
        return rett

    def encode_turnouts_list_command(self, message):
        """ encode turnouts """
        # PTL]\[LT12}|{Rico Station N}|{1]\[LT324}|{Rico Station S}|{2
        rett = "PTL"
        turnout_list = message.items
        for turnout in turnout_list:
            # print(">>> turnout: " + str(turnout))
            turnout_state = turnout.mode
            if turnout_state == Global.CLOSED:
                turnout_state = WithrottleConst.CLOSED
            elif turnout_state == Global.THROWN:
                turnout_state = WithrottleConst.THROWN
            elif turnout_state == Global.UNKNOWN:
                turnout_state = WithrottleConst.UNKNOWN
            port = turnout.port_id
            if turnout.node_id is not None:
                port = turnout.node_id + WithrottleConst.PORT_SEP + turnout.port_id
            rett += WithrottleConst.MAJOR_SEP + \
                port + WithrottleConst.MINOR_SEP  + \
                turnout.name + WithrottleConst.MINOR_SEP + \
                str(turnout_state)
        return rett

    def encode_turnouts_switch_command(self, message):
        """ encode turnout throw/close """
        # PTA2LT2"
        #print(">>> switch: " + str(message))
        rett = "PTA"
        mode = WithrottleConst.UNKNOWN
        smode = message.mode
        if smode is not None:
            if smode == Global.THROW:
                mode = "T"
            elif smode == Global.CLOSE:
                mode = "C"
            elif smode == Global.TOGGLE:
                mode = WithrottleConst.CLOSED
            elif smode == Global.CLOSED:
                mode = WithrottleConst.CLOSED
            elif smode == Global.THROWN:
                mode = WithrottleConst.THROWN
            elif smode == Global.UNKNOWN:
                mode = WithrottleConst.UNKNOWN
        port = message.port_id
        if message.node_id is not None:
            port = message.node_id + WithrottleConst.PORT_SEP + message.port_id
        rett += str(mode) + str(port)
        return rett

    def encode_routes_command(self, message):
        """ encode routes """
        # PRT]\[Routes}|{Route]\[Active}|{2]\[Inactive}|{4
        # route_label = Global.ROUTE
        rett = "PRT" + WithrottleConst.MAJOR_SEP
        rett += message.name
        rett += WithrottleConst.MINOR_SEP + "Route"
        rett += WithrottleConst.MAJOR_SEP + message.items.get(Global.ACTIVATED)
        rett += WithrottleConst.MINOR_SEP + str(WithrottleConst.ACTIVE)
        rett += WithrottleConst.MAJOR_SEP + message.items.get(
            Global.DEACTIVATED)
        rett += WithrottleConst.MINOR_SEP + str(WithrottleConst.INACTIVE)
        return rett

    def encode_routes_list_command(self, message):
        """ encode route list """
        # "PRL]\[IR:AUTO:0001}|{Rico Main}|{"
        rett = "PRL"
        route_list = message.items
        for route in route_list:
            rett += WithrottleConst.MAJOR_SEP + \
                route.port_id + WithrottleConst.MINOR_SEP  + \
                route.name + WithrottleConst.MINOR_SEP
        return rett

    def encode_routes_switch_command(self, message):
        """ encode route throw/close """
        # PRA2IR200
        rett = "PRA"
        mode = WithrottleConst.UNKNOWN
        smode = message.mode
        if smode is not None:
            if smode == Global.DEACTIVATED:
                mode = WithrottleConst.INACTIVE
            elif smode == Global.ACTIVATED:
                mode = WithrottleConst.ACTIVE
        rett += str(mode) + str(message.port_id)
        return rett

    def encode_consists_entry_command(self, message):
        """ encode consists """
        # RCD}|{74(S)}|{74(S)]\[3374(L)}|{true]\[346(L)}|{true
        address_type = "L"
        if message.dcc_id < 128:
            address_type = "S"
        rett = "RCD" + WithrottleConst.MINOR_SEP
        rett += str(message.dcc_id)
        rett += "(" + address_type + ")"
        rett += WithrottleConst.MINOR_SEP
        rett += message.name
        consist_list = message.items
        for loco in consist_list:
            addr_type = "L"
            if loco.dcc_id < 128:
                addr_type = "S"
            rett += WithrottleConst.MAJOR_SEP
            rett += str(loco.dcc_id)
            rett += "(" + addr_type + ")"
            rett += WithrottleConst.MINOR_SEP
            if loco.direction == Global.FORWARD:
                rett += "true"
            else:
                rett += "false"
        return rett

    def encode_consists_count_command(self, message):
        """ encode consist count command"""
        # RCC2
        count = message.value
        rett = "RCC" + str(count)
        return rett

    def encode_fastclock_command(self, message):
        """ encode fastclock """
        # PFT1550686525<;>4
        epoch_seconds = message.value
        ratio = message.items.get(Global.RATIO, "1.o")
        rett = "PFT" + str(epoch_seconds) + WithrottleConst.SUB_SEP + \
            str(ratio)
        return rett

    def encode_alert_command(self, message):
        """ encode alert message """
        # M=HMmessage
        rett = "HM" + message.text
        return rett

    def encode_message_command(self, message):
        """ encode info message """
        # M=Hmmessage
        rett = "Hm" + message.text
        return rett

    def encode_name_command(self, message):
        """ encode name """
        # NThrottleName
        rett = "N" + message.name
        return rett

    def encode_info_command(self, message):
        """ encode id """
        # HU12356, HT123456, HM.., Hm..
        rett = "H"
        sub = message.sub_command
        if sub == Global.SERVER:
            rett += "T"
        elif sub == Global.ADD:
            rett += "t"
        elif sub == Global.USER:
            rett += "U"
        elif sub == Global.ALERT:
            rett += "M"
        elif sub == Global.MESSAGE:
            rett += 'm'
        rett += message.text
        return rett

    def encode_version_command(self, message, _source=Global.SERVER):
        """ encode version """
        # VN2.0
        rett = "VN" + message.text
        return rett

    def encode_throttle_command(self, message):
        """ encode throttle """
        rett = ""
        sub = message.sub_command
        if sub == Global.ACQUIRE:
            rett = self.__encode_throttle_acquire(message)
        elif sub == Global.RELEASE:
            rett = self.__encode_throttle_release(message)
        elif sub == Global.STEAL:
            rett = self.__encode_throttle_steal(message)
        elif sub == Global.LABEL:
            rett = self.__encode_throttle_function_labels(message)
        elif sub == Global.CONSIST:
            rett = self.__encode_throttle_consist(message)
        elif sub == Global.LEAD:
            rett = self.__encode_throttle_set_lead(message)
        elif sub == Global.FUNCTION:
            rett = self.__encode_throttle_function(message)
        elif sub in [Global.SPEED, Global.IDLE]:
            rett = self.__encode_throttle_speed(message)
        elif sub == Global.DIRECTION:
            rett = self.__encode_throttle_direction(message)
        elif sub == Global.STEP:
            rett = self.__encode_throttle_speed_step(message)
        elif sub == Global.REPORT:
            rett = self.__encode_throttle_query(message)
        return rett

    def encode_web_address_command(self, message):
        """ encode web port address """
        # PW12080
        rett = "PW" + str(message.port_id)
        return rett

    def encode_hex_command(self, message):
        """ encode hex command """
        # D0a05
        rett = "D" + message.text
        return rett

    def encode_heartbeat_command(self, message):
        """ encode heartbeat """
        rett = "*"
        time = message.value
        if time is not None:
            rett += str(time)
        else:
            mode = message.mode
            if mode is not None:
                if mode == Global.ON:
                    rett += "+"
                elif mode == Global.OFF:
                    rett += "-"
        return rett

    def encode_panel_command(self, _message):
        """ encode panel """
        # not supported
        rett = ""
        return rett

    def encode_quit_command(self, _message):
        """ encode quit """
        rett = "Q"
        return rett

    #
    # private functions
    #

    def __encode_throttle_acquire(self, message):
        """ parse throttle acquire loco(s) """
        # MT+L341<;>ED&RGW 341
        #print(">>> encode throttle: " + str(message))
        loco = message.name
        if message.dcc_id is not None:
            loco = self.__convert_loco_ref(message.dcc_id)
        #print(">>> ... loco: " + str(loco))
        rett = "M" + str(message.cab_id)+ "+" + \
                str(loco) + \
                WithrottleConst.SUB_SEP
        if message.text:
            # loco id is a roster ref
            rett += message.text
        return rett

    def __encode_throttle_steal(self, message):
        """ parse throttle acquire steal loco(s) """
        # MTSL341<;>ED&RGW 341
        loco = message.name
        if message.dcc_id is not None:
            loco = self.__convert_loco_ref(message.dcc_id)
        rett = "M" + str(message.cab_id)+ "S" + \
                loco + \
                WithrottleConst.SUB_SEP
        if message.dcc_id:
            address_type = "L"
            if message.dcc_id < 128:
                address_type = "S"
            rett += address_type + \
                 str(message.dcc_id)
        return rett

    def __encode_throttle_release(self, message):
        """ parse throttle release loco(s) """
        # MT-L341<;>ED&RGW 341
        loco = message.name
        if message.dcc_id is not None:
            loco = self.__convert_loco_ref(message.dcc_id)
        rett = "M" + str(message.cab_id)+ "-" + \
                loco + \
                WithrottleConst.SUB_SEP
        option = None
        if isinstance(message.items, dict):
            option = message.items.get(Global.OPTIONS, None)
        if option is not None:
            rett += option
        return rett

    def __encode_throttle_consist(self, message):
        """ parse throttle acquire a consist """
        # MT+L341<;>ED&RGW 341
        loco = message.name
        if message.dcc_id is not None:
            loco = self.__convert_loco_ref(message.dcc_id)
        rett = "M" + str(message.cab_id)+ "A" + \
                loco + \
                WithrottleConst.SUB_SEP
        if message.dcc_id:
            address_type = "L"
            if message.dcc_id < 128:
                address_type = "S"
            rett += "C"+ address_type + \
                 str(message.dcc_id)
        elif message.text:
            # loco id is a consist ref
            rett += "c" + message.text
        return rett

    def __encode_throttle_function_labels(self, message):
        """ parse throttle functions labels """
        # MTLL41<;>]\[Headlight]\[Bell]\[Whistle]\[Short Whistle]\[Steam Release]\[FX5 Light]\[  .. ]\[]\[]\[
        loco = message.name
        if message.dcc_id is not None:
            loco = self.__convert_loco_ref(message.dcc_id)
        rett = "M"+message.cab_id+ "L"+ loco + \
            WithrottleConst.SUB_SEP
        label_list = message.items
        for label in label_list:
            rett += WithrottleConst.MAJOR_SEP + label
        return rett

    def __encode_throttle_set_lead(self, message):
        """ encode set lead """
        # MTAL341<;>cD&RGW 341
        # MTAL341<;>cL346
        # 'c' is a roster id, 'C' is a loco address
        loco = message.name
        if message.dcc_id is not None:
            loco = self.__convert_loco_ref(message.dcc_id)
        rett = "M"+message.cab_id + 'A' + \
                loco + \
                WithrottleConst.SUB_SEP
        if message.address_type is None:
            # loco id is not an address, it is a roster id
            rett += "C" + str(message.dcc_id)
        else:
            address_type = "L"
            if message.dcc_id < 128:
                address_type = "S"
            rett += "C" + address_type + str(message.dcc_id)
        return rett

    def __encode_throttle_function(self, message):
        """ encode function """
        # MTA*<;>F112
        loco = message.name
        if message.dcc_id is not None:
            loco = self.__convert_loco_ref(message.dcc_id)
        rett = "M"+message.cab_id + 'A' + \
                str(loco) + \
                WithrottleConst.SUB_SEP
        force = None
        if isinstance(message.items, dict):
            force = message.items.get(Global.OPTIONS, None)
        if force is not None and force == Global.FORCE:
            rett += 'f'
        else:
            rett += "F"
        mode = message.mode
        if mode == Global.ON:
            rett += "1"
        else:
            rett += "0"
        rett += str(message.function)
        return rett

    def __encode_throttle_speed(self, message):
        """ encode speed """
        # MTA*<;>V30
        loco = message.name
        if message.dcc_id is not None:
            loco = self.__convert_loco_ref(message.dcc_id)
        rett = "M"+message.cab_id + 'A' + \
                loco + \
                WithrottleConst.SUB_SEP
        speed = message.speed
        if message.sub_command == Global.IDLE:
            # idle
            rett += "I"
        elif speed == -1:
            # estop
            rett += "X"
        else:
            rett += "V" + str(speed)
        return rett

    def __encode_throttle_direction(self, message):
        """ encode direction """
        # MTA*<;>R0
        #print(">>> direction: " + str(message))
        loco = message.name
        if message.dcc_id is not None:
            loco = self.__convert_loco_ref(message.dcc_id)
        rett = "M"+str(message.cab_id) + 'A' + \
                loco + \
                WithrottleConst.SUB_SEP
        direction = WithrottleConst.FORWARD
        if message.direction == Global.REVERSE:
            direction = WithrottleConst.REVERSE
        rett += "R" + str(direction)
        return rett

    def __encode_throttle_speed_step(self, message):
        """ encode speed step """
        _name = message.dcc_id
        # MTAL5887<;>s1
        loco = message.name
        if message.dcc_id is not None:
            loco = self.__convert_loco_ref(message.dcc_id)
        rett = "M"+str(message.cab_id) + 'A' + \
                loco + \
                WithrottleConst.SUB_SEP
        rett += "s" + str(message.mode)
        return rett

    def __encode_throttle_query(self, message):
        """ encode query """
        loco = message.name
        if message.dcc_id is not None:
            loco = self.__convert_loco_ref(message.dcc_id)
        rett = "M"+str(message.cab_id) + 'A' + \
                loco + \
                WithrottleConst.SUB_SEP
        query = message.mode
        if query == Global.SPEED:
            # M0A*<;>qV
            rett+= "qV"
            #rett += "V"
            #rett += str(message.speed)
        elif query == Global.DIRECTION:
            # M0A*<;>qR
            rett += "qR"
            #rett += "R"
            #direction = WithrottleConst.FORWARD
            #if message.direction == Global.REVERSE:
            #    direction = WithrottleConst.REVERSE
            #rett += str(direction)
        return rett

    def __convert_loco_ref(self, dcc_id):
        """ convert dcc_id into a withrotle loco address """
        # print(">>> convert loco: " + str(dcc_id))
        loco = dcc_id
        if isinstance(loco, str):
            if Utility.is_number(loco):
                loco = int(loco)
        if isinstance(loco, int):
            if loco < 128:
                loco = "S"+str(loco)
            else:
                loco = "L"+str(loco)
        # print(">>> ... " + str(loco))
        return loco
