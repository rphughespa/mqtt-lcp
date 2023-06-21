# tower_notebook.py

"""

MainNotebook - Main notebook screen

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

from utils.global_synonyms import Synonyms
from utils.global_constants import Global

from structs.tower_data import TowerData

from components.local_constants import Local
from components.system_page import SystemPage
from components.dashboard_page import DashboardPage
from components.switches_page import SwitchesPage
from components.routes_page import RoutesPage
from components.signals_page import SignalsPage
from components.panels_notebook import PanelsNotebook
from components.image_button import ImageButton
from components.image_clickable import ImageClickable


#class TowerData(object):
#    """ data shared by multiple tower pages """
#
#    def __init__(self):
#        self.signals = {}
#        self.switches = {}
#        self.blocks = {}
#
#    def __repr__(self):
#        # return "%s(%r)" % (self.__class__, self.__dict__)
#        fdict = repr(self.__dict__)
#        return f"{self.__class__}({fdict})"


class MainNotebook(ttk.Frame):
    """ tower notebook screen """

    def __init__(self, parent, parent_node, **kwargs):
        """ initailize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_node = parent_node
        self.notebook = ttk.Notebook(self)  # , style='MyL.Notebook')
        self.notebook.grid(row=0, column=0, sticky='NESW')
        self.notebook.configure(style="Left.TNotebook")

        self.info_unknown_image = None
        self.info_thrown_image = None
        self.info_closed_image = None
        self.info_clear_image = None
        self.info_approach_image = None
        self.info_stop_image = None

        self.tower_data = TowerData()

        self.panels_notebook = PanelsNotebook(self.notebook, parent_node, self.tower_data, padding=(2, 2, 2, 2),
                                              borderwidth=1, relief="flat", style="My.TFrame")
        self.notebook.add(self.panels_notebook, text=' ' +
                          Local.PANELS.title()+' ')

        self.switches_page = SwitchesPage(self.notebook, parent_node, self.tower_data, padding=(2, 2, 2, 2),
                                          borderwidth=1, relief="flat", style="My.TFrame")
        self.notebook.add(self.switches_page, text=' ' +
                          Local.SWITCHES.title()+' ')

        self.routes_page = RoutesPage(self.notebook, parent_node, self.tower_data, padding=(2, 2, 2, 2),
                                      borderwidth=1, relief="flat", style="My.TFrame")
        self.notebook.add(self.routes_page, text=' '+Local.ROUTES.title()+' ')

        self.signals_page = SignalsPage(self.notebook, parent_node, self.tower_data, padding=(2, 2, 2, 2),
                                        borderwidth=1, relief="flat", style="My.TFrame")
        self.notebook.add(self.signals_page, text=' ' +
                          Local.SIGNALS.title()+' ')

        self.dashboard_page = DashboardPage(self.notebook, self.parent_node,
                                            padding=(2, 2, 2, 2), borderwidth=1, relief="flat",
                                            width=340, height=360, style="My.TFrame")
        self.notebook.add(self.dashboard_page, text=' ' +
                          Local.DASHBOARD.title()+' ')

        self.system_page = SystemPage(self.notebook, self.parent_node,
                                      padding=(2, 2, 2, 2), borderwidth=1, relief="flat",
                                      width=340, height=360, style="My.TFrame")
        self.notebook.add(self.system_page, text=' '+Local.SYSTEM.title()+' ')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

        self.__load_all_images()

    def process_output_message(self, message):
        """ process output message"""
        if message.msg_type == Global.SIGNAL:
            if message.msg_data.name == Global.INFO_COMMAND:
                if message.msg_data.mode == Global.CLEAR:
                    self.tower_data.signals = {}
            else:
                self.__update_tower_signals(message)
        if message.msg_type == Global.SWITCH:
            if message.msg_data.name == Global.INFO_COMMAND:
                if message.msg_data.mode == Global.CLEAR:
                    self.tower_data.switches = {}
            else:
                self.__update_tower_switches(message)
        if message.msg_type == Global.BLOCK:
            if message.msg_data.name == Global.INFO_COMMAND:
                if message.msg_data.mode == Global.CLEAR:
                    self.tower_data.blocks= {}
            else:
                self.__update_tower_blocks(message)
        if message.msg_type == Global.ROUTE:
            if message.msg_data.name == Global.INFO_COMMAND :
                if message.msg_data.mode == Global.CLEAR:
                    self.tower_data.routes = {}
            else:
                self.__update_tower_routes(message)
        self.switches_page.process_output_message(message)
        self.routes_page.process_output_message(message)
        self.signals_page.process_output_message(message)
        self.panels_notebook.process_output_message(message)
        self.dashboard_page.process_output_message(message)
        self.system_page.process_output_message(message)

