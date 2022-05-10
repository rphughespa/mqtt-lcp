#!/usr/bin/python3
# dccp_decoder.py
"""


   DccppDecoder.py -Decode serial messages from DCC++ command station

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

sys.path.append('../../lib')

from structs.throttle_message import ThrottleMessage

from utils.global_constants import Global
# from utils.global_synonyms import Synonyms


class DccppDecoder(object):
    """ Decode/Encode DCC++ serial commands """
    def __init__(self):
        pass

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def decode_message(self, serial_string, _source):
        """ decode a serial nessage from dcc++ command station """
        rett = ThrottleMessage()
        rett.command = Global.UNKNOWN
        rett.text = serial_string
        #print(">>> decode: : " + str(serial_string))
        if serial_string is not None:
            cmd = serial_string.strip()
            #print(">>> debug 1: " + str(cmd))
            if cmd.startswith("<") and cmd.endswith(">"):
                cmd = cmd[1:-1]
                #print(">>> debug 2: " + str(cmd))
                key = cmd[0].lower()
                #print(">>> debug 3: " + str(key))
                if key == "p":
                    rett = self.decode_power(rett, serial_string, cmd)
                elif key == "t":
                    rett = self.decode_throttle(rett, serial_string, cmd)

        return rett

    def decode_power(self, def_rett, serial_string, cmd):
        """ decode a power response  """
        rett = def_rett
        if cmd[1] == "0":
            rett.command = Global.POWER
            rett.mode = Global.OFF
        elif cmd[1] == "1":
            rett.command = Global.POWER
            rett.mode = Global.ON
        else:
            rett.command = Global.POWER
            rett.mode = Global.UNKNOWN
            rett.text = serial_string
        return rett

    def decode_throttle(self, def_rett, _serial_string, cmd):
        """ decode a throttle response """
        rett = def_rett
        command_parts = cmd.split(" ")
        if len(command_parts) > 3:
            loco_dir = Global.REVERSE
            if command_parts[3] == "1":
                loco_dir = Global.FORWARD
            rett.command = Global.THROTTLE
            rett.slot_id = cmd[1]
            rett.value = cmd[2]
            rett.direction = loco_dir
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
