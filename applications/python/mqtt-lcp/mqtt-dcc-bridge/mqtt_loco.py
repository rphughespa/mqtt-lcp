# mqtt_loco.py

"""

    mqtt_loco.py - Class representing a a single loco in a cab in a throttle on the mqtt network

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
from local_constants import Local

class MqttLoco():
    """ Class representing a loco in a cab in a throttle on the mqtt network """

    def __init__(self):
        self.loco_id = None
        self.dcc_id = None
        self.slot = -1
        self.is_direction_normal = True   # in consist loco is facing the opposite direction of lead loco
        self.apply_functions = True
        self.speed = 0                      # current speed
        self.direction_is_reversed = False  # current direction of travel
        self.functions = []

    def initialize_loco(self, loco_dict):
        """ parse a dictionary of parameters """
        # {dcc_id: "1234", name: "prr gg1 green 1234", direction:"reverse", function:"true"}
        self.initialize_functions()
        reported = Global.ERROR
        message = ""
        if Global.DCC_ID in loco_dict:
            self.dcc_id = loco_dict[Global.DCC_ID]
        if Global.NAME in loco_dict:
            self.loco_id = loco_dict[Global.NAME]
        if Global.DIRECTION in loco_dict:
            direction = loco_dict[Global.DIRECTION]
            if direction == Global.REVERSE:
                self.is_direction_normal = False
        if Global.FUNCTIONS in loco_dict:
            functions = loco_dict[Global.FUNCTIONS]
            if functions == Global.FALSE:
                self.apply_functions = False
        if self.loco_id is None:
            if self.dcc_id is not None:
                self.loco_id = self.dcc_id
        if self.dcc_id is not None:
            reported = "ok"
        else:
            message = Local.MSG_ERROR_NO_DCC_ID + str(loco_dict)
        return reported, message

    def initialize_functions(self):
        """ initial function to off """
        self.functions = []
        for _func in  range(0, 29):       # functons 0..28
            self.functions.append(0)      # 0 = off, 1 = on

    def release_loco(self, _parent_cab, parent_node):
        """ release a loco """
        parent_node.dcc_clear_a_slot(self.slot)
