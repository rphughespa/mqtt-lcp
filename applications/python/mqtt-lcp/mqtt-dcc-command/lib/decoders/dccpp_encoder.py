#!/usr/bin/python3
# dccp_encoder.py
"""


   DccppEncoder.py - Encode serial messages for DCC++ command station

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

sys.path.append('../../lib')

# from structs.gui_message import GuiMessage

from utils.global_constants import Global
from utils.global_synonyms import Synonyms


class DccppEncoder(object):
    """ Encode DCC++ serial commands """
    def __init__(self):
        pass

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def encode_message(self, message, _source):
        """ encode a message into dcc++ protocol """
        rett = message
        # print(">>> encode: " + str(message))
        if not isinstance(message, str):
            if message.command == Global.STATUS:
                rett = self.encode_status_request(message)
            elif message.command == Global.POWER:
                rett = self.encode_power_request(message)
            elif message.command == Global.THROTTLE:
                if message.sub_command == Global.FUNCTION:
                    rett = self.encode_function_request(message)
                else:
                    rett = self.encode_throttle_request(message)
            elif message.command == Global.SWITCH:
                rett = self.encode_switch_request(message)
        if not isinstance(rett, str) :
            print("!!! decode error: " + str(rett))
        return rett

    def encode_status_request(self, _message):
        """ encode a request for command station status """
        rett = "<s>"
        return rett

    def encode_power_request(self, message):
        """ encode a power request message """
        rett = "<0>"
        power_mode = message.mode
        if Synonyms.is_synonym_activate(power_mode):
            # turn on
            rett = "<1>"
        elif power_mode == Global.REPORT:
            rett = "<s>"
        return rett

    def encode_throttle_request(self, message):
        """ encode a throttle request message"""
        slot = message.slot_id
        dcc_id = message.dcc_id
        speed = message.speed
        direction = message.direction
        loco_dir = 1
        if direction == Global.REVERSE:
            loco_dir = 0
        rett = "<t " + str(slot) + " " + str(dcc_id) + " " + \
                str(speed) + " " + str(loco_dir) + ">"
        #print(">>> throttle: " + str(rett))
        return rett

    def encode_function_request(self, message):
        """ encode a loco function request message """
        _slot = message.slot_id
        dcc_id = message.dcc_id
        changed_function = message.function
        # functions_list_globals = message.items
        functions_list = message.items  # assumes func dict conrain 0,1 as off, on

        rett = ""
        func_byte1 = -1
        func_byte2 = -1
        if changed_function in range(0, 5):  # f0-f4
            func_byte1 = 128
            func_byte1 += functions_list[0] * 16
            func_byte1 += functions_list[1] * 1
            func_byte1 += functions_list[2] * 2
            func_byte1 += functions_list[3] * 4
            func_byte1 += functions_list[4] * 8
        elif changed_function in range(5, 9):  # f5-f8
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
        elif changed_function in range(13, 21):  # f13-f20
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
        elif changed_function in range(21, 29):  # f21-f28
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
            # command = self.__generate_function_command(slot, dcc_id, func_byte1, func_byte2)
            rett = "<f " + str(dcc_id) + " " + str(func_byte1)
            if func_byte2 != -1:
                rett = rett + ", " + str(func_byte2)
            rett = rett + ">"
        # print(">>> func code: " + str(rett))
        return rett

    def encode_switch_request(self, message):
        """ encode a switch request message """
        address = message.port_id
        sub_address = message.sub_address
        switch_mode = message.mode
        mode = "0"
        if Synonyms.is_synonym_activate(switch_mode):
            # turn on
            mode = "1"
        rett = "<a " + str(address) + " " + str(sub_address) + " " + str(
            mode) + ">"
        return rett

    #
    # private functions
    #

#    def __convert_functions_to_int(self, functions_list_globals):
#        rett = []
#        for func in functions_list_globals:
#            if func == Global.ON:
#                rett.append(1)
#            else:
#                rett.append(0)
#        return rett
