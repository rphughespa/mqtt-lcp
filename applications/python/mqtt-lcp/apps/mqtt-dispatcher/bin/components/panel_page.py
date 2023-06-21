#!/usr/bin/python3
# panel_page.py

"""

PanelPage - control panel page screen

the MIT License (MIT)

Copyright 2023 richard p hughes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import sys
import copy

# from ast import Pass

from tkinter import *
# from tkinter import messagebox
# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
# from tkinter import messagebox

sys.path.append('../../lib')

from utils.global_synonyms import Synonyms
from utils.global_constants import Global

from structs.gui_message import GuiMessage
from structs.gui_message import GuiMessageEnvelope

from components.image_clickable import ImageClickable



# from ossaudiodev import control_names
# from components.local_constants import Local
# from structs.gui_message import GuiMessageEnvelope

# from image_button import ImageButton

IMAGE_WIDTH = 48  # 64
IMAGE_HEIGHT = 24  # 32


class PanelItem(object):
    """ panel item """

    def __init__(self, key=None, button=None, state=None, ptype=Global.BLANK):
        self.key = key
        self.button = button
        self.state = state
        self.type = ptype


class PanelPage(ttk.Frame):
    """ control panel page """

    def __init__(self, parent_page, parent, parent_node, tower_data, _layout_images, name, rows, callback, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent_page = parent_page
        self.parent = parent
        self.parent_node = parent_node
        self.tower_data = tower_data
        self.name = name
        self.switches = []
        self.signals = []
        self.blocks = []
        self.locators = []
        self.routes = []
        self.callback = callback
        self.style = ttk.Style()
        self.style.configure(
            "Panel.TLabel", foreground="black", background="white")
        (self.row_map, self.panel_rows, self.panel_cols) = self.__map_rows(rows)
        (self.panel_width, self.panel_height) = self.__calc_panel_size(
            self.panel_rows, self.panel_cols)
        # print(">>> panel size: "+str(self.panel_width) +
        #       " : " + str(self.panel_height))
        self.canvas = ttk.Canvas(
            self, width=self.panel_width, height=self.panel_height)  # bg='black')
        self.frame = ttk.Frame(self.canvas)
        self.vsb = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.hsb = ttk.Scrollbar(
            self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.hsb.set)
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw",
                                  tags="self.frame")
        self.frame.bind("<Configure>", self.onFrameConfigure)

        if self.row_map is not None and \
                len(self.row_map) > 0:
            self.populate(self.row_map, self.panel_rows, self.panel_cols)
            # initialize the panel with data already reveived
            for _key, switch in self.tower_data.switches.items():
                message = GuiMessageEnvelope(msg_type=Global.SWITCH,
                                    cab=Global.CAB_ALL,
                                    msg_data=switch)
                self.__process_a_switch_change(message)

            for _key, signal in self.tower_data.signals.items():
                message = GuiMessageEnvelope(msg_type=Global.SIGNAL,
                                    cab=Global.CAB_ALL,
                                    msg_data=signal)
                self.__process_a_signal_change(message)

            for _key, route in self.tower_data.routes.items():
                message = GuiMessageEnvelope(msg_type=Global.ROUTE,
                                    cab=Global.CAB_ALL,
                                    msg_data=route)
                self.__process_a_route_change(message)

    def populate(self, row_map, panel_rows, panel_cols):
        """ populate page """
        # col data may be sparse within in rows, ie not 1,2,3,4,5 rather 2,5
        # create blank images for missing col data
        # print(">>> row map: " + str(row_map))
        for r in range(panel_rows):
            row = r + 1  # python range is zero based
            mapped_row = row_map.get(row, None)
            # print(">>> mapped row: " + str(mapped_row))
            if mapped_row is None:
                # no row defined, generate a row of blanks
                for c in range(panel_cols):
                    col = c + 1  # python range os zero based
                    # insert blanks images
                    self.__insert_image(
                        row, col, Global.BLOCK, Global.UNKNOWN, Global.BLANK, "")
            else:
                for c in range(panel_cols):
                    col = c + 1  # python range is zero based
                    mapped_col = None
                    mapped_cols = mapped_row.get(Global.COLS, None)
                    if mapped_cols is not None:
                        mapped_col = mapped_cols.get(col, None)
                    if mapped_col is None:
                        # insert blanks images
                        self.__insert_image(
                                row, col, Global.BLOCK, \
                                Global.UNKNOWN, Global.BLANK, "")
                    else:
                        # print(">>> mapped col: "+str(mapped_col))
                        ident = ""
                        button = None
                        if mapped_col.type in [Global.BLOCK, Global.SWITCH, \
                                               Global.ROUTE, Global.SIGNAL, Global.LOCATOR]:
                            if mapped_col.port_id is not None:
                                ident = mapped_col.port_id
                            elif mapped_col.block_id is not None:
                                ident = mapped_col.block_id
                        if mapped_col.type == Global.LOCATOR:
                            button = self.__insert_text(row, col, mapped_col.type,
                                                        Global.UNKNOWN, mapped_col.image, ident)
                        else:
                            button = self.__insert_image(row, col, mapped_col.type,
                                                         Global.UNKNOWN, mapped_col.image, ident)
                        if mapped_col.type == Global.SWITCH:
                            self.switches.append(PanelItem(key=ident,
                                                           button=button, state=Global.UNKNOWN, ptype=mapped_col.image))
                        elif mapped_col.type == Global.SIGNAL:
                            self.signals.append(PanelItem(key=ident,
                                                          button=button, state=Global.UNKNOWN, ptype=mapped_col.image))
                        elif mapped_col.type == Global.ROUTE:
                            self.routes.append(PanelItem(key=ident,
                                                          button=button, state=Global.UNKNOWN, ptype=mapped_col.image))
                        elif mapped_col.type == Global.BLOCK:
                            # print(">>> new block: " + str(row) + " ... " +  \
                            # str(col) + " ... "+ str(ident) + " ... " + str(mapped_col))
                            self.blocks.append(PanelItem(key=ident, button=button,
                                                         state=Global.UNKNOWN, ptype=mapped_col.image))
                        elif mapped_col.type == Global.LOCATOR:
                            self.locators.append(PanelItem(key=ident, button=button,
                                                           state=""))
                        mapped_col.display = button

    def onFrameConfigure(self, _event):
        """ frame configure selected"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def process_output_message(self, message):
        """ process output message """
        # print(">>> panel message: " + str(message.msg_type))
        if message.msg_type == Global.SWITCH:
            self.__process_a_switch_change(message)
        elif message.msg_type == Global.SIGNAL:
            self.__process_a_signal_change(message)
        elif message.msg_type == Global.ROUTE:
            self.__process_a_route_change(message)
        elif message.msg_type == Global.BLOCK:
            self.__process_a_block_change(message)
        elif message.msg_type == Global.LOCATOR:
            self.__process_a_locator_change(message)

    def on_item_clicked(self, state):
        """ panel item clicked """
        (group, ident) = state
        # print(">>> Item Clicked: " + str(group) + " : "+str(ident))
        if group == Global.SIGNAL:
            self.__signal_clicked(ident)
        elif group == Global.SWITCH:
            self.__switch_clicked(ident)
        elif group == Global.ROUTE:
            self.__route_clicked(ident)

    #
    # private functions
    #

    def __signal_clicked(self, ident):
        """ signal clicked """
        # print(">>> Signal Clicked: " + str(ident))
        signal = self.tower_data.signals.get(ident, None)
        if signal is not None:
            new_mode = Global.APPROACH
            if signal.mode == Global.APPROACH:
                new_mode = Global.CLEAR
            elif signal.mode == Global.CLEAR:
                new_mode = Global.STOP
            signal_message = GuiMessage()
            signal_message.command = Global.SIGNAL
            signal_message.port_id = signal.port_id
            signal_message.node_id = signal.node_id
            signal_message.text = signal.text  # command topic
            signal_message.mode = new_mode
            self.parent_node.queue_tk_input(
                GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=signal_message))

    def __route_clicked(self, ident):
        """ route clicked """
        # print(">>> Route Clicked: " + str(ident))
        route = self.tower_data.routes.get(ident, None)
        if route is not None:
            new_mode = Global.ON
            if route.mode == Global.ON:
                new_mode = Global.OFF
            route_message = GuiMessage()
            route_message.command = Global.ROUTE
            route_message.port_id = route.port_id
            route_message.node_id = route.node_id
            route_message.text = route.text  # command topic
            route_message.mode = new_mode
            self.parent_node.queue_tk_input(
                GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=route_message))

    def __switch_clicked(self, ident):
        """ switch clicked """
        # print(">>> Switch Clicked: " + str(ident))
        switch = self.tower_data.switches.get(ident, None)
        if switch is not None:
            new_mode = Global.THROW
            if switch.mode == Global.THROWN:
                new_mode = Global.CLOSE
            switch_message = GuiMessage()
            switch_message.command = Global.SWITCH
            switch_message.port_id = switch.port_id
            switch_message.node_id = switch.node_id
            switch_message.text = switch.text  # command topic
            switch_message.mode = new_mode
            self.parent_node.queue_tk_input(
                GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=switch_message))

    def __insert_image(self, r, c, group, state, image_name, ident):
        # create a new image on the panel
        error = False
        if self.parent_page.layout_images.get(group, None) is None:
            error = True
        else:
            if self.parent_page.layout_images[group].get(state, None) is None:
                error = True
            else:
                if self.parent_page.layout_images[group][state].get(image_name, None) is None:
                    error = True
        rett_button = None
        if error:
            # use a default blank image
            group = Global.BLOCK
            state = Global.UNKNOWN
            image_name = Global.BLANK
            print("!!! Error is panel image not found: " +
                  str(r) + " : " + str(c) + " ... " + str(group) +
                  " ... " + str(state) + " ... " + str(image_name))
        else:
            layout_image = self.parent_page.layout_images[group][state][image_name]
            if ident != "":
                layout_button = ImageClickable(self.frame, height=IMAGE_HEIGHT, width=IMAGE_WIDTH,
                                               image=layout_image,
                                               bg="black", command=self.on_item_clicked,
                                               command_value=(group, ident))
                layout_button.grid(row=r, column=c, padx=0,
                                   pady=0, ipadx=0, ipady=0)
                rett_button = layout_button
            else:
                layout_image = ImageClickable(self.frame, height=IMAGE_HEIGHT, width=IMAGE_WIDTH,
                                              image=layout_image, bg="black")
                layout_image.grid(row=r, column=c, padx=0,
                                  pady=0, ipadx=0, ipady=0)
                rett_button = layout_image
            if rett_button is None:
                print("!!! Error image not found: "+str(group) +
                      ":"+str(state)+":"+str(image_name))
        return rett_button

    def __insert_text(self, r, c, _group, _state, _image_name, _ident):
        # create a new text box on the panel
        locator_box = ttk.Label(self.frame, text="     ",
                                width=5, style="Panel.TLabel")
        # bootstyle="dark")
        # bg="black", fg="white", width=5)
        locator_box.grid(row=r, column=c, padx=0,
                         pady=0, ipadx=0, ipady=0)
        return locator_box

    def __map_rows(self, rows):
        """ map a list of rows,col into a dict by row number, col number """
        max_rows = 1
        max_cols = 1
        row_map = {}
        for row in rows:
            mapped_row = {}
            mapped_row[Global.ROW] = row.row
            max_rows = max(max_rows, row.row)
            cols = {}
            for col in row.cols:
                max_cols = max(max_cols, col.col)
                cols[col.col] = col
            mapped_row[Global.COLS] = cols
            row_map[mapped_row.get(Global.ROW)] = mapped_row
        return (row_map, max_rows, max_cols)

    def __calc_panel_size(self, max_rows, max_cols):
        """ calc the size of the window based on rows, cols """
        # print(">>> max row,col: " + str(max_rows) + " : " + str(max_cols))
        blank_image = self.parent_page.layout_images[Global.BLOCK][Global.UNKNOWN][Global.BLANK]
        panel_width = max_cols * (blank_image.width() + 4)
        panel_height = max_rows * (blank_image.height() + 4)
        return (panel_width, panel_height)


    def __process_a_switch_change(self, message):
        """ a single switch has changed state """
        skey = message.msg_data.port_id
        for panel_switch in self.switches:
            pkey = panel_switch.key
            panel_item = None
            group = Global.SWITCH
            stype = None
            if skey == pkey:
                panel_switch.state = Global.UNKNOWN
                if Synonyms.is_on(name=message.msg_data.mode):
                    panel_switch.state = Global.THROWN
                if Synonyms.is_off(name=message.msg_data.mode):
                    panel_switch.state = Global.CLOSED
                stype = panel_switch.type
                # print(">>> switch state:" + str(group)+":"+str(state)+":"+str(type))
                new_panel_image = self.parent_page.layout_images[group][panel_switch.state][stype]
                panel_item = panel_switch.button
                if panel_item is not None:
                    panel_item.replace_image(image=new_panel_image)

    def __process_a_signal_change(self, message):
        """ a single signal has changed state """
        skey = message.msg_data.port_id
        for panel_signal in self.signals:
            pkey = panel_signal.key
            panel_item = None
            group = Global.SIGNAL
            stype = None
            # print(">>> key: "+str(skey)+" : "+str(pkey))
            if skey == pkey:
                _state = Global.UNKNOWN
                if message.msg_data.mode in [Global.APPROACH, Global.CLEAR, Global.STOP]:
                    panel_signal.state = message.msg_data.mode
                stype = panel_signal.type
                # print(">>> signal state:" + str(group)+":"+str(panel_signal.state)+":"+str(type))
                new_panel_image = self.parent_page.layout_images[group][panel_signal.state][stype]
                panel_item = panel_signal.button
                if panel_item is not None:
                    panel_item.replace_image(image=new_panel_image)
                    # print(">>>  ... replace signal image")

    def __process_a_route_change(self, message):
        """ a single route has changed state """
        skey = message.msg_data.port_id
        for panel_route in self.routes:
            pkey = panel_route.key
            panel_item = None
            group = Global.ROUTE
            stype = None
            if skey == pkey:
                panel_route.state = Global.UNKNOWN
                if Synonyms.is_on(name=message.msg_data.mode):
                    panel_route.state = Global.ON
                if Synonyms.is_off(name=message.msg_data.mode):
                    panel_route.state = Global.OFF
                stype = panel_route.type
                # print(">>> route state: " + str(group)+" : "+str(panel_route.state)+" : "+str(stype))
                new_panel_image = self.parent_page.layout_images[group][panel_route.state][stype]
                panel_item = panel_route.button
                if panel_item is not None:
                    panel_item.replace_image(image=new_panel_image)

    def __process_a_block_change(self, message):
        """ a single block has changed state """
        skey = message.msg_data.block_id
        for panel_block in self.blocks:
            pkey = panel_block.key
            panel_item = None
            group = Global.BLOCK
            _state = Global.UNKNOWN
            btype = None
            # print(">>> block key: " + str(skey) + " ... " + str(pkey))
            if skey == pkey:
                panel_block.state = Global.UNKNOWN
                if message.msg_data.mode in [Global.OCCUPIED, Global.CLEAR]:
                    panel_block.state = message.msg_data.mode
                btype = panel_block.type
                new_panel_image = self.parent_page.layout_images[group][panel_block.state][btype]
                panel_item = panel_block.button
                if panel_item is not None:
                    panel_item.replace_image(image=new_panel_image)

    def __process_a_locator_change(self, message):
        """ a single locator has changed state """
        # an update of a loco location
        # set the loco in the new block and remove from prev block
        # print(">>> locator: "+str(message))
        skey = message.msg_data.block_id
        text = message.msg_data.dcc_id
        if text is not None and \
                isinstance(text, list) and \
                len(text) > 0:
            text = text[0]
        # print(">>> loco: "+str(text))
        for panel_locator in self.locators:
            panel_item = panel_locator.button
            if panel_item is not None:
                pkey = panel_locator.key
                if skey == pkey:
                    # set loco in new block
                    if message.msg_data.mode == Global.EXITED:
                        panel_locator.state = ""
                    else:
                        panel_locator.state = text
                    panel_item.configure(text=panel_locator.state)
                else:
                    if message.msg_data.mode == Global.ENTERED:
                        # remove loco from old block since loco is now in a new block
                        if panel_locator.state == text:
                            panel_locator.state = ""
                            panel_item.configure(text=panel_locator.state)