#
# private functions
#

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
            self.info_clear_image = ImageClickable.load_image(
                info_image_path + "/info-green.png")
            self.info_approach_image = ImageClickable.load_image(
                info_image_path + "/info-yellow.png")
            self.info_stop_image = ImageClickable.load_image(
                info_image_path + "/info-red.png")

    def __update_tower_signals(self, message):
        """ apply new message to tower signal data """
        skey = message.msg_data.port_id
        signal = self.tower_data.signals.get(skey, None)
        if signal is None:
            signal = copy.deepcopy(message.msg_data)
            self.tower_data.signals[skey] = signal
        if signal is not None:
            signal.mode = message.msg_data.mode
            signal = self.__set_signal_image(signal)

    def __update_tower_blocks(self, message):
        """ apply new message to tower block data """
        skey = message.msg_data.block_id
        block = self.tower_data.signals.get(skey, None)
        if block is None:
            block = copy.deepcopy(message.msg_data)
            self.tower_data.blocks[skey] = block
        if block is not None:
            block.mode = message.msg_data.mode
            if Synonyms.is_on(name=block.mode):
                block.image = self.info_stop_image
            if Synonyms.is_off(name=block.mode):
                block.image = self.info_clear_image

    def __update_tower_switches(self, message):
        """ apply new message to tower switches """
        if message.msg_data is None:
            # clear out switch table
            self.tower_data.switches = {}
        else:
            # print(">>> switches page: " + str(message.msg_data))
            # an update of a single switch state
            skey = message.msg_data.port_id
            switch = self.tower_data.switches.get(skey, None)
            if switch is None:
                switch = copy.deepcopy(message.msg_data)
                switch.image = self.info_unknown_image
                self.tower_data.switches[skey] = switch
            if switch is not None:
                switch.mode = message.msg_data.mode
                switch.image = self.info_unknown_image
                if Synonyms.is_on(name=switch.mode):
                    switch.image = self.info_thrown_image
                if Synonyms.is_off(name=switch.mode):
                    switch.image = self.info_closed_image

    def __update_tower_routes(self, message):
        """ apply new message to tower routes """
        if message.msg_data is None:
            # clear out switch table
            self.tower_data.routes = {}
        else:
            # print(">>> tower route: "+str(message.msg_data))
            skey = message.msg_data.port_id
            route = self.tower_data.routes.get(skey, None)
            if route is None:
                route = copy.deepcopy(message.msg_data)
                route.image = self.info_unknown_image
                self.tower_data.routes[skey] = route
            if route is not None:
                route.mode = message.msg_data.mode
                route.image = self.info_unknown_image
                if Synonyms.is_on(name=route.mode):
                    route.image = self.info_thrown_image
                if Synonyms.is_off(name=route.mode):
                    route.image = self.info_closed_image

    def __set_signal_image(self, signal):
        """ set signal image based on mode """
        if signal.mode == Global.CLEAR:
            signal.image = self.info_clear_image
        elif signal.mode == Global.STOP:
            signal.image = self.info_stop_image
        elif signal.mode == Global.APPROACH:
            signal.image = self.info_approach_image
        else:
            signal.image = self.info_unknown_image
        return signal
