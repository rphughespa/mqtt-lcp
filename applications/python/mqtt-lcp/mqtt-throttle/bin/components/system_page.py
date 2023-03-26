#! /usr/bin/python3
# system_page.py

"""

SystemPage - Track power page screen

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
from tkinter import *
from tkinter import messagebox
# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
# from tkinter import messagebox


sys.path.append('../../lib')

from structs.gui_message  import GuiMessage
from utils.global_constants import Global
from components.tk_message import  TkMessage
from components.local_constants import Local

# from image_button import ImageButton

class SystemPage(ttk.Frame):
    """ control misc layout features """

    def __init__(self, parent, parent_node, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)

        self.track_power =  False
        self.parent = parent
        self.parent_node = parent_node

        self.frame = ttk.Frame(self, width=720, height=250, padding=(2,2,2,2))
        self.frame.grid(row=0,column=0,sticky="N")
        self.frame.grid_propagate(0)

        self.power_frame = ttk.LabelFrame(self.frame, width=220, height=60, \
                text=Local.POWER.title(), relief="raised")
        self.power_frame.grid(row=0,column=0,padx=12,sticky="N")
        self.power_frame.grid_propagate(0)

        self.TrackPower = IntVar()

        self.track_power_checkbutton =  ttk.Checkbutton(self.power_frame,
                bootstyle="success-round-toggle",
                width=22, # padx=1,
                text=Local.TRACK_POWER.title(),
                variable=self.TrackPower,
                onvalue=1, offvalue=0,
                state="normal",
                command=self.on_track_power_changed)
        self.track_power_checkbutton.grid(row=0, column=0, padx=12, pady=12)

        self.power_frame.grid(row=0, column=0)


        self.shutdown_frame = ttk.LabelFrame(self.frame, width=200, height=220, \
                text=Local.SHUTDOWN.title(), relief="raised")
        self.shutdown_frame.grid_propagate(0)

        self.shutdown_button = ttk.Button(self.shutdown_frame,
                    bootstyle="outline-danger",
                    text=Local.SHUTDOWN.title(), state=NORMAL, width=12,
                    command=self.on_shutdown_clicked)
        self.shutdown_button.grid(column=0,row=0,padx=2, pady=2)

        self.text1 = ttk.Label(self.shutdown_frame,text=Local.MSG_SHUTDOWN_1, \
                justify="center", font="Helvetica,16")
        self.text1.grid(column=0,row=1, padx=4, pady=12)

        self.text2 = ttk.Label(self.shutdown_frame,text=Local.MSG_SHUTDOWN_2, justify="center")
        self.text2.grid(column=0,row=2,padx=4, pady=2)

        self.shutdown_frame.grid(row=0, column=1, rowspan=2,stick=(NE))

        self.frame.grid(row=0, column=0, rowspan=2, sticky=(NW))


    def on_track_power_changed(self):
        """ track power change requested  """
        power = self.TrackPower.get()
        power_message = GuiMessage()
        power_message.command =  Global.SWITCH
        power_message.port_id = Global.POWER
        if power == 1:
            power_message.mode = Global.ON
        else:
            power_message.mode = Global.OFF
        self.parent_node.queue_tk_input( \
            TkMessage(msg_type=Global.PUBLISH, msg_data=power_message))

    def on_shutdown_clicked(self):
        """ shutdown key clicked """
        okk = messagebox.askokcancel(message=Local.MSG_SHUTDOWN_CONFIRM)
        if okk is True:
            shutdown_message = GuiMessage()
            shutdown_message.command =  Global.NODE
            shutdown_message.mode = Global.SHUTDOWN
            self.parent_node.queue_tk_input( \
                TkMessage(msg_type=Global.PUBLISH, msg_data=shutdown_message))

    def process_output_message(self, message):
        """ process output message """
        if message.msg_type == Global.POWER:
            if message.msg_data.command == Global.SWITCH and \
                    message.msg_data.port_id == Global.POWER:
                if message.msg_data.mode == Global.ON:
                    self.TrackPower.set(1)
                else:
                    self.TrackPower.set(0)

        if message.msg_type == Global.POWER:
            if message.msg_data.mode == Global.ON:
                self.track_power = True
            else:
                self.track_power = False
