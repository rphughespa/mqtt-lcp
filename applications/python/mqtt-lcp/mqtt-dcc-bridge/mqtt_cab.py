# mqtt_cab.py

"""

    mqtt_cab.py - Class representing a cab of one or more locos in a throttle on the mqtt network

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

from mqtt_loco import MqttLoco


class MqttCab():
    """ Class representing a cab in a throttle on the mqtt network """

    def __init__(self, port_id):
        self.port_id = port_id
        self.locos_by_id = {}
        self.locos_by_seq = []
        self.consist = None

    def initialize_cab(self):
        """ initilaize a cab """
        reported = Global.ERROR
        message = ""
        if self.consist is None:
            self.consist = []
            self.consist.append({Global.DCC_ID: self.port_id, Global.NAME: "",
                    Global.DIRECTION: Global.FORWARD,
                    Global.FUNCTIONS:Global.TRUE})
        for loco in self.consist:
            new_loco = MqttLoco()
            reported, message = new_loco.initialize_loco(loco)
            if reported == Global.ERROR:
                break
            self.locos_by_id[new_loco.dcc_id] = new_loco
            self.locos_by_seq.append(new_loco)
        return reported, message

    def release_cab(self, parent_node):
        """ release a cab """
        for loco in self.locos_by_seq:
            loco.release_loco(self, parent_node)
        self.locos_by_id = {}
        self.locos_by_seq = []
        return "OK", None
