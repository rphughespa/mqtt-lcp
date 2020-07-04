# node_base_dccpp.py - base class for dcc++ nodes
"""


 node_base_dccpp - base class for nodes that interact with dcc++ command stations

the MIT License (MIT)

Copyright © 2020 richard p hughes

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

from global_constants import Global

from node_base_serial import NodeBaseSerial


class NodeBaseDccpp(NodeBaseSerial):
    """
        Base class for node programs that interact with dcc++ command stations.
        Manages runs on main thread
    """

    def __init__(self):
        super().__init__()
        self.slots = []          # dcc++ calls slots "registers"
        self.slot_count = -1
        self.dcc_power_status = "unknown"

    def initialize_threads(self):
        """ initialize all IO threads"""
        # load config file
        super().initialize_threads()
        self.dcc_initialize_slots()

    def shutdown_theads(self):
        """ shutdown all IO threads"""
        super().shutdown_threads()

    # Register (slot) management

    def dcc_initialize_slots(self):
        """ initialize the register slots """
        self.slot_count = 12  # use dcc++ default
        if Global.OPTIONS in self.config[Global.CONFIG]:
            if Global.SLOTS in self.config[Global.CONFIG][Global.OPTIONS]:
                self.slot_count = self.ping_interval = self.config[Global.CONFIG][Global.OPTIONS][Global.SLOTS]
        self.log_queue.add_message("info", "dcc++ slots: "+str(self.slot_count))
        for _slot in range(0, self.slot_count+1):   # slot 0 is for programming, don't use it
            self.slots.append(-1)

    def dcc_get_slots_available(self):
        """ return count of unasigned register slots """
        available = 0
        for reg_index in range(1, self.slot_count+1):
            if self.slots[reg_index] == -1:
                available += 1
        return available

    def dcc_assign_loco_to_slot(self, dcc_id):
        """ asssign a register slot o a loco """
        slot = -1
        first_avail = -1
        for reg_index in range(1, self.slot_count+1):
            if ((self.slots[reg_index] == -1) and
                    (first_avail == -1)):
                first_avail = reg_index
            if self.slots[reg_index] == dcc_id:  # dcc_id already has a slot
                slot = reg_index
                break
        if ((slot == -1) and (first_avail != -1)):
            slot = first_avail
        if slot != -1:
            self.slots[slot] = dcc_id
        return slot

    def dcc_clear_a_slot(self, slot):
        """ clear out a register slot, make it available for reuse"""
        # clear an individual regsietr slot
        # if ((slot >= 0) and (slot <= self.slot_count)):
        if 0 <= slot <= self.slot_count:
            self.slots[slot] = -1

    # serial io

    def send_serial_message(self, message):
        """ send message to serial port """
        self.log_queue.add_message("info", Global.MSG_SEND_SERIAL+" {"+ message +"}")
        self.send_to_serial(message)

    def send_serial_immediate(self, message):
        """ send serial message and wait for a reply """
        self.log_queue.add_message("info", Global.MSG_SEND_SERIAL_WAIT + " {"+ message +"}")
        return self.send_to_serial_and_wait(message)

    def received_from_serial(self, serial_input):
        """ process serial input"""
        self.log_queue.add_message("info", Global.MSG_SERIAL_RECEIVED +" {"+ serial_input+"}")

    # commands

    def __generate_power_command(self, new_power_mode):
        """ dcc++ power command """
        command = None
        if new_power_mode == Global.ON:
            command = "<1>"
        elif new_power_mode == Global.OFF:
            command = "<0>"
        return command

    def __generate_speed_command(self, slot, dcc_id, speed, direction):
        """ dcc++ power command """
        command = "<t "+ str(slot)+" "+dcc_id+" "+str(speed)+" "+str(direction)+">"
        return command

    def __generate_function_command(self, _slot, dcc_id, func_byte1, func_byte2):
        """ dcc++ power command """
        command = "<f "+ dcc_id+" "+str(func_byte1)
        if func_byte2 != -1:
            command = command + ", "+str(func_byte2)
        command = command + ">"
        return command

    def __parse_power_response(self, power_mode):
        """ dcc++ power command """
        response = Global.UNKNOWN
        if power_mode == "<p0>":
            response = Global.OFF
        elif power_mode == "<p1>":
            response = Global.ON
        return response

    def __generate_accessory_command(self, dcc_id, sub_address, action):
        """ dcc++ accessory decoder command """
        command = "<a "+ str(dcc_id)+" "+str(sub_address)+" "+str(action)+" >"
        return command

    def __parse_speed_response(self, speed_response):
        """ dcc++ power command """
        reported = Global.ERROR
        message = ""
        if speed_response.startswith("<T"):
            reported = Global.OK
        else:
            message = speed_response
        return reported, message

    def dcc_set_track_power(self, setting):
        """ set track power, on / off """
        setting = setting.lower()
        response = Global.ERROR
        send_message = self.__generate_power_command(setting)
        if send_message is not None:
            response = self.send_serial_immediate(send_message)
        self.log_queue.add_message("debug", Global.TRACK + " " +
                Global.POWER +' '+Global.RESPONSE + " {"+ str(response) +"}")
        self.dcc_power_status = self.__parse_power_response(response['text'])

    def dcc_get_track_status(self):
        """ get status of dcc++ comamnd station """
        send_message = "<s>"
        self.log_queue.add_message("debug", Global.DCC + " " +
                Global.STATUS + " " + Global.REQUEST +" : {"+ send_message +"}")
        response = self.send_serial_immediate(send_message)  # send status request, get back first response
        self.dcc_power_status = self.__parse_power_response(response['text'])
        self.log_queue.add_message("debug", Global.DCC + " " +
                Global.STATUS + " " + Global.RESPONSE + " : {"+ str(response) +"}")

    def dcc_emergency_stop(self, slot, dcc_id):
        """ execute emergency stop for a loco """
        return self.dcc_set_loco_speed(slot, dcc_id, -1, False)

    def dcc_set_loco_speed(self, slot, dcc_id, speed, direction_is_reversed):
        """ execute emergency stop for a loco """
        direction = 1  # forward
        if direction_is_reversed:
            direction = 0 # reversed
        command = self.__generate_speed_command(slot, dcc_id, speed, direction)
        response = self.send_serial_immediate(command)
        self.log_queue.add_message("debug", Global.TRACK + " " +
                Global.SPEED +' '+Global.RESPONSE + " {"+ str(response['text']) +"}")
        reported, message = self.__parse_speed_response(response['text'])
        return reported, message

    def dcc_set_loco_functions(self, slot, dcc_id, changed_function, functions_list):
        """ set a loco function """
        reported = "error"
        message = ""
        func_byte1 = -1
        func_byte2 = -1
        if changed_function in range(0, 5):     # f0-f4
            func_byte1 = 128
            func_byte1 += functions_list[0] * 16
            func_byte1 += functions_list[1] * 1
            func_byte1 += functions_list[2] * 2
            func_byte1 += functions_list[3] * 4
            func_byte1 += functions_list[4] * 8
        elif changed_function in range(5, 9):   # f5-f8
            func_byte1 = 176
            func_byte1 += functions_list[5] * 1
            func_byte1 += functions_list[6] * 2
            func_byte1 += functions_list[7] * 4
            func_byte1 += functions_list[8] * 8
        elif changed_function in range(9, 13):  # f9-f12
            func_byte1 = 160
            func_byte1 += functions_list[9] * 1
            func_byte1 += functions_list[10] * 2
            func_byte1 += functions_list[11] * 4
            func_byte1 += functions_list[12] * 8
        elif changed_function in range(13, 21): # f13-f20
            func_byte1 = 222
            func_byte2 = 0
            func_byte2 += functions_list[13] * 1
            func_byte2 += functions_list[14] * 2
            func_byte2 += functions_list[15] * 4
            func_byte2 += functions_list[16] * 8
            func_byte2 += functions_list[17] * 16
            func_byte2 += functions_list[18] * 32
            func_byte2 += functions_list[19] * 64
            func_byte2 += functions_list[20] * 128
        elif changed_function in range(21, 29): # f21-f28
            func_byte1 = 223
            func_byte2 = 0
            func_byte2 += functions_list[21] * 1
            func_byte2 += functions_list[22] * 2
            func_byte2 += functions_list[23] * 4
            func_byte2 += functions_list[24] * 8
            func_byte2 += functions_list[25] * 16
            func_byte2 += functions_list[26] * 32
            func_byte2 += functions_list[27] * 64
            func_byte2 += functions_list[28] * 128
        if func_byte1 != -1:
            command = self.__generate_function_command(slot, dcc_id, func_byte1, func_byte2)
            self.send_serial_message(command)
            self.log_queue.add_message("debug", Global.TRACK + " " +
                Global.FUNCTION +" {"+command+"}")
            reported = Global.OK
        return reported, message

    def dcc_set_dcc_decoder(self, address, sub_address, action):
        """ set a dcc decoder """
        reported = "error"
        message = ""
        sub_addr = sub_address
        if sub_addr is None:
            sub_addr = 0
        command = self.__generate_accessory_command(address, sub_addr, action)
        self.send_serial_message(command)
        self.log_queue.add_message("info", Global.TRACK + " " +
            Global.SWITCH +" {"+command+"}")
        reported = Global.OK
        return reported, message
