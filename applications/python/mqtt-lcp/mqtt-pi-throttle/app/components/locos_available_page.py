#!/usr/bin/python3
# locos_available_page.py

"""

LocosAvailablePage - Locos available, not selected for consist screen

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
import sys
# import json


# import tkinter as tk
from tkinter import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../../lib')

from utils.global_constants import Global
from components.local_constants import Local

# from components.tk_message import TkMessage
from components.locos_info_list import LocosInfoList
# from select_list_data import SelectListData
# from key_pad import KeyPadFrame
from components.image_button import ImageButton
from components.image_clickable import ImageClickable


class LocosAvailablePage(ttk.Frame):
    """ Locos Screen """

    def __init__(self, parent, parent_node, parent_cab, **kwargs):
        """ Initialize """
        super().__init__(parent, **kwargs)
        self.grid_propagate(0)
        self.parent = parent
        self.parent_node = parent_node
        self.parent_cab = parent_cab
        self.loco_name = ""
        self.loco_id = 0
        self.loco_desc = ""
        self.loco_image = None
        self.loco_is_reversed = False
        self.loco_blank_image = ImageClickable.load_image("img/locos/blank.png")

        self.LocoIsReversed = ttk.IntVar(self)

        self.top_frame=ttk.Frame(self, width=340, height=122, padding=(2,2,2,2))

        self.top_frame.grid_propagate(False)



        self.loco_frame=ttk.Frame(self.top_frame, relief="raised", width=236,  height=116, \
                padding=(4,2,4,2))
        self.loco_frame.grid_propagate(False)

        self.id_label = ttk.Label(self.loco_frame,
                text=self.loco_id,
                width=5, anchor='w')
        self.id_label.grid(row=0, column=0, padx=1)

        self.name_label = ttk.Label(self.loco_frame, text=self.loco_name, width=15, anchor='w')
        self.name_label.grid(row=0, column=1, padx=4)

        self.desc_label = ttk.Label(self.loco_frame, text=self.loco_desc, width=22, anchor='w')
        self.desc_label.grid(row=1, column=0, columnspan=2, padx=1, sticky=(W+E))

        self.loco_is_reversed_checkbox = ttk.Checkbutton(self.loco_frame,
                bootstyle="success-round-toggle",
                width=24, # padx=1,
                text=Local.IS_REVERSED.title(),
                variable=self.LocoIsReversed,
                onvalue=1, offvalue=0,
                command=self.on_loco_is_reversed)


        self.loco_is_reversed_checkbox.grid(row=2, column=0, columnspan=2)
        self.loco_is_reversed_checkbox.configure(state='disabled')

        self.image_label = ImageClickable(self.loco_frame, image=self.loco_image,
                height=Local.LOCO_IMAGE_HEIGHT,width=Local.LOCO_IMAGE_WIDTH)
        self.image_label.grid(row=3, column=0, columnspan=2, padx=1, pady=2, sticky=(W))

        self.loco_frame.grid(row=0, column=0, sticky=(NW))

        self.button_frame = ttk.Frame(self.top_frame, relief="raised",
                height=116, width=98, padding=(2,2,2,2))
        # self.button_frame.grid_propagate(False)

        self.acquire_button = ImageButton(self.button_frame, width=96, height=32, \
                        text=' '+Local.ACQUIRE.title(),
                        compound=LEFT, image_file="img/buttons/plus.png", \
                        image_width=26, image_height=26,
                        command=self.on_acquire_clicked)
        self.acquire_button.set_disabled()
        self.acquire_button.grid(row=0, column=0, sticky=(NE))

        self.button_frame.grid(row=0, column=1, padx=2, sticky=(NE))

        self.top_frame.grid(row=0, column=0, sticky=(NW))

        self.list_frame = ttk.Frame(self, padding=(2,2,2,2), relief="raised")
        #self.loco_list = SelectList(self.list_frame, [])
        self.loco_list = LocosInfoList(self.list_frame, None, \
                width=330, height=114, row_height=80,
                callback=self.on_list_item_clicked)
        self.loco_list.grid(row=0, column=0)

        self.list_frame.grid(row=1, column=0, sticky=(SE))


    def on_list_item_clicked(self, key):
        """ List item clicked """
        #print("Loco Clicked: "+ str(key))
        self.loco_id = key
        self.__populate_top_frame()

    def on_acquire_clicked(self, _state):
        """ selection clicked """
        #print("Acquire Loco: " + str(self.loco_id))
        if self.loco_id in self.parent_cab.locos_roster_map:
            self.parent_cab.locos_selected_list.append(self.loco_id)
            loco = self.parent_cab.locos_roster_map.get(self.loco_id, None)
            if loco is not None:
                self.parent_cab.publish_acquire_request(loco.dcc_id)
                loco.mode = Local.SELECTED
                if self.LocoIsReversed.get() == 1:
                    loco.direction = Global.REVERSE
                else:
                    loco.direction = Global.FORWARD
                #print(">>> loco dir: " + str(loco.direction))
                self.loco_id = 0
                self.parent_cab.refresh_all_pages()

    def on_loco_is_reversed(self):
        """ is reversed changed """
        loco_reversed = self.LocoIsReversed.get()
        print("Loc Reversed changed: " + str(loco_reversed))

    def process_output_message(self, message):
        """ process output message """
        if message.msg_type in [Global.ROSTER, Global.REFRESH]:
            self.__rebuild_available_list()

    def refresh_page(self):
        """ refresh the display page """
        self.__rebuild_available_list()
        if self.loco_id > 0:
            self.__populate_top_frame()
        else:
            self.__clear_top_frame()
        pass
    #
    # private functions
    #
    def __populate_top_frame(self):
        """ populate top frame """
        self.acquire_button.set_normal()
        self.loco_id = self.parent_cab.locos_roster_map[self.loco_id].dcc_id
        self.loco_name = self.parent_cab.locos_roster_map[self.loco_id].name
        self.loco_desc = self.parent_cab.locos_roster_map[self.loco_id].text
        self.loco_image = self.parent_cab.locos_roster_map[self.loco_id].image
        self.loco_is_reversed = False
        self.loco_is_reversed_checkbox.configure(state='normal')
        if self.loco_id > 0:
            self.id_label.config(text=str(self.loco_id))
        else:
            self.id_label.config(text="")
        self.name_label.config(text=self.loco_name)
        self.desc_label.config(text=self.loco_desc)
        if self.parent_cab.locos_roster_map[self.loco_id].image is not None:
            self.loco_image = self.parent_cab.locos_roster_map[self.loco_id].image
            self.image_label.replace_image(self.loco_image)

    def __clear_top_frame(self):
        """ clear top frame """
        self.acquire_button.set_disabled()
        self.LocoIsReversed.set(0)
        self.loco_is_reversed_checkbox.configure(state='disabled')
        self.loco_name = ""
        self.loco_id = 0
        self.loco_desc = ""
        self.loco_image = self.loco_blank_image
        if self.loco_id > 0:
            self.id_label.config(text=str(self.loco_id))
        else:
            self.id_label.config(text="")
        self.name_label.config(text=self.loco_name)
        self.desc_label.config(text=self.loco_desc)
        self.loco_image = self.loco_blank_image
        self.image_label.replace_image(self.loco_image)

    def __rebuild_available_list(self):
        """ build display list box """
        loco_available_map = {}
        for key in self.parent_cab.locos_available_list:
            loco_available_map[key] = self.parent_cab.locos_roster_map[key]
        self.loco_list.populate(loco_available_map)
