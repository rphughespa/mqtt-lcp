#!/usr/bin/python3
# command_loco.py
"""

    CommandLoco.py - Class representing a a single loco in a cab in a throttle in the mqtt-dcc-command

the MIT License (MIT)

Copyright © 2021 richard p hughes

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

sys.path.append('../lib')

from utils.global_constants import Global

# from structs.roster import LocoData


class CommandLoco():
    """ Class representing a loco in a cab in a throttle in the mqtt-dcc-command """
    def __init__(self, node_id, throttle_id, cab_id, dcc_id, roster):
        self.node_id = node_id
        self.throttle_id = throttle_id
        self.cab_id = cab_id
        self.dcc_id = dcc_id
        self.roster_loco = None
        self.request_message = None
        self.slot_id = -1
        self.apply_functions = True
        self.is_direction_normal = True  # loco is facing normally or is facing reversed in consist
        self.current_speed = 0  # current speed
        # current direction of travel, either FORWARD or REVERSE
        self.current_direction = Global.FORWARD
        self.function_states = {}
        for f in range(0, 29):
            self.function_states[f] = 0  # 0 = off, 1 = on
        self.__init_from_roster(roster)

    def __repr__(self):
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    @classmethod
    def parse_gui_message(cls, gui_message):
        """ generate a new CommandLoco from a GuiMessage"""
        rett = CommandLoco(\
            gui_message.node_id, \
            gui_message.throttle_id, \
            gui_message.cab_id, \
            gui_message.dcc_id,
            None)
        if gui_message.direction == Global.REVERSE:
            # loco is facing backward
            rett.is_direction_normal = False
        return rett

    def get_corrected_direction(self):
        """ corect curent direction by applying is direction reversed """
        rett = self.current_direction
        if not self.is_direction_normal:
            if self.current_direction == Global.FORWARD:
                rett = Global.REVERSE
            else:
                rett = Global.FORWARD
        return rett

    def set_function(self, func, new_state):
        """ set all loco function  to a new state """
        if new_state in [Global.ON, Global.OFF]:
            if func in range(0, 29):
                if new_state == Global.ON:
                    self.function_states[func] = 1
                else:
                    self.function_states[func] = 0

    def set_speed(self, new_speed):
        """ set speed of loco """
        if new_speed in range(-1, 127):
            self.current_speed = new_speed

    def set_direction(self, new_direction):
        """ set direction of loco """
        if new_direction in [Global.FORWARD, Global.REVERSE]:
            if self.is_direction_normal:
                self.current_direction = new_direction
            else:
                if new_direction == Global.REVERSE:
                    self.current_direction = Global.FORWARD
                else:
                    self.current_direction = Global.REVERSE

    #
    # private functions
    #

    def __init_from_roster(self, roster):
        self.roster_loco = None
        if roster is not None:
            roster_loco = roster.locos.get(self.dcc_id, None)
            if roster_loco is not None:
                self.roster_loco = roster_loco
