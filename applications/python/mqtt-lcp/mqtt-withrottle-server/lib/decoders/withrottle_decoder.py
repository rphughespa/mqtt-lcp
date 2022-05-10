#!/usr/bin/python3
# withrottle_decoder.py
"""

	withrottle_decoder.py - helper class to decode withrottle messages
    Decodes withrottle text messages into dictionaries of values.
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
import datetime

sys.path.append('../../lib')

from utils.global_constants import Global
from utils.utility import Utility

from structs.throttle_message import ThrottleMessage
from structs.withrottle_const import WithrottleConst

CLOSED = 2
THROWN = 4
UNKNOWN = 1
ACTIVE = 2
INACTIVE = 4
FORWARD = 1
REVERSE = 0
MAJOR_SEP = "]\\["
MINOR_SEP = "}|{"
SUB_SEP = "<;>"
PORT_SEP = ":"


class WithrottleDecoder:
    """ decode withrottle messages """
    def __init__(self, log_queue=None):
        self.log_queue = log_queue

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def decode_message(self, message, source=Global.CLIENT):
        """ parse a withtottle command """
        self.log_queue.put(
            (Global.LOG_LEVEL_DEBUG,
             "Decode: [" + str(source) + "] ... [" + str(message) + "]"))
        rett = {Global.COMMAND: Global.UNKNOWN, Global.TEXT: str(message)}
        # print(">>> Decode: " + str(message))
        in_message = message.strip()
        #print(">>> ... stripped: " + str(in_message))
        if in_message:
            command_parts = in_message.split(WithrottleConst.MAJOR_SEP)
            command = command_parts[0].strip()
            del command_parts[0]
            #self.log_queue.put(Global.LOG_LEVEL_WARNING, "Process Parsed Command[" + \
            #       str(command)+"]["+str(command_parts)+"]")
            #print(">>> ... split: " + str(command)+"]["+str(command_parts)+"]")
            first_byte = ""
            if command:
                first_byte = command[0]
            # print(">>> command: " + str(command))
            if command.startswith("VN"):
                rett = self.decode_version_command(command, command_parts)
            elif command.startswith("RL"):
                rett = self.decode_roster_list_command(command, command_parts)
            elif command.startswith("PFT"):
                rett = self.decode_fastclock_command(command, command_parts)
            elif command.startswith("PFC"):
                rett = self.decode_pfc_command(command, command_parts)
            elif command.startswith("PPA"):
                rett = self.decode_track_power_command(command, command_parts)
            elif command.startswith("PTA"):
                rett = self.decode_turnouts_switch_command(
                    command, command_parts, source)
            elif command.startswith("PTT"):
                # fix bug in LNW1 PTT message
                fixed_message = in_message.replace("][", "]\\[")
                command_parts = fixed_message.split(WithrottleConst.MAJOR_SEP)
                command = command_parts[0].strip()
                del command_parts[0]
                # end of LNW1 fix
                # print(">>> parts: " + str(command_parts))
                rett = self.decode_turnouts_command(command, command_parts)
            elif command.startswith("PTL"):
                rett = self.decode_turnouts_list_command(
                    command, command_parts)
            elif command.startswith("PRT"):
                rett = self.decode_routes_command(command, command_parts)
            elif command.startswith("PRL"):
                rett = self.decode_routes_list_command(command, command_parts)
            elif command.startswith("PRA"):
                rett = self.decode_routes_switch_command(
                    command, command_parts)
            elif command.startswith("RCD"):
                rett = self.decode_consists_entry_command(
                    command, command_parts)
            elif command.startswith("RCC"):
                rett = self.decode_consists_count_command(
                    command, command_parts)
            elif command.startswith("PW"):
                rett = self.decode_web_address_command(command, command_parts)
            elif command.startswith("M"):
                rett = self.decode_throttle_command(command, command_parts)
            elif first_byte == "H":
                rett = self.decode_info_command(command, command_parts)
            elif first_byte == "D":
                rett = self.decode_hex_command(command, command_parts)
            elif first_byte == "*":
                rett = self.decode_heartbeat_command(command, command_parts)
            elif first_byte == "N":
                rett = self.decode_name_command(command, command_parts)
            elif first_byte == "P":
                rett = self.decode_panel_command(command, command_parts)
            elif first_byte == "Q":
                rett = self.decode_quit_command(command, command_parts)
            else:
                self.log_queue.put(
                    (Global.LOG_LEVEL_WARNING, "!!! Unrecognized Command[" +
                     str(command) + "]...[" + str(command_parts) + "]"))
                rett = ThrottleMessage()
                rett.command = Global.UNKNOWN
                rett.text = message
        self.log_queue.put((Global.LOG_LEVEL_DEBUG, " .... : " + str(rett)))
        return rett

    def decode_roster_list_command(self, _command, command_parts):
        """ deocde roster """
        # RL2]\[RGS 41}|{41}|{L]\[Test Loco}|{1234}|{L
        rosters = []
        for roster_entry in command_parts:
            roster_entry_parts = roster_entry.split(WithrottleConst.MINOR_SEP)
            roster_entry_name = ""
            roster_entry_address = ""
            roster_entry_address_type = ""
            if len(roster_entry_parts) > 0:
                roster_entry_name = roster_entry_parts[0]
            if len(roster_entry_parts) > 1:
                roster_entry_address = roster_entry_parts[1]
            if len(roster_entry_parts) > 2:
                roster_entry_address_type = roster_entry_parts[2]
            #self.roster[roster_entry_name] = {
            #    "address": roster_entry_address,
            #    "address_type": roster_entry_address_type
            #}
            roster_item = ThrottleMessage()
            roster_item.name = roster_entry_name
            roster_item.dcc_id = int(roster_entry_address)
            roster_item.address_type = roster_entry_address_type.upper()
            rosters.append(roster_item)
        roster_list = ThrottleMessage()
        roster_list.command = Global.ROSTER
        roster_list.items = rosters
        return roster_list

    def decode_track_power_command(self, command, _command_parts):
        """ decode track power """
        # PPA1
        track_power = Global.UNKNOWN
        if command == "PPA0":
            track_power = Global.OFF
        elif command == "PPA1":
            track_power = Global.ON
        elif command == "PPA2":
            track_power = Global.UNKNOWN
        power_command = ThrottleMessage()
        power_command.command = Global.POWER
        power_command.mode = track_power
        # print(">>> decode: " + str(command) + " ... " + str(power_command))
        return power_command

    def decode_turnouts_command(self, _command, command_parts):
        """ decode turnouts """
        #PTT]\[Turnouts}|{Turnout]\[Closed}|{2]\[Thrown}|{4
        turnout_label = Global.TURNOUT
        close_label = Global.UNKNOWN
        throw_label = Global.UNKNOWN
        for turnouts in command_parts:
            turnout_parts = turnouts.split(WithrottleConst.MINOR_SEP)
            #print(">>> turn sub parts: " + str(turnout_parts))
            part_lower = turnout_parts[1].lower()
            #print(">>> part lower: " + str(part_lower) + " ... " +
            #      str(Utility.is_number(part_lower)))
            if part_lower == "turnout":
                turnout_label = turnout_parts[0]
            elif Utility.is_number(part_lower):
                part_number = int(part_lower)
                if part_number == WithrottleConst.CLOSED:
                    close_label = turnout_parts[0]
                elif part_number == WithrottleConst.THROWN:
                    throw_label = turnout_parts[0]
        label_list = {}
        label_list[Global.CLOSE] = close_label
        label_list[Global.THROW] = throw_label
        turnout_command = ThrottleMessage()
        turnout_command.command = Global.TURNOUT
        turnout_command.sub_command = Global.LABEL
        turnout_command.name = turnout_label
        turnout_command.items = label_list
        return turnout_command

    def decode_turnouts_switch_command(self, command, _command_parts, source):
        """ decode turnout throw / close """
        # code for throw, close vary if request or response
        # PTA2LT203
        #print(">>> switch: " + str(command))

        mode = command[3]
        if Utility.is_number(mode):
            mode = int(mode)
        rmode = Global.UNKNOWN
        if source == Global.SERVER:
            #server response
            if mode in ["C", WithrottleConst.CLOSED]:
                rmode = Global.CLOSED
            elif mode in ["T", WithrottleConst.THROWN]:
                rmode = Global.THROWN
        else:
            # client request
            if mode == WithrottleConst.CLOSED:
                rmode = Global.TOGGLE
            elif rmode == "C":
                rmode = Global.CLOSE
            elif rmode == "T":
                rmode = Global.THROW
        turnout = command[4:]
        switch_command = ThrottleMessage()
        switch_command.command = Global.SWITCH
        switch_command.port_id = turnout
        switch_command.mode = str(rmode)
        # print(">>> decode switch: " + str(switch_command))
        return switch_command

    def decode_turnouts_list_command(self, _command, command_parts):
        """ decode turnouts """
        # PTL]\[LT12}|{Rico Station N}|{1]\[LT324}|{Rico Station S}|{2
        turnouts = []
        for turnout_entry in command_parts:
            turnout_entry_parts = turnout_entry.split(
                WithrottleConst.MINOR_SEP)
            turnout_system_name = ""
            turnout_user_name = ""
            turnout_state = Global.UNKNOWN
            if len(turnout_entry_parts) > 0:
                turnout_system_name = turnout_entry_parts[0]
            if len(turnout_entry_parts) > 1:
                turnout_user_name = turnout_entry_parts[1]
            if len(turnout_entry_parts) > 2:
                turnout_state = Global.UNKNOWN
                state = turnout_entry_parts[2]
                if Utility.is_number(state):
                    state = int(state)
                if state == WithrottleConst.CLOSED:
                    turnout_state = Global.CLOSED
                elif state == WithrottleConst.THROWN:
                    turnout_state = Global.THROWN
            turnout = ThrottleMessage()
            turnout.port_id = turnout_system_name
            turnout.name = turnout_user_name
            turnout.mode = turnout_state
            turnouts.append(turnout)
        turnout_list = ThrottleMessage()
        turnout_list.command = Global.TURNOUT
        turnout_list.sub_command = Global.LIST
        turnout_list.items = turnouts
        return turnout_list

    def decode_routes_command(self, _command, command_parts):
        """ decode routes """
        # PRT]\[Routes}|{Route]\[Active}|{2]\[Inactive}|{4
        # route_label = Global.ROUTE
        route_title = None
        route_state_active = Global.UNKNOWN
        route_state_deactive = Global.UNKNOWN
        for routes in command_parts:
            route_parts = routes.split(WithrottleConst.MINOR_SEP)
            part_lower = route_parts[1].lower()
            if part_lower == "route":
                route_title = route_parts[0]
            elif Utility.is_number(part_lower):
                part_number = int(part_lower)
                if part_number == WithrottleConst.ACTIVE:
                    route_state_active = route_parts[0]
                elif part_number == WithrottleConst.INACTIVE:
                    route_state_deactive = route_parts[0]
        label_list = {}
        label_list[Global.UNKNOWN] = 1
        label_list[Global.ACTIVATED] = route_state_active
        label_list[Global.DEACTIVATED] = route_state_deactive
        route_command = ThrottleMessage()
        route_command.command = Global.ROUTE
        route_command.sub_command = Global.LABEL
        route_command.name = route_title
        route_command.items = label_list
        return route_command

    def decode_routes_list_command(self, _command, command_parts):
        """ decode routes """
        # PRL]\[IR:AUTO:0001}|{Rico Main}|{
        routes = []
        for route_entry in command_parts:
            route_entry_parts = route_entry.split(WithrottleConst.MINOR_SEP)
            route_system_name = ""
            route_user_name = ""
            if len(route_entry_parts) > 0:
                route_system_name = route_entry_parts[0]
            if len(route_entry_parts) > 1:
                route_user_name = route_entry_parts[1]
            route = ThrottleMessage()
            route.port_id = route_system_name
            route.name = route_user_name
            routes.append(route)
        route_list = ThrottleMessage()
        route_list.command = Global.ROUTE
        route_list.sub_command = Global.LIST
        route_list.items = routes
        return route_list

    def decode_routes_switch_command(self, command, _command_parts):
        """ decode route inactive / active """
        # PRA2IR200
        mode = command[3]
        if Utility.is_number(mode):
            mode = int(mode)
        rmode = Global.UNKNOWN
        if mode == WithrottleConst.ACTIVE:
            rmode = Global.ACTIVATED
        elif mode == WithrottleConst.INACTIVE:
            rmode = Global.DEACTIVATED
        route = command[4:]
        route_command = ThrottleMessage()
        route_command.command = Global.ROUTE
        route_command.sub_command = Global.SWITCH
        route_command.port_id = route
        route_command.mode = str(rmode)
        return route_command

    def decode_consists_entry_command(self, command, command_parts):
        """ decode consists """
        # RCD}|{74(S)}|{74(S)]\[3374(L)}|{true]\[346(L)}|{true
        # this comand reverses the major an minor separators
        # do a special parsing
        id_parts = command.split(WithrottleConst.MINOR_SEP)
        consist_addr = id_parts[1]
        consist_id = id_parts[2]
        (consist_addr_id, consist_addr_address_type) = \
                self.__parse_loco_address(consist_addr)
        consist_list = []
        for consist_part in command_parts:
            consist_part_parts = consist_part.split(WithrottleConst.MINOR_SEP)
            loco_addr = consist_part_parts[0]
            loco_facing = Global.FORWARD
            if len(consist_part_parts) > 1:
                if consist_part_parts[1].lower() == "false":
                    loco_facing = Global.REVERSE
            (loco_id, address_type) = self.__parse_loco_address(loco_addr)
            loco = ThrottleMessage()
            loco.dcc_id = int(loco_id)
            loco.address_type = address_type
            loco.mode = loco_facing
            consist_list.append(loco)
        consist_list_command = ThrottleMessage()
        consist_list_command.command = Global.CONSIST
        consist_list_command.sub_command = Global.LIST
        consist_list_command.name = consist_id
        consist_list_command.dcc_id = int(consist_addr_id)
        consist_list_command.address_type = consist_addr_address_type
        consist_list_command.items = consist_list
        return consist_list_command

    def decode_consists_count_command(self, command, _command_parts):
        """ decode consist count command"""
        # RCC2
        ncount = 0
        count = command[3:]
        if not count:
            count = "0"
        if Utility.is_number(count):
            ncount = int(count)
        else:
            ncount = -1
        consist_command = ThrottleMessage()
        consist_command.command = Global.CONSIST
        consist_command.sub_command = Global.COUNT
        consist_command.value = ncount
        return consist_command

    def decode_fastclock_command(self, command, _command_parts):
        """ decode fastclock """
        # PFT1550686525<;>4
        clock_epoch_seconds = -1
        clock_fast_ratio = 1
        fast_time = ""
        clock_values = command[3:]
        clock_entries = clock_values.split(WithrottleConst.SUB_SEP)
        if len(clock_entries) > 0:
            seconds = clock_entries[0]
            if Utility.is_number(seconds):
                clock_epoch_seconds = int(seconds)
            if len(clock_entries) > 1:
                ratio = clock_entries[1]
                if Utility.is_number(ratio):
                    clock_fast_ratio = ratio
            try:
                fast_time = datetime.datetime.fromtimestamp(
                    int(clock_epoch_seconds)).isoformat()
            except Exception as ex:
                self.log_queue.put(("warning", "Fastclock exception: " + ex))
        fastclock_command = ThrottleMessage()
        fastclock_command.command = Global.FASTCLOCK
        fastclock_command.value = clock_epoch_seconds
        fastclock_command.text = fast_time
        fastclock_command.items = {Global.RATIO: clock_fast_ratio}
        return fastclock_command

    def decode_name_command(self, command, _command_parts):
        """ decode name """
        # print(">>> decode name")
        name = command[1:]
        name_command = ThrottleMessage()
        name_command.command = Global.NAME
        name_command.name = name
        return name_command

    def decode_info_command(self, command, _command_parts):
        """ decode user id """
        ctype = command[1]
        idd = command[2:]
        sub = Global.USER
        if ctype == "U":
            sub = Global.USER
        elif ctype == "T":
            sub = Global.SERVER
        elif ctype == "t":
            sub = Global.ADD
        elif ctype == "M":
            sub = Global.ALERT
        elif ctype == "m":
            sub = Global.MESSAGE
        info_command = ThrottleMessage()
        info_command.command = Global.INFO
        info_command.sub_command = sub
        info_command.text = idd
        return info_command

    def decode_version_command(self, command, _command_parts):
        """ decode version """
        version = command[2:]
        version_command = ThrottleMessage()
        version_command.command = Global.VERSION
        version_command.text = version
        return version_command

    def decode_throttle_command(self, command, command_parts):
        """ decode throttle """
        rett = ThrottleMessage()
        rett.command = Global.UNKNOWN
        rett.text = str(command) + " ... " + str(command_parts)
        throttle_action = command[2]
        if throttle_action == "+":
            rett = self.__parse_throttle_acquire(command, command_parts)
        elif throttle_action == "-":
            rett = self.__parse_throttle_release(command, command_parts)
        elif throttle_action == "S":
            rett = self.__parse_throttle_steal(command, command_parts)
        elif throttle_action == "L":
            rett = self.__parse_throttle_function_labels(
                command, command_parts)
        elif throttle_action == "A":
            rett = self.__parse_throttle_actions(command, command_parts)
        return rett

    def decode_web_address_command(self, command, _command_parts):
        """ decode web port address """
        # PW12080
        port = command[2:]
        if Utility.is_number(port):
            port = int(port)
        address_command = ThrottleMessage()
        address_command.command = Global.ADDRESS
        address_command.sub_command = Global.PORT
        address_command.port_id = port
        return address_command

    def decode_hex_command(self, command, _command_parts):
        """ decode hex command """
        # D0a05
        hexx = command[2:]
        hex_command = ThrottleMessage()
        hex_command.command = Global.HEX
        hex_command.text = hexx
        return hex_command

    def decode_heartbeat_command(self, command, _command_parts):
        """ decode heartbeat """
        rett = ThrottleMessage()
        rett.command = Global.PING
        if len(command) > 1:
            time = command[1:]
            if Utility.is_number(time):
                time = int(time)
                rett.value = time
            elif time == "+":
                rett.mode = Global.ON
            elif time == "-":
                rett.mode = Global.OFF
        return rett

    def decode_panel_command(self, command, command_parts):
        """ decode pannel """
        # ignore, not documented
        panel_command = ThrottleMessage()
        panel_command.command = Global.PANELS
        panel_command.text = str(command) + " ... " + str(command_parts)
        return panel_command

    def decode_pfc_command(self, command, command_parts):
        """ pfc command from LNW1 """
        # ignore, not documented
        pfc_command = ThrottleMessage()
        pfc_command.command = Global.UNKNOWN
        pfc_command.text = str(command) + " ... " + str(command_parts)
        return pfc_command

    def decode_quit_command(self, _command, _command_parts):
        """ decode quit """
        quit_command = ThrottleMessage()
        quit_command.command = Global.DISCONNECT
        return quit_command

    #
    # private functions
    #

    def __parse_throttle_acquire(self, command, _command_parts):
        """ parse throttle acquire loco(s) """
        # MT+L341<;>ED&RGW 341
        throttle_cab = command[1]
        throttle_target = command[3:]
        throttle_parts = throttle_target.split(WithrottleConst.SUB_SEP)
        # print(">>> acquire throttle parts: " + str(throttle_parts))
        loco_ref = throttle_parts[0]
        rett = ThrottleMessage()
        rett.command = Global.THROTTLE
        rett.sub_command = Global.ACQUIRE
        rett.cab_id = throttle_cab
        rett.name = loco_ref
        rett.text = throttle_parts[1]
        if rett.text is not None:
            rett.text = rett.text
        if rett.text == "" or \
                rett.text.startswith("E"):
            (loco_id, address_type) = self.__parse_loco_address(rett.name)
            rett.dcc_id = int(loco_id)
            rett.address_type = address_type
        else:
            (loco_id, address_type) = self.__parse_loco_address(rett.text)
            rett.dcc_id = int(loco_id)
            rett.address_type = address_type
        return rett

    def __parse_throttle_steal(self, command, _command_parts):
        """ parse throttle acquire steal loco(s) """
        # MTSL341<;>ED&RGW 341
        throttle_cab = command[1]
        throttle_target = command[3:]
        throttle_parts = throttle_target.split(WithrottleConst.SUB_SEP)
        loco_ref = throttle_parts[0]
        rett = ThrottleMessage()
        rett.command = Global.THROTTLE
        rett.sub_command = Global.STEAL
        rett.cab_id = throttle_cab
        rett.name = loco_ref
        rett.text = throttle_parts[1]
        if rett.text is not None:
            rett.text = rett.text
        if rett.text == "" or \
                rett.text.startswith("E"):
            (loco_id, address_type) = self.__parse_loco_address(rett.name)
            rett.dcc_id = int(loco_id)
            rett.address_type = address_type
        else:
            (loco_id, address_type) = self.__parse_loco_address(rett.text)
            rett.dcc_id = int(loco_id)
            rett.address_type = address_type
        return rett

    def __parse_throttle_release(self, command, _command_parts):
        """ parse throttle release loco(s) """
        # MT-L341<;>r
        throttle_cab = command[1]
        throttle_target = command[3:]
        throttle_parts = throttle_target.split(WithrottleConst.SUB_SEP)
        loco_ref = throttle_parts[0]
        rett = ThrottleMessage()
        rett.command = Global.THROTTLE
        rett.sub_command = Global.RELEASE
        rett.cab_id = throttle_cab
        rett.name = loco_ref
        # loco_id = throttle_parts[1].strip()
        if len(throttle_parts) > 1:
            rett.items = {Global.OPTIONS: throttle_parts[1]}
        return rett

    def __parse_throttle_function_labels(self, command, command_parts):
        """ parse throttle functions labels """
        # MTLL41<;>]\[Headlight]\[Bell]\[Whistle]\[Short Whistle]\[Steam Release]\[FX5 Light]\[  ... ]\[]\[]\[
        throttle_cab = command[1]
        throttle_target = command[3:]
        throttle_parts = throttle_target.split(WithrottleConst.SUB_SEP)
        loco_ref = throttle_parts[0]
        rett = ThrottleMessage()
        rett.command = Global.THROTTLE
        rett.sub_command = Global.LABEL
        rett.cab_id = throttle_cab
        rett.name = loco_ref
        rett.items = command_parts
        return rett

    def __parse_throttle_actions(self, command, _command_parts):
        """ parse throttle actions """
        throttle_cab = command[1]
        throttle_target = command[3:]
        throttle_parts = throttle_target.split(WithrottleConst.SUB_SEP)
        loco_ref = throttle_parts[0]
        sub_action_part = throttle_parts[1]
        sub_action = sub_action_part[0]
        # print(">>> action: " + str(sub_action) + " ... " +
        #      str(sub_action_part))
        rett = ThrottleMessage()
        rett.command = Global.THROTTLE
        rett.cab_id = throttle_cab
        rett.name = loco_ref
        if sub_action in ["C", "c"]:
            # set consist lead
            rett.sub_command = Global.CONSIST
            loco_id = sub_action_part[1:]
            if sub_action == "c":
                # roster reference
                rett.text = loco_id
            else:
                (loco_id, address_type) = self.__parse_loco_address(loco_id)
                rett.sub_command = Global.LEAD
                rett.dcc_id = int(loco_id)
                rett.address_type = address_type
        elif sub_action in ["F", "f"]:
            # set function
            mode = Global.ON
            on_off = sub_action_part[1]
            if on_off == "0":
                mode = Global.OFF
            function = sub_action_part[2:].strip()
            if Utility.is_number(function):
                function = int(function)
            rett.sub_command = Global.FUNCTION
            rett.function = function
            rett.mode = mode
            if sub_action == "f":
                rett.items = {Global.OPTIONS: Global.FORCE}
        elif sub_action == "I":
            # idle
            rett.sub_command = Global.SPEED
            rett.speed = 0
        elif sub_action == "L":
            # ignore set long, not documentated
            pass
        elif sub_action == "m":
            # ignore monentary. not documentated
            pass
        elif sub_action == "q":
            # query
            query = None
            if sub_action_part == "qV":
                query = Global.SPEED
            elif sub_action_part == "qR":
                query = Global.DIRECTION
            if query is not None:
                rett.sub_command = Global.REPORT
                rett.mode = query
        elif sub_action == "Q":
            rett.command = Global.DISCONNECT
        elif sub_action == "R":
            direction = Global.FORWARD
            dirr = sub_action_part[1]
            if Utility.is_number(dirr):
                dirr = int(dirr)
            if dirr == WithrottleConst.REVERSE:
                direction = Global.REVERSE
            rett.sub_command = Global.DIRECTION
            rett.direction = direction
        elif sub_action == "S":
            # ignore short address, not documented
            pass
        elif sub_action == "s":
            # set speed set step mode
            mode = sub_action_part[1]
            rett.sub_command = Global.STEP
            rett.mode = mode
        elif sub_action == "V":
            speed = sub_action_part[1:].strip()
            if Utility.is_number(speed):
                speed = int(speed)
            rett.sub_command = Global.SPEED
            rett.speed = speed
        elif sub_action == "X":
            # estop
            rett.sub_command = Global.SPEED
            rett.speed = -1
        return rett

    def __parse_loco_address(self, loco_id):
        """ parse loco address in form of 1234(L) into dcc id and address_type, (1234, L) """
        upper_loco = loco_id.strip().upper()
        address_type = "L"
        loco_str = loco_id
        loco_num = -1
        if upper_loco.startswith("S"):
            address_type = "S"
            loco_str = loco_id[1:]
        elif upper_loco.startswith("L"):
            address_type = "L"
            loco_str = loco_id[1:]
        elif upper_loco.endswith("(S)"):
            address_type = "S"
            loco_str = loco_id[0:-3]
        elif upper_loco.endswith("(L)"):
            address_type = "L"
            loco_str = loco_id[0:-3]
        # print(">>> ... "+str(loco_str))
        if Utility.is_number(loco_str):
            loco_num = int(loco_str)
        # print(">>> convert: "+str(loco_id) + " > " + str(loco_str), " > "+str(loco_num))
        return (loco_num, address_type)
