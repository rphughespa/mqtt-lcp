#!/usr/bin/python3
# Dashboard_page.py

"""

DashboardPage - Display / change the state of Dashboard of computers and apps

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
import os
import sys
import copy


# import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk


from ttkbootstrap.constants import *

sys.path.append('../../lib')

from utils.global_synonyms import Synonyms
from utils.global_constants import Global

from structs.gui_message import GuiMessage
from structs.gui_message import GuiMessageEnvelope

from components.local_constants import Local
from components.dashboard_info_list import DashboardInfoList
from components.image_button import ImageButton
from components.image_clickable import ImageClickable




# from select_list_data import SelectListData
# from key_pad import KeyPadFrame


class DashboardPage(ttk.Frame):
    """ Dashboard Screen """

    def __init__(self, parent, parent_node, **kwargs):
        """ Initialize """
        super().__init__(parent, **kwargs)
        self.grid_propagate(0)
        self.parent = parent
        self.parent_node = parent_node
        self.image_path = "./img"
        self.signal_type = "color"
        self.dashboard = None
        self.dashboard_image = None
        self.dashboard_key = None
        self.dashboard_computers = {}
        self.dashboard_apps = {}

        self.info_unknown_image = None
        self.info_error_image = None
        self.info_ok_image = None

        self.__load_all_images()

        self.top_frame = ttk.Frame(
            self, width=340, height=64, padding=(2, 2, 2, 2))

        self.top_frame.grid_propagate(False)

        self.dashboard_frame = ttk.Frame(self.top_frame, relief="raised", width=236,  height=58,
                                         padding=(4, 2, 4, 2))
        self.dashboard_frame.grid_propagate(False)

        self.title_label = ttk.Label(self.dashboard_frame,
                                     text="",
                                     width=27, anchor='w')
        self.title_label.grid(row=0, column=0, padx=1)

        self.name_label = ttk.Label(self.dashboard_frame, text="",
                                    width=27, anchor='w')
        self.name_label.grid(row=1, column=0, padx=4)

        self.dashboard_frame.grid(row=0, column=0, sticky=(NW))

        self.button_frame = ttk.Frame(self.top_frame, relief="raised",
                                      height=116, width=98, padding=(2, 2, 2, 2))

        self.reboot_button = ImageButton(self.button_frame, width=96, height=32,
                                         text=' '+Local.REBOOT.title(),
                                         image_width=26, image_height=26,
                                         command=self.on_reboot_clicked)

        self.reboot_button.set_disabled()
        self.reboot_button.grid(row=0, column=0, sticky=(NE))

        self.button_frame.grid(row=0, column=1, padx=2, sticky=(NE))

        self.top_frame.grid(row=0, column=0, sticky=(NW))

        self.list_frame = ttk.Frame(
            self, padding=(2, 2, 2, 2), relief="raised")

        self.dashboard_computers_list = DashboardInfoList(self.list_frame, None,
                                                          width=330, height=320, row_height=80,
                                                          callback=self.on_list_item_clicked)
        self.dashboard_computers_list.grid(row=0, column=0)

        self.dashboard_apps_list = DashboardInfoList(self.list_frame, None,
                                                     width=330, height=320, row_height=80,
                                                     callback=None)
        self.dashboard_apps_list.grid(row=0, column=1)

        self.list_frame.grid(row=1, column=0, sticky=(SE))

    def on_list_item_clicked(self, key):
        """ List item clicked """
        # print("Dashboard Clicked: "+ str(key))
        self.dashboard_key = key
        self.__populate_top_frame()

    def on_reboot_clicked(self, _state):
        """ selection clicked """
        print(">>> reboot: " + str(self.dashboard.node_id))
        okk = messagebox.askokcancel(message=Local.MSG_REBOOT_CONFIRM)
        if okk is True:
            # print("Reboot request: " + str(self.dashboard.name))
            if self.dashboard is not None:
                # print(">>> Dashboard selected: " +str(self.dashboard))
                dashboard_message = GuiMessage()
                dashboard_message.command = Global.NODE
                dashboard_message.node_id = self.dashboard.node_id
                dashboard_message.mode = Global.REBOOT
                self.parent_node.queue_tk_input(
                    GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=dashboard_message))

    def refresh_page(self):
        """ refresh the display page """
        self.__rebuild_dashboard_list()
        if self.dashboard is not None:
            self.__populate_top_frame()
        else:
            self.__clear_top_frame()
        pass

    def process_output_message(self, message):
        """ process output message """
        if message.msg_type == Global.DASHBOARD:
            # the Dashboard status
            # print(">>> dashboard page: " + str(message.msg_type) +
            #      " ... "+str(message.msg_data))
            self.dashboard_computers = {}
            self.dashboard_apps = {}
            seq_number = 0
            nodes = message.msg_data.nodes
            if nodes is not None:
                for key, received_dashboard in nodes.items():
                    dashboard = copy.deepcopy(received_dashboard)
                    dashboard.image = self.info_unknown_image
                    if Synonyms.is_on(name=dashboard.state):
                        dashboard.image = self.info_ok_image
                    if Synonyms.is_off(name=dashboard.state):
                        dashboard.image = self.info_error_image
                    skey = key
                    if Global.SUPERVISOR.lower() in skey.lower():
                        self.dashboard_computers[skey] = dashboard
                    else:
                        self.dashboard_apps[skey] = dashboard
                    seq_number += 1
            self.refresh_page()

    #
    # private functions
    #

    def __rebuild_dashboard_list(self):
        """ build display list box """
        self.dashboard_computers_list.populate(self.dashboard_computers)
        self.dashboard_apps_list.populate(self.dashboard_apps)

    def __populate_top_frame(self):
        """ populate top frame """
        self.reboot_button.set_normal()
        self.dashboard = self.dashboard_computers[self.dashboard_key]
        self.title_label.config(text=self.dashboard.node_id)
        self.name_label.config(text=self.dashboard.description)
        #print(">>> Dashboard mode: " + str(self.dashboard.mode))

    def __clear_top_frame(self):
        """ clear top frame """
        self.reboot_button.set_disabled()
        self.dashboard = None
        self.title_label.config(text="")
        self.name_label.config(text="")

    def __load_all_images(self):
        """ load images info application """
        self.image_path = "./img"
        if "options" in self.parent_node.config[Global.CONFIG]:
            if Global.IMAGE + "-" + Global.PATH in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                self.image_path = self.parent_node.config[Global.CONFIG][
                    Global.OPTIONS][Global.IMAGE + "-" + Global.PATH]
            if Global.SIGNAL + "-" + Global.TYPE in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                self.signal_type = self.parent_node.config[Global.CONFIG][
                    Global.OPTIONS][Global.SIGNAL + "-" + Global.TYPE]

        info_image_path = os.path.join(self.image_path, Global.INFO)

        self.info_unknown_image = ImageClickable.load_image(
            os.path.join(info_image_path, "info-unknown.png"))
        self.info_error_image = ImageClickable.load_image(
            os.path.join(info_image_path, "info-red.png"))
        self.info_ok_image = ImageClickable.load_image(
            os.path.join(info_image_path, "info-green.png"))
