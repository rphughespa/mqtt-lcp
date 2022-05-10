#!/usr/bin/python3
# locos_keypad_page.py

"""

LocosKeypadPage - Locos Keypad screen

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
# import json
import sys

# import tkinter as tk
from tkinter import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../../lib')

from utils.global_constants import Global
from structs.throttle_message import ThrottleMessage
from components.local_constants import Local
from components.key_pad import KeyPadFrame
# from components.tk_message import TkMessage
from components.image_button import ImageButton

class LocosKeypadPage(ttk.Frame):
    """ Locos Screen """

    def __init__(self, parent, parent_node, parent_cab, **kwargs):
        """ Initialize """
        super().__init__(parent, **kwargs)
        self.grid_propagate(0)
        self.parent = parent
        self.parent_node = parent_node
        self.parent_cab = parent_cab
        self.loco_id = ""
        self.loco_desc = ""

        self.top_frame=ttk.Frame(self, width=340, height=112, padding=(2,2,2,2))
        #self.top_frame.configure(style="InfoBox.TFrame")
        self.padding=(2,2,2,2)
        self.top_frame.grid_propagate(0)

        self.loco_frame=ttk.Frame(self.top_frame, relief="raised", width=236,  height=106, \
                padding=(4,2,4,2))

        self.loco_frame.grid_propagate(False)

        self.id_label = ttk.Label(self.loco_frame, text=self.loco_id, \
                font=("Helvetica", 32), width=5,
                relief="raised", anchor=E)
        self.id_label.grid(row=0, column=0, padx=6, pady=4, sticky=(NW))

        self.LocoIsReversed = IntVar(self)

        self.loco_is_reversed_checkbox = ttk.Checkbutton(self.loco_frame,
                bootstyle="success-round-toggle",
                width=22,
                text=Local.IS_REVERSED.title(),
                variable=self.LocoIsReversed,
                onvalue=1, offvalue=0,
                command=self.on_loco_is_reversed)

        self.loco_is_reversed_checkbox.grid(row=1, column=0,padx=4, sticky=(SW))
        self.loco_is_reversed_checkbox.configure(state='disabled')

        self.loco_frame.grid(row=0, column=0,sticky=(E))

        self.button_frame = ttk.Frame(self.top_frame, relief="raised",
                height=106, width=98, padding=(2,2,2,2))

        #self.button_frame.configure(style="InfoBox.TFrame")
        self.button_frame.grid_propagate(0)

        self.acquire_button = ImageButton(self.button_frame, width=96, height=32, \
                        text=' '+Local.ACQUIRE.title(),
                        compound=LEFT, image_file="img/buttons/plus.png", \
                        image_width=26, image_height=26,
                        command=self.on_acquire_clicked)
        self.acquire_button.set_disabled()
        self.acquire_button.grid(row=0, column=0, sticky=(NE))

        self.button_frame.grid(row=0, column=1, padx=2, sticky=(NE))

        self.top_frame.grid(row=0, column=0, sticky=(NW))

        self.key_frame = ttk.Frame(self, padding=(2,2,2,2))
        self.keypad = KeyPadFrame(self.key_frame, callback=self.on_keypad_clicked)
        # self.keypad.grid(row=2, column=0)
        self.keypad.grid(row=0, column=0, pady=4)

        self.key_frame.grid(row=1, column=0, sticky=(S))

    def on_keypad_clicked(self, key_number):
        """ keypad has been clicked """
        # print("Clicked: "+str(key_number))

        if self.loco_desc != "":
            self.loco_desc = ""
            # self.desc_label.config(text="")

        if key_number.isdigit():
            if len(self.loco_id) < 5:
                self.loco_id += str(key_number)
        elif key_number == "CLR":
            self.loco_id = ""
        elif key_number == "<==":  # back space
            if len(self.loco_id) > 0:
                self.loco_id = self.loco_id[:-1]
        if self.loco_id == "0":
            self.loco_id = ""
        self.__populate_top_frame()

    def on_loco_is_reversed(self):
        """ is reversed changed """
        loco_reversed = self.LocoIsReversed.get()
        print("Loc Reversed changed: " + str(loco_reversed))

    def on_acquire_clicked(self, _state):
        """ selection clicked """
        #print("Acquire Loco: " + str(self.loco_id))
        dcc_id = int(self.loco_id)
        self.parent_cab.publish_acquire_request(dcc_id)
        self.parent_cab.locos_selected_list.append(int(dcc_id))
        loco = self.parent_cab.locos_roster_map.get(dcc_id, None)
        if loco is None:
            # using a loco not in roster, add a temp entry
            loco = ThrottleMessage()
            loco.dcc_id = dcc_id
            # mark is as a loco added from keypad
            loco.reported = Global.KEYPAD
            self.parent_cab.locos_roster_map[loco.dcc_id] = loco
            # print(">>> roster: " + str(self.parent_cab.locos_roster_map))
        loco.mode = Local.SELECTED
        if self.LocoIsReversed.get() == 1:
            loco.direction = Global.REVERSE
        else:
            loco.direction = Global.FORWARD
        self.loco_id = ""
        self.LocoIsReversed.set(0)
        self.parent_cab.refresh_all_pages()

    def refresh_page(self):
        """ refresh the display page """
        self.parent_cab.build_display_lists()
        if self.loco_id > "":
            self.__populate_top_frame()
        else:
            self.__clear_top_frame()
        pass

    def process_output_message(self, message):
        """ process output message"""
        pass

    #
    # private functions
    #

    def __populate_top_frame(self):
        """ populate top frame """
        self.acquire_button.set_normal()
        self.loco_is_reversed_checkbox.configure(state='normal')
        self.id_label.config(text=self.loco_id)

    def __clear_top_frame(self):
        """ clear top frame """

        self.loco_id = ""
        self.LocoIsReversed.set(0)
        self.loco_is_reversed_checkbox.configure(state='disabled')
        self.id_label.config(text=self.loco_id)
