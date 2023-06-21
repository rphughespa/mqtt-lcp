#!/usr/bin/python3
# scrollable_info_list.py

"""

ScrollableInfoLIst - Scrollabel Info List screen

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


# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../../lib')

# from utils.global_constants import Global

# from image_box import ImageBox
from components.local_constants import Local
from components.info_box import InfoBox

class ScrollableInfoList(ttk.Frame):
    """ scrollable infor list """

    def __init__(self, parent, info_dict, width=330, height=220, row_height=24, callback=None, **kwargs):
        """ initialize """
        # info_dict must have a "id" value and and a "description" value foreach item

        super().__init__(parent, **kwargs)
        self.parent = parent
        self.info_dict = None
        self.info_boxes = {}
        self.width = width
        self.row_height = row_height
        self.callback = callback
        # self.pack_propagate(False)
        self.canvas = ttk.Canvas(
            self, width=width, height=height, bg=Local.DEFAULT_BG)
        self.frame = ttk.Frame(self.canvas)
        self.vsb = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw",
                                  tags="self.frame")
        self.frame.bind("<Configure>", self.onFrameConfigure)
        if info_dict is not None:
            self.populate(info_dict)

    def populate(self, info_dict):
        """ populate list """
        self.info_dict = info_dict
        self.info_boxes = {}
        for child in self.frame.winfo_children():
            child.destroy()
        r = 0
        for key, value in info_dict.items():
            info_box = self.format_info_box(key, value)
            info_box.grid(row=r, pady=2)
            seq = None
            if hasattr(value, "sequence"):
                seq = value.sequence
            if seq is None:
                seq = 0
            self.info_boxes[seq] = info_box
            r += 1

    def format_info_box(self, key, value):
        """ format info box """
        info_box = InfoBox(self.frame, key, title=key,
                           value=value.description, name=value.name,
                           callback=self.callback, width=self.width-4)
        return info_box

    def onFrameConfigure(self, _event):
        """ frame configure selected"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
