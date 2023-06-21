#!/usr/bin/python3
# main_notebook.py

"""

CabNotebook - Cab Notebook screen, parent of cab sub screens. Contains data used by all cab sub screens


    Multiple list are maintains that supports he loco screens:

        parent_node.roster.items - master list (dict) of locos from tower
                these items are augments in this application by adding loco images
        loco_roster_map : roster.items dict entries reformated for use in scrollable_listms list
        locos_available_list: items from loco_roster_map whose state is unselected
        locos_selected_list: items from loco_roster_map whose state is selected
        locos_selected_by_seq_list: selected list keys indexed by sequence number



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

import os
import sys
import copy

# import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk

from ttkbootstrap.constants import *

sys.path.append('../../lib')

from utils.global_constants import Global

from structs.gui_message import GuiMessage
from structs.gui_message import GuiMessageEnvelope


from components.image_clickable import ImageClickable
from components.locos_notebook import LocosNotebook
from components.functions_page import FunctionsPage
from components.controls_page import ControlsPage
from components.local_constants import Local


# from components.select_list_data import SelectListData


class CabNotebook(ttk.Frame):
    """ main notebook """

    def __init__(self, parent, parent_node, cab_id, **kwargs):
        """ init cab notebook"""
        super().__init__(parent, **kwargs)
        # self.grid_propagate(False)
        self.parent = parent
        self.parent_node = parent_node
        self.cab_id = cab_id
        self.lead_loco = None
        self.loco_cab_signal_aspect = Global.APPROACH
        self.locos_selected_list = []
        self.locos_available_list = []
        self.locos_roster_map = {}
        self.loco_images_map = {}
        self.loco_blank_image = None
        self.__load_all_images()
        self.loco_current_speed = 0
        self.loco_current_direction = None
        self.loco_current_functions = []
        for _func in range(0, 28):
            self.loco_current_functions.append(0)  # 0=off 1=on
        self.clear_loco_data()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='NESW')
        self.notebook.configure(style="Left.TNotebook")

        self.controls_page = ControlsPage(self.notebook, self.parent_node, self, self.cab_id,
                                          padding=(2, 2, 2, 2), borderwidth=1, relief="flat")
        self.notebook.add(self.controls_page, text=' ' +
                          Local.THROTTLE.title()+' ')

        self.functions_page = FunctionsPage(self.notebook, self.parent_node, self, padding=(2, 2, 2, 2),
                                            borderwidth=1, relief="flat")
        self.notebook.add(self.functions_page, text=' ' +
                          Local.FUNCTIONS.title()+' ')

        self.locos_notebook = LocosNotebook(self.notebook, parent_node, self,
                                            padding=(2, 2, 2, 2), borderwidth=1, relief="flat")
        self.notebook.add(self.locos_notebook, text=' ' +
                          Local.LOCOS.title()+' ')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

    def by_sequence(self, item):
        """ get sequence number """
        return item[1].seq_number

    def build_selected_list(self, _renumber=True):
        """ build selected list """
        # self.locos_selected_list = []
        # for key, value in sorted(self.locos_roster_map.items()):
        #    if value.state == Local.SELECTED:
        #        self.locos_selected_list += [key]
        self.lead_loco = None
        selected_list_len = len(self.locos_selected_list)
        if selected_list_len > 0:
            self.lead_loco = self.locos_selected_list[0]
            self.controls_page.status_frame.set_loco(str(self.lead_loco))
        else:
            self.controls_page.status_frame.set_loco("")

    def build_available_list(self):
        """ build available list """
        self.locos_available_list = []
        for key in sorted(self.locos_roster_map):
            if self.locos_roster_map[key].mode != Local.SELECTED:
                # print(">>> avail: " + str(key))
                self.locos_available_list += [key]

    def build_display_lists(self):
        """ build display list"""
        self.build_available_list()
        self.build_selected_list()

    def build_roster_display_list(self, roster_data):
        """ build roster list """
        # print(">>> locos: " + str(roster_data))
        self.locos_selected_list = []
        for _key, roster_loco in roster_data.items():
            loco = copy.deepcopy(roster_loco)
            loco.mode = Local.UNSELECTED
            loco.direction = Global.FORWARD
            loco.sequence = 0
            # print(">>> roster image: " +str(roster_loco.image))
            # roster loco_image is a string of loco image file
            # in loco_roster_map replace with the image itself
            if roster_loco.image in self.loco_images_map:
                loco.image = self.loco_images_map[roster_loco.image]
            else:
                # print(">>> loco image not found for : " + str(roster_loco.image))
                loco.image = self.loco_blank_image
            self.locos_roster_map[loco.dcc_id] = loco
        self.build_display_lists()

    def clear_loco_data(self):
        """ clear loco data """
        self.loco_current_direction = None
        for func in range(0, 28):
            self.loco_current_functions[func] = 0  # 0=off 1=on

    def process_output_message(self, message):
        """ process output message """
        if message.msg_type == Global.ROSTER:
            self.build_roster_display_list(message.msg_data)
            self.build_display_lists()
            self.refresh_all_pages()
        elif message.msg_type == Global.CAB_SIGNAL:
            #print(">>> cab signal: " +str(message.msg_data.dcc_id) +\
            #        " : "+str(message.msg_data.mode))
            if self.lead_loco == message.msg_data.dcc_id:
                self.loco_cab_signal_aspect = message.msg_data.mode
                self.controls_page.refresh_page()
        elif message.msg_type == Global.REFRESH:
            self.build_display_lists()
            self.refresh_all_pages()
        elif message.msg_type == Global.STEAL_NEEDED:
            self.__process_steal_needed(message.msg_data)
        elif message.msg_type == Global.STOLEN:
            self.__process_stolen(message.msg_data)
            self.refresh_all_pages()
        else:
            self.controls_page.process_output_message(message)
            self.locos_notebook.process_output_message(message)

    def refresh_all_pages(self):
        """ ask pages to refresh their display """
        self.build_display_lists()
        self.controls_page.refresh_page()
        self.functions_page.refresh_page()
        self.locos_notebook.refresh_page()

    def publish_acquire_request(self, dcc_id):
        """ send acquire requested """
        acquire_message = GuiMessage()
        acquire_message.command = Global.THROTTLE
        acquire_message.sub_command = Global.ACQUIRE
        acquire_message.dcc_id = dcc_id
        acquire_message.cab_id = self.cab_id
        self.parent_node.queue_tk_input(
            GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=acquire_message))

    def publish_steal_request(self, dcc_id):
        """ send steal requested """
        steal_message = GuiMessage()
        steal_message.command = Global.THROTTLE
        steal_message.sub_command = Global.STEAL
        steal_message.dcc_id = dcc_id
        steal_message.cab_id = self.cab_id
        self.parent_node.queue_tk_input(
            GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=steal_message))

    def publish_release_request(self, dcc_id):
        """ send acquire requested """
        release_message = GuiMessage()
        release_message.command = Global.THROTTLE
        release_message.sub_command = Global.RELEASE
        release_message.dcc_id = dcc_id
        release_message.cab_id = self.cab_id
        self.parent_node.queue_tk_input(
            GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=release_message))

    def publish_speed_request(self):
        """ send speed requested  for all locos selected """
        speed_message = GuiMessage()
        speed_message.command = Global.THROTTLE
        speed_message.sub_command = Global.SPEED
        # send speed for all locos in cab
        speed_message.dcc_id = None
        speed_message.cab_id = self.cab_id
        speed_message.speed = self.loco_current_speed
        self.parent_node.queue_tk_input(
            GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=speed_message))

    def publish_direction_request(self):
        """ send speed requested  for all locos selected """
        for dcc_id in self.locos_selected_list:
            loco = self.locos_roster_map.get(dcc_id, None)
            if loco is not None:
                direction_message = GuiMessage()
                direction_message.command = Global.THROTTLE
                direction_message.sub_command = Global.DIRECTION
                direction_message.dcc_id = loco.dcc_id
                direction_message.cab_id = self.cab_id
                direction_message.direction = self.loco_current_direction
                if loco.direction == Global.REVERSE:
                    if self.loco_current_direction == Global.FORWARD:
                        direction_message.direction = Global.REVERSE
                    else:
                        direction_message.direction = Global.FORWARD
                self.parent_node.queue_tk_input(
                    GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=direction_message))

    def publish_function_request(self, function_id):
        """ send speed requested  for all locos selected """
        func = int(function_id)
        mode = self.get_function_state(func)
        if 0 <= func <= 2:
            # send func 0-2 only to lead loco
            dcc_id = self.locos_selected_list[0]
            self.__publish_function_request(dcc_id, func, mode)
        elif 3 <= func <= 27:
            # send to all loco in cab
            self.__publish_function_request(None, func, mode)

    def set_function_state(self, function_id, function_state):
        """ set function state """
        func = int(function_id)
        func_value = 0
        if function_state == Global.ON:
            func_value = 1
        if 0 <= func <= 27:
            # print(">>> func set: " + str(func) + " : " + str(func_value))
            self.loco_current_functions[func] = func_value

    def get_function_state(self, function_id):
        """ get state of a function """
        func = int(function_id)
        rett = Global.OFF
        if 0 <= func <= 27:
            if self.loco_current_functions[func] == 1:
                rett = Global.ON
        return rett

    def any_locos_selected(self):
        """ have any locos been selected """
        rett = False
        if len(self.locos_selected_list) > 0:
            rett = True
        return rett

    def release_loco(self, dcc_id):
        """ remove loco from selected list """
        if dcc_id in self.locos_selected_list:
            self.locos_selected_list.remove(dcc_id)
        loco = self.locos_roster_map.get(dcc_id, None)
        if loco is not None:
            loco.mode = Local.UNSELECTED
            loco.direction = Global.FORWARD
            if loco.reported == Global.KEYPAD:
                # temp roster loco added by keypad selection, remove it
                del self.locos_roster_map[dcc_id]
        if not self.any_locos_selected():
            self.locos_selected_list = []
            self.clear_loco_data()

    #
    # private functions
    #

    def __load_all_images(self):
        """ load images info application """
        image_path = None
        _signal_type = "color"
        if "options" in self.parent_node.config[Global.CONFIG]:
            if Global.SIGNAL + "-" + Global.TYPE in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                _signal_type = self.parent_node.config[Global.CONFIG][
                    Global.OPTIONS][Global.SIGNAL + "-" + Global.TYPE]
            if Global.IMAGE + "-" + Global.PATH in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                image_path = self.parent_node.config[Global.CONFIG][Global.OPTIONS][Global.IMAGE + "-" + Global.PATH]

        if image_path is not None:
            # load "cab" signals

            # locos_image_path = image_path + "/" + Global.LOCOS + \
            #    "/" + signal_type + "/" + Global.CAB
            locos_image_path = os.path.join(image_path, Global.LOCOS)
            self.loco_blank_image = ImageClickable.load_image(
                locos_image_path+"/blank.png")

            self.loco_images_map = {}

            files = os.listdir(locos_image_path)
            for file in files:
                loco_name = os.path.basename(file)
                loco_image_file_path = os.path.join(locos_image_path, file)
                #print(">>> loco: "+str(loco_image_file_path) +
                #     "..." + str(loco_name))
                self.loco_images_map[loco_name] = ImageClickable.load_image(
                    loco_image_file_path)

    def __publish_function_request(self, dcc_id, func, mode):
        """ publish a loco function request"""
        function_message = GuiMessage()
        function_message.command = Global.THROTTLE
        function_message.sub_command = Global.FUNCTION
        function_message.dcc_id = dcc_id
        function_message.cab_id = self.cab_id
        function_message.function = func
        function_message.mode = mode
        self.parent_node.queue_tk_input(
            GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=function_message))

    def __process_steal_needed(self, loco_id):
        """ a steal needed response received, process it """
        dcc_id = int(loco_id)
        steal_message = Global.LOCO.title() + " " + str(dcc_id) + \
            Local.MSG_STEAL_NEEDED_CONFIRM
        resp_yes = messagebox.askyesno(message=steal_message)
        # yes no: "+ str(resp_yes))
        if resp_yes:
            # print(">>> send steal request: " + str(self.cab_id) + \
            #        " ... " + str(loco_id))
            self.publish_steal_request(dcc_id)
        else:
            # print(">>> remove loco from selected list: " + str(self.cab_id) + \
            #        " ... " + str(loco_id))
            self.release_loco(dcc_id)
            self.refresh_all_pages()

    def __process_stolen(self, dcc_id):
        """ a loco has been stolen, remove from selected list """
        self.release_loco(dcc_id)
