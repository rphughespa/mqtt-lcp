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
import copy



# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../../lib')

from utils.global_synonyms import Synonyms
from utils.global_constants import Global
from structs.throttle_message import ThrottleMessage
# from components.local_constants import Local

from components.tk_message import TkMessage
from components.switches_info_list import SwitchesInfoList
# from select_list_data import SelectListData
# from key_pad import KeyPadFrame
from components.image_button import ImageButton
from components.image_clickable import ImageClickable


class SwitchesPage(ttk.Frame):
    """ Switches Screen """

    def __init__(self, parent, parent_node, **kwargs):
        """ Initialize """
        super().__init__(parent, **kwargs)
        self.grid_propagate(0)
        self.parent = parent
        self.parent_node = parent_node
        self.switch = None
        self.switch_image = None
        self.switch_key = None
        self.switches = {}

        self.info_unknown_image = ImageClickable.load_image("img/info/info_unknown.png")
        self.info_thrown_image = ImageClickable.load_image("img/info/info_red.png")
        self.info_closed_image = ImageClickable.load_image("img/info/info_green.png")

        self.switch_unknown_image = ImageClickable.load_image("img/track/switch_unknown.png")
        self.switch_thrown_image = ImageClickable.load_image("img/track/switch_thrown.png")
        self.switch_closed_image = ImageClickable.load_image("img/track/switch_closed.png")
        self.switch_blank_image = ImageClickable.load_image("img/track/switch_blank.png")

        self.top_frame=ttk.Frame(self, width=340, height=64, padding=(2,2,2,2))

        self.top_frame.grid_propagate(False)

        self.switch_frame=ttk.Frame(self.top_frame, relief="raised", width=236,  height=58, \
                padding=(4,2,4,2))
        self.switch_frame.grid_propagate(False)

        self.title_label = ttk.Label(self.switch_frame,
                text="",
                width=27, anchor='w')
        self.title_label.grid(row=0, column=0, padx=1)

        self.name_label = ttk.Label(self.switch_frame, text="",
                width=27, anchor='w')
        self.name_label.grid(row=1, column=0, padx=4)

        self.switch_frame.grid(row=0, column=0, sticky=(NW))

        self.button_frame = ttk.Frame(self.top_frame, relief="raised",
                height=116, width=98, padding=(2,2,2,2))

        self.switch_button = ImageButton(self.button_frame, width=96, height=36, \
                        image=self.switch_blank_image,
                        image_width=92, image_height=28,
                        command=self.on_switch_clicked)
        self.switch_button.set_disabled()
        self.switch_button.grid(row=0, column=0, sticky=(NE))

        self.button_frame.grid(row=0, column=1, padx=2, sticky=(NE))

        self.top_frame.grid(row=0, column=0, sticky=(NW))

        self.list_frame = ttk.Frame(self, padding=(2,2,2,2), relief="raised")

        self.switches_list = SwitchesInfoList(self.list_frame, None, \
                width=330, height=160, row_height=80,
                callback=self.on_list_item_clicked)
        self.switches_list.grid(row=0, column=0)

        self.list_frame.grid(row=1, column=0, sticky=(SE))

    def on_list_item_clicked(self, key):
        """ List item clicked """
        # print("Switch Clicked: "+ str(key))
        self.switch_key = key
        self.__populate_top_frame()

    def on_switch_clicked(self, _state):
        """ selection clicked """
        #print("Switch turnout: " + str(self.switch.name))
        if self.switch is not None:
            #print(">>> switch selected: " +str(self.switch))
            new_mode = Global.TOGGLE
            if self.switch.mode == Global.CLOSED:
                new_mode = Global.THROW
            if self.switch.mode == Global.THROWN:
                new_mode = Global.CLOSE
            switch_message = ThrottleMessage()
            switch_message.command =  Global.SWITCH
            switch_message.port_id = self.switch.port_id
            switch_message.node_id = self.switch.node_id
            switch_message.text = self.switch.text # command topic
            switch_message.mode = new_mode
            self.parent_node.queue_tk_input( \
                    TkMessage(msg_type=Global.PUBLISH, msg_data=switch_message))

    def refresh_page(self):
        """ refresh the display page """
        self.__rebuild_switches_list()
        if self.switch is not None:
            self.__populate_top_frame()
        else:
            self.__clear_top_frame()
        pass

    def process_output_message(self, message):
        """ process output message """
        if message.msg_type == Global.SWITCHES:
            # the switch inventory
            # print(">>> switches page: " + str(message.msg_data))
            self.switches = {}
            seq_number = 0
            for key, received_switch in message.msg_data.items():
                switch = copy.deepcopy(received_switch)
                switch.image = self.info_unknown_image
                if Synonyms.in_synonym_active(name=switch.mode):
                    switch.image = self.info_thrown_image
                if Synonyms.in_synonym_inactive(name=switch.mode):
                    switch.image = self.info_closed_image
                skey = key
                self.switches[skey] = switch
                seq_number +=1
            self.refresh_page()
        elif message.msg_type == Global.SWITCH:
            #print(">>> switches page: " + str(message.msg_data))
            # an update of a signle switch state
            skey = message.msg_data.node_id + ":" + message.msg_data.port_id
            switch = self.switches.get(skey, None)
            if switch is not None:
                switch.mode = message.msg_data.mode
                switch.image = self.info_unknown_image
                if Synonyms.in_synonym_active(name=switch.mode):
                    switch.image = self.info_thrown_image
                if Synonyms.in_synonym_inactive(name=switch.mode):
                    switch.image = self.info_closed_image
                self.refresh_page()

    #
    # private functions
    #

    def __rebuild_switches_list(self):
        """ build display list box """
        self.switches_list.populate(self.switches)

    def __populate_top_frame(self):
        """ populate top frame """
        self.switch = self.switches[self.switch_key]
        self.title_label.config(text=self.switch.port_id)
        self.name_label.config(text=self.switch.name)
        #print(">>> switch mode: " + str(self.switch.mode))
        if Synonyms.in_synonym_active(name=self.switch.mode):
            self.switch_button.replace_image(image=self.switch_thrown_image)
        elif Synonyms.in_synonym_inactive(name=self.switch.mode):
            self.switch_button.replace_image(image=self.switch_closed_image)
        else:
            self.switch_button.replace_image(image=self.switch_unknown_image)
        self.switch_button.set_normal()

    def __clear_top_frame(self):
        """ clear top frame """
        self.switch = None
        self.title_label.config(text="")
        self.name_label.config(text="")
        self.switch_button.replace_image(image=self.switch_blank_image)
        self.switch_button.set_disabled()
