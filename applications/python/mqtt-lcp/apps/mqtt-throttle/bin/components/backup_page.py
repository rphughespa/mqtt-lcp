#!/usr/bin/python3
# backup_page.py

"""

BackupPage - Backup page screen

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
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import Messagebox


sys.path.append('../../lib')

# from utils.global_constants import Global
from structs.gui_message import  GuiMessageEnvelope
from components.local_constants import Local

# from image_button import ImageButton



class BackupPage(ttk.Frame):
    """ control panel page """

    def __init__(self, parent, parent_node, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_node = parent_node
        self.frame = ttk.Frame(self, width=240, height=240, style="InfoBox.TFrame")
        self.frame.grid(row=0,column=0,sticky="N")
        self.frame.grid_propagate(0)
        #self.frame.update()
        self.text = ttk.Label(self.frame,text=Local.MSG_BACKUP_1, style="Medium.TLabel")
        self.text.grid(column=0,row=0, padx=24, pady=12)
        self.text = ttk.Label(self.frame,text=Local.MSG_BACKUP_2, style="My.TLabel")
        self.text.grid(column=0,row=1,padx=2, pady=2)
        self.button_frame = ttk.Frame(self.frame, width=200, height=48, style="InfoBox.TFrame")
        self.on_button = ttk.Button(self.button_frame,
                    text=Local.BACKUP.title(), state=NORMAL, width=12,
                    command=lambda: self.on_clicked(Local.BACKUP))
        self.on_button.grid(row=0, column=0, padx=16, pady=6)
        self.on_button.configure(style="KeyButton.TButton")
        self.button_frame.grid(row=3,column=0, padx=16, pady=24)
        self.button_frame.grid_propagate(0)

    def on_clicked(self, button_text):
        """ key clicked """
        # print("Clicked: "+str(button_text))
        if button_text == Local.BACKUP:
            okk = Messagebox.okcancel(message=Local.MSG_BACKUP_CONFIRM)
            if okk is True:
                self.parent_node.queue_tk_input(GuiMessageEnvelope(msg_type=Local.TOWER, data_type=Local.BACKUP))

    def process_output_message(self, message):
        """ process output message """
        pass

#cardBtn.state(["disabled"])   # Disable the button.
#cardBtn.state(["!disabled"])
