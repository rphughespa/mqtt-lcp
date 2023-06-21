#!/usr/bin/python3
# switches_page.py

"""

SwitchesPage - Display / change the state of switches

the MIT License (MIT)

Copyright © 2023 richard p hughes

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

from utils.global_constants import Global
from utils.global_synonyms import Synonyms

from structs.gui_message import GuiMessage
from structs.gui_message import GuiMessageEnvelope

from components.image_clickable import ImageClickable
from components.image_button import ImageButton
from components.switches_info_list import SwitchesInfoList



# from components.local_constants import Local

# from select_list_data import SelectListData
# from key_pad import KeyPadFrame


class SwitchesPage(ttk.Frame):
    """ Switches Screen """

    def __init__(self, parent, parent_node, tower_data, **kwargs):
        """ Initialize """
        super().__init__(parent, **kwargs)
        self.grid_propagate(0)
        self.parent = parent
        self.parent_node = parent_node
        self.tower_data = tower_data

        self.switch = None
        self.switch_image = None
        self.switch_key = None

        self.info_unknown_image = None
        self.info_thrown_image = None
        self.info_closed_image = None

        self.switch_unknown_image = None
        self.switch_thrown_image = None
        self.switch_closed_image = None
        self.switch_blank_image = None

        self.__load_all_images()

        self.top_frame = ttk.Frame(
            self, width=340, height=64, padding=(2, 2, 2, 2))

        self.top_frame.grid_propagate(False)

        self.switch_frame = ttk.Frame(self.top_frame, relief="raised", width=236,  height=58,
                                      padding=(4, 2, 4, 2))
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
                                      height=116, width=98, padding=(2, 2, 2, 2))

        self.switch_button = ImageButton(self.button_frame, width=96, height=36,
                                         image=self.switch_blank_image,
                                         image_width=92, image_height=28,
                                         command=self.on_switch_clicked)
        self.switch_button.set_disabled()
        self.switch_button.grid(row=0, column=0, sticky=(NE))

        self.button_frame.grid(row=0, column=1, padx=2, sticky=(NE))

        self.top_frame.grid(row=0, column=0, sticky=(NW))

        self.list_frame = ttk.Frame(
            self, padding=(2, 2, 2, 2), relief="raised")

        self.switches_list = SwitchesInfoList(self.list_frame, None,
                                              width=330, height=320, row_height=80,
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
            switch_message = GuiMessage()
            switch_message.command = Global.SWITCH
            switch_message.port_id = self.switch.port_id
            switch_message.node_id = self.switch.node_id
            switch_message.text = self.switch.text  # command topic
            switch_message.mode = new_mode
            self.parent_node.queue_tk_input(
                GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=switch_message))

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
        if message.msg_type == Global.SWITCH:
            if message.msg_data.name == Global.INFO_COMMAND:
                if message.msg_data.mode == Global.REFRESH:
                    self.refresh_page()
            elif message.msg_data is None:
                self.switch = None

    #
    # private functions
    #

    def __rebuild_switches_list(self):
        """ build display list box """
        self.switches_list.populate(self.tower_data.switches)

    def __populate_top_frame(self):
        """ populate top frame """
        self.switch = self.tower_data.switches[self.switch_key]
        self.title_label.config(text=self.switch.port_id)
        self.name_label.config(text=self.switch.name)
        #print(">>> switch mode: " + str(self.switch.mode))
        if Synonyms.is_on(name=self.switch.mode):
            self.switch_button.replace_image(image=self.switch_thrown_image)
        elif Synonyms.is_off(name=self.switch.mode):
            self.switch_button.replace_image(image=self.switch_closed_image)
        else:
            self.switch_button.replace_image(image=self.switch_unknown_image)
        self.switch_button.set_normal()

    def __clear_top_frame(self):
        """ clear top frame """
        self.switch = None
        self.title_label.config(text="")
        self.name_label.config(text="")
        if self.switch_blank_image is not None:
            self.switch_button.replace_image(image=self.switch_blank_image)
        self.switch_button.set_disabled()

    def __load_all_images(self):
        """ load images info application """
        image_path = "img"
        if "options" in self.parent_node.config[Global.CONFIG]:
            if Global.IMAGE + "-" + Global.PATH in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                image_path = self.parent_node.config[Global.CONFIG][
                    Global.OPTIONS][Global.IMAGE + "-" + Global.PATH]

        if image_path is not None:
            # load "info" signals
            info_image_path = image_path + "/" + Global.INFO

            self.info_unknown_image = ImageClickable.load_image(
                info_image_path + "/info-unknown.png")
            self.info_closed_image = ImageClickable.load_image(
                info_image_path + "/info-green.png")
            self.info_thrown_image = ImageClickable.load_image(
                info_image_path + "/info-red.png")

            switch_image_path = image_path + "/" + Global.SWITCH
            # print(">>> switch image path: "+str(switch_image_path))
            self.switch_unknown_image = ImageClickable.load_image(
                switch_image_path + "/switch-unknown.png")
            self.switch_thrown_image = ImageClickable.load_image(
                switch_image_path + "/switch-thrown.png")
            self.switch_closed_image = ImageClickable.load_image(
                switch_image_path + "/switch-closed.png")
            self.switch_blank_image = ImageClickable.load_image(
                switch_image_path + "/switch-blank.png")
            #print(">>> self.switch_blank_image" +
            #      str(self.switch_blank_image is not None))
