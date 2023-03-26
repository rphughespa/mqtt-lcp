#!/usr/bin/python3
# panels_notebook.py

"""

PanelsNotebook - Panel notebook screen

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

import os
import sys
# import copy

# import tkinter as tk
# from tkinter import messagebox
import ttkbootstrap as ttk

from ttkbootstrap.constants import *

sys.path.append('../../lib')

# from structs.gui_message import GuiMessage
from utils.global_constants import Global

from components.image_clickable import ImageClickable
from components.panel_page import PanelPage
# from components.tk_message import TkMessage
# from components.local_constants import Local



# from image_button import ImageButton


IMAGE_WIDTH = 48 # 64
IMAGE_HEIGHT = 24 # 32


class PanelsNotebook(ttk.Frame):
    """ panel notbook screen """

    def __init__(self, parent, parent_node, tower_data, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_node = parent_node
        self.tower_data = tower_data
        self.layout_images = {}
        self.panels = []
        self.label = ttk.Label(self, text=Global.PANELS, style="My.TLabel")
        self.label.grid(row=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='NESW')
        self.notebook.configure(style="Center.TNotebook")

        self.__load_all_images()
        # self.load_layout_pages()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

    def on_item_clicked(self, ident, _rett):
        """ item clicked"""
        print("Layout Clicked: "+str(ident))

    def process_output_message(self, message):
        """ process output messafe """
        if message.msg_type == Global.PANELS:
            # print(">>> panels: " + str(message.msg_data))
            for panel in self.panels:
                self.notebook.forget(panel)
            self.panels = []
            for _key, panel in message.msg_data.panels.items():
                name = str(panel.name)
                # description = str(panel.description)
                new_page = PanelPage(self, self.notebook, self.parent_node, \
                                    self.tower_data, self.layout_images, name, panel.rows,
                                     callback=self.on_item_clicked, \
                                     padding=(
                                         0, 0, 0, 0),
                                     borderwidth=1, relief="flat",
                                     style="My.TFrame")
                self.notebook.add(new_page, text=" "+name+" ")
                self.panels.append(new_page)
        for page in self.panels:
            page.process_output_message(message)

    #
    # local functions
    #

    def __load_all_images(self):
        """ load images info application """
        image_path = None
        signal_type = "color"
        if "options" in self.parent_node.config[Global.CONFIG]:
            if Global.SIGNAL + "-" + Global.TYPE in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                signal_type = self.parent_node.config[Global.CONFIG][
                    Global.OPTIONS][Global.SIGNAL + "-" + Global.TYPE]
            if Global.IMAGE + "-" + Global.PATH in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                image_path = self.parent_node.config[Global.CONFIG][Global.OPTIONS][Global.IMAGE + "-" + Global.PATH]

        if image_path is not None:

            block_image_path = image_path + "/" + Global.PANEL + "/" + Global.BLOCK
            self.layout_images[Global.BLOCK] = self.__load_group_state_images(
                block_image_path)

            switch_image_path = image_path + "/" + Global.PANEL + "/" + Global.SWITCH
            self.layout_images[Global.SWITCH] = self.__load_group_state_images(
                switch_image_path)

            signal_image_path = image_path + "/" + Global.PANEL + \
                "/" + Global.SIGNAL + "/" + signal_type
            self.layout_images[Global.SIGNAL] = self.__load_group_state_images(
                signal_image_path)

    def __load_group_state_images(self, group_folder_path):
        """ load a number of images assoiated by state for a group """
        group_images = {}
        # print(">>> group state: " + str(group_folder_path))
        for state_folder in os.listdir(group_folder_path):
            #print(">>> state folder: " + str(state_folder))
            state_folder_path = group_folder_path + "/" + state_folder
            #print(">>> state folder path: "+str(state_folder_path))
            if os.path.isdir(state_folder_path):
                state_images = {}
                for image_name in os.listdir(state_folder_path):
                    image_path = state_folder_path + "/" + image_name
                    #print(">>> image name: "+str(image_path))
                    if os.path.isfile(image_path):
                        file_image = self.__load_one_image(image_path)
                        # get filename without extension
                        file_root = image_name.split(".")[0]
                        state_images[file_root] = file_image
                        # print(">>> images: " + str(state_folder) +
                        #      " : "+str(file_root))
                group_images[state_folder] = state_images
        return group_images

    def __load_one_image(self, image_file_name):
        """ load one image """
        return ImageClickable.load_image(image_file_name, height=IMAGE_HEIGHT, width=IMAGE_WIDTH)
