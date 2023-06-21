#!/usr/bin/python3
# message_frame.py

"""

MessageFrame - Message Frame screen

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
from datetime import datetime

# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../../lib')

from utils.global_constants import Global

class MessageFrame(ttk.Frame):
    """ message frame """

    def __init__(self, parent, parent_node, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_node = parent_node
        self.message_label = ttk.Label(self, text="Message", width=72, style="My.TLabel")
        self.message_label.grid(row=0, column=0)
        self.local_label = ttk.Label(self, text="Local: 0:00", width=12, style="My.TLabel")
        self.local_label.grid(row=0, column=1)
        self.fast_label = ttk.Label(self, text="Fast: 0:00", width=12, style="My.TLabel")
        self.fast_label.grid(row=0, column=2)

    def process_output_message(self, message):
        """ process output message """
        if message.msg_type == Global.MESSAGE:
            self.message_label.configure(text=message.msg_data)
        elif message.msg_type == Global.FASTCLOCK:
            _fast_time_string = "00:00"
            # print(">>> fastclock: " + str(message.msg_data))
            date_time = message.msg_data.get(Global.DATETIME, "0T00:00")
            # datetime is iso datetime YYYYYY-MM-DDTHH:SS:ms
            date_time_object = datetime.fromisoformat(date_time)
            hour = str(date_time_object.hour)
            mins = str(date_time_object.minute)
            if len(mins) < 2:
                mins = "0"+mins
            hhmm = hour+":"+mins
            self.fast_label.configure(text="Fast: " +hhmm)
        elif message.msg_type == Global.TIME:
            date_time = message.msg_data.get(Global.DATETIME, "0T00:00")
            # datetime is iso datetime YYYYYY-MM-DDTHH:SS:ms
            date_time_object = datetime.fromisoformat(date_time)
            hour = str(date_time_object.hour)
            mins = str(date_time_object.minute)
            if len(mins) < 2:
                mins = "0"+mins
            hhmm = hour+":"+mins
            self.local_label.configure(text="Local: "+hhmm)
