#!/usr/bin/python3
# info_box.py
"""

InfoBox - Info Box screen

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

class InfoBox(ttk.Frame):
    """ info box """

    def __init__(self, parent, key, name=None, title=None, value=None, callback=None,
            width=130, height=48, _anchor='w'):
        """ initialize """

        super().__init__(parent,width=width,height=height)
        self.parent = parent
        self.width = width
        self.key = key
        self.title = title
        self.name = name
        self.value = None
        self.callback = callback
        self.grid_propagate(0)
        self.title_label = ttk.Label(self, text=self.title, anchor='w')
        self.title_label.grid(row=0, column=0, padx=2, pady=2, sticky="w")
        self.value_label = ttk.Label(self, text="", anchor='w',font=(16))
        self.value_label.grid(row=1, column=0, padx=12, pady=0, sticky="w")
        self.set_value(value)
        if self.callback is not None:
            self.title_label.bind('<Button-1>', self.on_click)
            self.value_label.bind('<Button-1>', self.on_click)

    def set_value(self, new_value):
        """ set info value """
        self.value= ""
        if new_value is not None and new_value != "":
            substr = 32
            if self.width < 161:
                substr = 20
            if self.width < 121:
                substr = 9
            self.value = new_value[:substr]
        self.value_label.config(text="  "+str(self.value))

    def on_click(self, _info):
        """ info was clcked """
        self.callback(self.key)
