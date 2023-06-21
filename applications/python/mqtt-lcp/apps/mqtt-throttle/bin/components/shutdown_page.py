#!/usr/bin/python3
# Shutdown_page.py

"""

ShutdownPage - Shutdown page screen

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


# import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# from ttkbootstrap.dialogs.dialogs import Messagebox

sys.path.append('../../lib')

from utils.global_constants import Global
from structs.gui_message import GuiMessage
from structs.gui_message import  GuiMessageEnvelope
from components.local_constants import Local

# from image_button import ImageButton



class ShutdownPage(ttk.Frame):
    """ control panel page """

    def __init__(self, parent, parent_node, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_node = parent_node
        self.power = "???"
        self.frame = ttk.Frame(self, width=240, height=240)
        self.frame.grid(row=0,column=0,sticky="N")
        self.frame.grid_propagate(0)
        #self.frame.update()
        self.text1 = ttk.Label(self.frame,text=Local.MSG_SHUTDOWN_1,font="Helvetica,16")
        self.text1.grid(column=0,row=0, padx=24, pady=12)
        self.text2 = ttk.Label(self.frame,text=Local.MSG_SHUTDOWN_2)
        self.text2.grid(column=0,row=1,padx=2, pady=2)
        self.button_frame = ttk.Frame(self.frame, width=200, height=48)
        self.on_button = ttk.Button(self.button_frame,
                    text=Local.SHUTDOWN.title(), state=NORMAL, width=12,
                    command=lambda: self.on_clicked(Local.SHUTDOWN))
        self.on_button.grid(row=0, column=0, padx=16, pady=6)

        self.button_frame.grid(row=3,column=0, padx=16, pady=24)
        self.button_frame.grid_propagate(0)

    def on_clicked(self, button_text):
        """ key clicked """
        # print("Clicked: "+str(button_text))
        if button_text == Local.SHUTDOWN:
            okk = messagebox.askokcancel(message=Local.MSG_SHUTDOWN_CONFIRM)
            # okk = Messagebox.okcancel(message=Local.MSG_SHUTDOWN_CONFIRM, parent=self)
            if okk is True:
                shutdown_message = GuiMessage()
                shutdown_message.command =  Global.POWER
                shutdown_message.sub_command = Global.SHUTDOWN
                self.parent_node.queue_tk_input( \
                    GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=shutdown_message))

    def process_output_message(self, message):
        """ process output message """
        pass

#cardBtn.state(["disabled"])   # Disable the button.
#cardBtn.state(["!disabled"])
