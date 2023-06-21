#!/usr/bin/python3
# routes_page.py

"""

RoutesPage - Display / change the state of routes

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
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../../lib')


from utils.global_constants import Global
from utils.global_synonyms import Synonyms

from structs.gui_message import GuiMessage
from structs.gui_message import GuiMessageEnvelope

from components.image_clickable import ImageClickable
from components.image_button import ImageButton
from components.routes_info_list import RoutesInfoList

from components.local_constants import Local



# from select_list_data import SelectListData
# from key_pad import KeyPadFrame


class RoutesPage(ttk.Frame):
    """ Routes Screen """

    def __init__(self, parent, parent_node, tower_data, **kwargs):
        """ Initialize """
        super().__init__(parent, **kwargs)
        self.grid_propagate(0)
        self.parent = parent
        self.parent_node = parent_node
        self.tower_data = tower_data
        self.route = None
        self.route_image = None
        self.route_key = None


        self.image_path = "./img"

        self.info_unknown_image = None
        self.info_thrown_image = None
        self.info_closed_image = None

        self.route_unknown_image = None
        self.route_thrown_image = None
        self.route_closed_image = None
        self.route_blank_image = None

        self.__load_all_images()


        self.top_frame = ttk.Frame(
            self, width=340, height=64, padding=(2, 2, 2, 2))

        self.top_frame.grid_propagate(False)

        self.route_frame = ttk.Frame(self.top_frame, relief="raised", width=236,  height=58,
                                     padding=(4, 2, 4, 2))
        self.route_frame.grid_propagate(False)

        self.title_label = ttk.Label(self.route_frame,
                                     text="",
                                     width=27, anchor='w')
        self.title_label.grid(row=0, column=0, padx=1)

        self.name_label = ttk.Label(self.route_frame, text="",
                                    width=27, anchor='w')
        self.name_label.grid(row=1, column=0, padx=4)

        self.route_frame.grid(row=0, column=0, sticky=(NW))

        self.button_frame = ttk.Frame(self.top_frame, relief="raised",
                                      height=116, width=98, padding=(2, 2, 2, 2))

        self.route_button = ImageButton(self.button_frame, width=96, height=36,
                                         image=self.route_blank_image,
                                         image_width=92, image_height=28,
                                         command=self.on_route_clicked)
        self.route_button.set_disabled()
        self.route_button.grid(row=0, column=0, sticky=(NE))


        self.button_frame.grid(row=0, column=1, padx=2, sticky=(NE))

        self.top_frame.grid(row=0, column=0, sticky=(NW))

        self.list_frame = ttk.Frame(
            self, padding=(2, 2, 2, 2), relief="raised")

        self.routes_list = RoutesInfoList(self.list_frame, None,
                                          width=330, height=320, row_height=80,
                                          callback=self.on_list_item_clicked)
        self.routes_list.grid(row=0, column=0)

        self.list_frame.grid(row=1, column=0, sticky=(SE))

    def on_list_item_clicked(self, key):
        """ List item clicked """
        # print("Route Clicked: "+ str(key))
        self.route_key = key
        self.__populate_top_frame()

    def on_route_clicked(self, _state):
        """ selection clicked """
        # print("Route request: " + str(self.route.name))
        if self.route is not None:
            # print(">>> route selected: " +str(self.route))
            new_mode = Global.ON
            if self.route.mode == Global.ON:
                new_mode = Global.OFF
            route_message = GuiMessage()
            route_message.command = Global.ROUTE
            route_message.port_id = self.route.port_id
            route_message.node_id = self.route.node_id
            route_message.text = self.route.text  # command topic
            route_message.mode = new_mode
            self.parent_node.queue_tk_input(
                GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=route_message))

    def refresh_page(self):
        """ refresh the display page """
        self.__rebuild_routes_list()
        if self.route is not None:
            self.__populate_top_frame()
        else:
            self.__clear_top_frame()
        pass

    def process_output_message(self, message):
        """ process output message """
        if message.msg_type == Global.ROUTE:
            if message.msg_data.name == Global.INFO_COMMAND:
                if message.msg_data.mode == Global.REFRESH:
                    self.refresh_page()
            elif message.msg_data is None:
                self.route = None

    #
    # private functions
    #

    def __load_all_images(self):
        """ load images info application """
        self.image_path = "./img"
        if "options" in self.parent_node.config[Global.CONFIG]:
            if Global.IMAGE + "-" + Global.PATH in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                self.image_path = self.parent_node.config[Global.CONFIG][
                    Global.OPTIONS][Global.IMAGE + "-" + Global.PATH]

        info_image_path = os.path.join(self.image_path, Global.INFO)

        self.info_unknown_image = ImageClickable.load_image(
            os.path.join(info_image_path,"info-unknown.png"))
        self.info_thrown_image = ImageClickable.load_image(
            os.path.join(info_image_path, "info-red.png"))
        self.info_closed_image = ImageClickable.load_image(
            os.path.join(info_image_path,"info-green.png"))

        route_image_path = os.path.join(self.image_path, Global.ROUTE)

        self.route_unknown_image = ImageClickable.load_image(
            os.path.join(route_image_path, "route-unknown.png"))
        self.route_thrown_image = ImageClickable.load_image(
            os.path.join(route_image_path, "route-thrown.png"))
        self.route_closed_image = ImageClickable.load_image(
            os.path.join(route_image_path,"route-closed.png"))
        self.route_blank_image = ImageClickable.load_image(
            os.path.join(route_image_path, "route-blank.png"))

    def __rebuild_routes_list(self):
        """ build display list box """
        self.routes_list.populate(self.tower_data.routes)

    def __populate_top_frame(self):
        """ populate top frame """
        self.route = self.tower_data.routes[self.route_key]
        self.title_label.config(text=self.route.port_id)
        self.name_label.config(text=self.route.name)
        if Synonyms.is_on(name=self.route.mode):
            self.route_button.replace_image(image=self.route_thrown_image)
        elif Synonyms.is_off(name=self.route.mode):
            self.route_button.replace_image(image=self.route_closed_image)
        else:
            self.route_button.replace_image(image=self.route_unknown_image)
        self.route_button.set_normal()

    def __clear_top_frame(self):
        """ clear top frame """
        self.route = None
        self.title_label.config(text="")
        self.name_label.config(text="")
        if self.route_blank_image is not None:
            self.route_button.replace_image(image=self.route_blank_image)
        self.route_button.set_disabled()
