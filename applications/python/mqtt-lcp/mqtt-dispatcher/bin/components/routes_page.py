#!/usr/bin/python3
# routes_page.py

"""

RoutesPage - Display / change the state of routes

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

from structs.gui_message import GuiMessage
from utils.global_constants import Global
from utils.global_synonyms import Synonyms

from components.image_clickable import ImageClickable
from components.image_button import ImageButton
from components.routes_info_list import RoutesInfoList
from components.tk_message import TkMessage
from components.local_constants import Local



# from select_list_data import SelectListData
# from key_pad import KeyPadFrame


class RoutesPage(ttk.Frame):
    """ Routes Screen """

    def __init__(self, parent, parent_node, **kwargs):
        """ Initialize """
        super().__init__(parent, **kwargs)
        self.grid_propagate(0)
        self.parent = parent
        self.parent_node = parent_node
        self.route = None
        self.route_image = None
        self.route_key = None
        self.routes = {}

        self.info_unknown_image = ImageClickable.load_image(
            "img/info/info-unknown.png")
        self.info_thrown_image = ImageClickable.load_image(
            "img/info/info-red.png")
        self.info_closed_image = ImageClickable.load_image(
            "img/info/info-green.png")

        self.route_unknown_image = ImageClickable.load_image(
            "img/panel/route-unknown.png")
        self.route_thrown_image = ImageClickable.load_image(
            "img/panel/route-thrown.png")
        self.route_closed_image = ImageClickable.load_image(
            "img/panel/route-closed.png")
        self.route_blank_image = ImageClickable.load_image(
            "img/panel/route-blank.png")

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

        self.request_button = ImageButton(self.button_frame, width=96, height=32,
                                          text=' '+Local.REQUEST.title(),
                                          image_width=26, image_height=26,
                                          command=self.on_request_clicked)

        self.request_button.set_disabled()
        self.request_button.grid(row=0, column=0, sticky=(NE))

        self.button_frame.grid(row=0, column=1, padx=2, sticky=(NE))

        self.top_frame.grid(row=0, column=0, sticky=(NW))

        self.list_frame = ttk.Frame(
            self, padding=(2, 2, 2, 2), relief="raised")

        self.routes_list = RoutesInfoList(self.list_frame, None,
                                          width=330, height=220, row_height=80,
                                          callback=self.on_list_item_clicked)
        self.routes_list.grid(row=0, column=0)

        self.list_frame.grid(row=1, column=0, sticky=(SE))

    def on_list_item_clicked(self, key):
        """ List item clicked """
        # print("Route Clicked: "+ str(key))
        self.route_key = key
        self.__populate_top_frame()

    def on_request_clicked(self, _state):
        """ selection clicked """
        # print("Route request: " + str(self.route.name))
        if self.route is not None:
            # print(">>> route selected: " +str(self.route))
            route_message = GuiMessage()
            route_message.command = Global.SWITCH
            route_message.port_id = self.route.port_id
            route_message.node_id = self.route.node_id
            route_message.text = self.route.text  # command topic
            route_message.mode = Global.ACTIVATE
            self.parent_node.queue_tk_input(
                TkMessage(msg_type=Global.PUBLISH, msg_data=route_message))

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
            #print(">>> routes page: " + str(message.msg_data))
            # an update of a signle route state
            skey = message.msg_data.node_id + ":" + message.msg_data.port_id
            route = self.routes.get(skey, None)
            if route is None:
                route = copy.deepcopy(message.msg_data)
                route.image = self.info_unknown_image
                if Synonyms.is_synonym_active(name=route.mode):
                    route.image = self.info_thrown_image
                if Synonyms.is_synonym_inactive(name=route.mode):
                    route.image = self.info_closed_image
                self.routes[skey] = route
            if route is not None:
                route.mode = message.msg_data.mode
                route.image = self.info_unknown_image
                if Synonyms.is_synonym_active(name=route.mode):
                    route.image = self.info_thrown_image
                if Synonyms.is_synonym_inactive(name=route.mode):
                    route.image = self.info_closed_image
                self.refresh_page()

    #
    # private functions
    #

    def __rebuild_routes_list(self):
        """ build display list box """
        self.routes_list.populate(self.routes)

    def __populate_top_frame(self):
        """ populate top frame """
        self.request_button.set_normal()
        self.route = self.routes[self.route_key]
        self.title_label.config(text=self.route.port_id)
        self.name_label.config(text=self.route.name)
        #print(">>> route mode: " + str(self.route.mode))

    def __clear_top_frame(self):
        """ clear top frame """
        self.request_button.set_disabled()
        self.route = None
        self.title_label.config(text="")
        self.name_label.config(text="")
