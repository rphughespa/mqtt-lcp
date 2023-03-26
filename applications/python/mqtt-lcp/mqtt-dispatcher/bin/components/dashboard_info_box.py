#!/usr/bin/python3
# dashboard_info_box.py
"""

DashboardInfoBox - Dashboard Info Box screen

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


# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../../lib')

# from utils.global_constants import Global

# from image_button import ImageButton
# from components.image_clickable import ImageClickable


class DashboardInfoBox(ttk.Frame):
    """ info box """

    def __init__(self, parent, key, title=None, name=None, description=None, image=None,
                 callback=None,
                 width=240, height=24, _anchor='w', image_width=None, image_height=None):
        """ initialize """

        super().__init__(parent,
                         width=width,
                         height=height,
                         relief="raised",
                         padding=(2, 2, 2, 2)
                         )
        self.parent = parent
        self.width = width
        self.height = height
        self.image = image
        self.image_height = image_height
        if self.image_height is None and self.image is not None:
            self.image_height = self.image.height()
        self.image_width = image_width
        if self.image_width is None and self.image is not None:
            self.image_width = self.image.width()
        self.key = key
        self.title = title
        self.name = name
        self.description = description
        self.value = None
        self.callback = callback

        self.state_label = ttk.Label(self, image=self.image, width=24)
        self.state_label.grid(row=0, column=0, padx=4, sticky=(NW))

        self.title_label = ttk.Label(self, text=self.title, width=26)
        self.title_label.grid(row=0, column=1, padx=4, sticky=(SW))

        self.name_label = ttk.Label(self, text=self.name, width=38, anchor='w')
        self.name_label.grid(
            row=1, column=0, columnspan=2, padx=4, sticky=(SW))

        self.title_label.bind('<Button-1>', self.on_click)
        self.name_label.bind('<Button-1>', self.on_click)

    def on_click(self, _info):
        """ info was clcked """
        if self.callback is not None:
            self.callback(self.key)
