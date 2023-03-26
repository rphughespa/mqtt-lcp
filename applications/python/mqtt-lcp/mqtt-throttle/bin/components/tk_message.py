# tk_message.py

"""

    tk_message.py - helper class for messages to tk screens

The MIT License (MIT)

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

sys.path.append('../../lib')

from utils.global_constants import Global
from components.local_constants import Local

class TkMessage(object):
    """ Class for a item in the state collection"""

    def __init__(self, msg_type=Global.TOWER, data_type="", msg_data=None, cab=Local.CAB_ALL):
        self.msg_type = msg_type  # Global.TOWER, Local.THROTTLE, Local.SENSOR
        self.data_type = data_type
        self.cab = cab  # Local.CAB_ALL, Local.CAB_A, Local.CAB_B
        self.msg_data = msg_data

    def __repr__(self):
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"
