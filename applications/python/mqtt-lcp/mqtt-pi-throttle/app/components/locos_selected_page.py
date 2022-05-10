#!/usr/bin/python3
# locos_selected_page.py

"""

LocosListPage - Locos Selected / Consist List screen

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
# from io import open_code
import sys
import copy


# import tkinter as tk
from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# from ttkbootstrap.dialogs.dialogs import Messagebox
# from pathlib import Path

sys.path.append('../../lib')

# from structs.roster import LocoData

from utils.global_constants import Global
from structs.throttle_message import ThrottleMessage
from components.local_constants import Local
from components.tk_message import TkMessage
from components.locos_info_list import LocosInfoList
from components.image_button import ImageButton
from components.image_clickable import ImageClickable
# from components.select_list_data import SelectListData

class LocosSelectedPage(ttk.Frame):
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
        self.loco_key = ""
        self.loco_desc = ""
        self.loco_image = None
        self.seq_number = 0
        self.loco_blank_image = ImageClickable.load_image("img/locos/blank.png")

        self.top_frame=ttk.Frame(self, width=340, height=122, padding=(2,2,2,2))

        self.top_frame.grid_propagate(False)

        self.loco_frame=ttk.Frame(self.top_frame, relief="raised", width=236,  height=116, \
                padding=(4,2,4,2))
        self.loco_frame.grid_propagate(False)

        self.id_label = ttk.Label(self.loco_frame,
                text="",
                width=5, anchor='w')
        self.id_label.grid(row=0, column=0, padx=1)

        self.name_label = ttk.Label(self.loco_frame, text=self.loco_name, width=15, anchor='w')
        self.name_label.grid(row=0, column=1, padx=4)

        self.desc_label = ttk.Label(self.loco_frame, text=self.loco_desc, width=22, anchor='w')
        self.desc_label.grid(row=1, column=0, columnspan=2, padx=1, sticky=(W+E))

        self.LocoIsReversed = IntVar(self)

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

        self.release_button = ImageButton(self.button_frame, width=96, height=32, \
                        text=' '+Local.RELEASE.title(),
                        compound=LEFT, image_file="img/buttons/minus.png", \
                        image_width=26, image_height=26,
                        command=self.on_release_clicked)
        self.release_button.set_disabled()
        self.release_button.grid(row=0, column=0, sticky=(NE))

        self.up_down_frame = ttk.LabelFrame(self.button_frame, width=98, \
                text="sort loco")

        # self.up_down_frame.grid_propagate(False)
        # self.up_down_frame.set_disabled()

        self.up_button = ImageButton(self.up_down_frame, width=47, height=28, compound=CENTER,
                        image_file="img/buttons/triangle_up.png", image_width=22, image_height=22,
                        style="link",
                        command=self.on_move_up_clicked)
        self.up_button.set_disabled()

        self.up_button.grid(row=0, column=0, sticky=(W))

        self.down_button = ImageButton(self.up_down_frame, width=47, height=28, compound=CENTER,
                        image_file="img/buttons/triangle_down.png", image_width=22, image_height=22,
                        style="link",
                        command=self.on_move_down_clicked)
        self.down_button.set_disabled()

        self.down_button.grid(row=0, column=1, sticky=(E))

        self.up_down_frame.grid(row=1, column=0, sticky=(E))

        self.release_all_button = ImageButton(self.button_frame, width=96, height=32, \
                        text=' '+Local.EMPTY.title(),
                        compound=LEFT, image_file="img/trash_can.png", \
                        image_width=26, image_height=26,
                        command=self.on_release_all_clicked)
        # self.release_all_button.set_disabled()
        self.release_all_button.grid(row=2, column=0,  sticky=(SE))

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

    def on_loco_is_reversed(self):
        """ is reversed changed """
        loco_reversed = self.LocoIsReversed.get()
        #print("Loc Reversed changed: " + str(loco_reversed))
        loco = self.parent_cab.locos_roster_map.get(self.loco_id, None)
        if loco is not None:
            if self.LocoIsReversed.get() == 1:
                loco.direction = Global.REVERSE
            else:
                loco.direction = Global.FORWARD
            #print(">>> loco dir: " + str(loco.direction))

    def on_release_all_clicked(self, _state):
        """ release all selected loco clicked """
        #print("release list")
        okk = messagebox.askokcancel(message=Local.MSG_RELEASE_CONFIRM)
        # okk = Messagebox.okcancel(message=Local.MSG_RELEASE_CONFIRM)
        if okk is True:
            # make a copy of list before we start changing it
            selected_list = copy.deepcopy(self.parent_cab.locos_selected_list)
            for loco_id in selected_list:
                self.parent_cab.publish_release_request(loco_id)
                self.parent_cab.release_loco(loco_id)
            self.loco_id = 0
            self.parent_cab.refresh_all_pages()

    def on_move_up_clicked(self, _state):
        """ move up clicked """
        print("move up in list")
        sel_list = self.parent_cab.locos_selected_list
        if self.loco_id in sel_list:
            idx = sel_list.index(self.loco_id)
            if idx > 0:  # not the first item
                sel_list[idx-1], sel_list[idx] = sel_list[idx], sel_list[idx-1]
                self.__clear_top_frame()
                self.parent_cab.build_display_lists()
                self.parent_cab.process_output_message(TkMessage(cab=Local.CAB_ALL,
                        msg_type=Global.REFRESH))

    def on_move_down_clicked(self, _state):
        """ move down clicked """
        print("move down in list")
        sel_list = self.parent_cab.locos_selected_list
        if self.loco_id in sel_list:
            idx = sel_list.index(self.loco_id)
            if (len(sel_list) - idx) >= 2:  # not the last item
                sel_list[idx], sel_list[idx+1] = sel_list[idx+1], sel_list[idx]
                self.__clear_top_frame()
                self.parent_cab.build_display_lists()
                self.parent_cab.process_output_message(TkMessage(cab=Local.CAB_ALL,
                        msg_type=Global.REFRESH))

    def on_release_clicked(self, _state):
        """ release clicked """
        #print("Release Loco: " + str(self.loco_id))
        if self.loco_id in self.parent_cab.locos_selected_list:
            self.parent_cab.publish_release_request(self.loco_id)
            self.parent_cab.release_loco(self.loco_id)
        self.loco_id = 0
        self.parent_cab.refresh_all_pages()

    def refresh_page(self):
        """ refresh the display page """
        self.__rebuild_selected_list()
        if self.loco_id > 0:
            self.__populate_top_frame()
        else:
            self.__clear_top_frame()

    def process_output_message(self, message):
        """ process output message """
        pass

    #
    # private functions
    #

    def __clear_top_frame(self):
        """ clear top frame """
        self.up_button.set_disabled()
        self.down_button.set_disabled()
        self.release_button.set_disabled()
        self.LocoIsReversed.set(0)
        self.loco_is_reversed_checkbox.configure(state='disabled')
        self.loco_name = ""
        self.loco_id = 0
        self.loco_desc = ""
        self.loco_image = self.loco_blank_image
        self.seq_number = ""
        self.id_label.config(text="")
        self.name_label.config(text=self.loco_name)
        self.desc_label.config(text=self.loco_desc)
        # self.seq_label.config(text=self.seq_number)
        self.image_label.replace_image(self.loco_image)

    def __populate_top_frame(self):
        """ populate top frame """
        self.up_button.set_normal()
        self.down_button.set_normal()
        self.release_button.set_normal()
        loco = self.__get_roster_loco_information(self.loco_id)
        self.loco_name = loco.name
        self.loco_desc = loco.text
        self.seq_number = loco.sequence
        self.loco_image = loco.image
        if loco.direction == Global.REVERSE:
            self.LocoIsReversed.set(1)
        else:
            self.LocoIsReversed.set(0)
        self.loco_is_reversed_checkbox.configure(state='normal')
        if self.loco_id > 0:
            self.id_label.config(text=self.loco_id)
        else:
            self.id_label.config(text="")
        self.name_label.config(text=self.loco_name)
        self.desc_label.config(text=self.loco_desc)
        # self.seq_label.config(text=self.__format_seq(self.seq_number))
        self.loco_image = None
        roster_loco = self.parent_cab.locos_roster_map.get(self.loco_id, None)
        if roster_loco is  not None and roster_loco.image is not None:
            self.loco_image = roster_loco.image
            self.image_label.replace_image(self.loco_image)

    def __rebuild_selected_list(self):
        """ build display list box """
        loco_selected_map = {}
        for key in self.parent_cab.locos_selected_list:
            loco = self.__get_roster_loco_information(key)
            # print(">>> loco: " + str(loco))
            if loco is None:
                loco = ThrottleMessage()
                loco.id = key
            loco_selected_map[key] = loco
        self.loco_list.populate(loco_selected_map)

    def __get_roster_loco_information(self, loco_id):
        """ get loco info from roster data """
        loco = self.parent_cab.locos_roster_map.get(loco_id, None)
        # print(">>> loco is: "+ str(loco))
        if loco is None:
            loco = ThrottleMessage()
            loco.dcc_id = loco_id
        return loco

#    def __format_seq(self, new_seq):
#        """ format sequence """
#        seq = ""
#        if new_seq is not None and new_seq > 0:
#            seq = "seq# { "+str(new_seq)+" }"
#        return seq


    #def __rebuild_loco_lists(self):
    #    """ rebuild list, redisplay available"""
    #    self.__rebuild_loco_lists()
    #    self.parent_cab.build_selected_list()
    #    self.parent_cab.build_available_list()
    #    loco_selected_map = {}
    #    for key in self.parent_cab.locos_selected_list:
    #        loco_selected_map[key] = self.parent_cab.locos_roster_map[key]
    #    self.loco_list.populate(loco_selected_map)
