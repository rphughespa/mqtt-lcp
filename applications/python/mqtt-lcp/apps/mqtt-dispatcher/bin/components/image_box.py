#!/usr/bin/python3
# image_box.py
"""

ImageBox - Info Box screen

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
from components.image_clickable import ImageClickable

IMAGE_WIDTH = 16
IMAGE_HEIGHT = 16

class ImageBox(ttk.Frame):
    """ info box """

    def __init__(self, parent, key, title=None, description=None, image=None, callback=None,
            width=120, height=24, _anchor='w'):
        """ initialize """

        super().__init__(parent, width=width, height=height)
        self.parent = parent
        self.width = width
        self.key = key
        self.title = title
        self.description = description
        self.value = None
        self.callback = callback
        self.configure(style="InfoBox.TFrame")
        self.padding=(2,2,2,2)
        self.grid_propagate(0)
        # base_row = 0
        if description is None:
            self.title_label = ttk.Label(self, text=self.title, anchor='w')
            self.title_label.grid(row=0, column=0, padx=2, pady=2, sticky="w")
            self.title_label.configure(style="InfoTitle.TLabel")
            self.value_button = ImageClickable(self, height=IMAGE_HEIGHT, width=IMAGE_WIDTH, image=image)
            self.value_button.grid(row=0, column=1, padx=8, pady=0, sticky="e")
            if self.callback is not None:
                self.title_label.bind('<Button-1>', self.on_click)
                self.value_button.bind('<Button-1>', self.on_click)

        else:
            self.value_button = ImageClickable(self, height=40, width=190,
                image=image, command=self.on_click, command_value='<Button-1>')
            self.value_button.grid(row=0, column=0, padx=4, pady=2, sticky=(NW))

            self.title_label = ttk.Label(self, text=self.title, width=12, anchor='w')
            self.title_label.grid(row=1, column=0,padx=4, stick=(SW))
            self.title_label.configure(style="Medium.TLabel")

            self.desc_label = ttk.Label(self, text=self.description, width=42, anchor='w')
            self.desc_label.grid(row=2, column=0, padx=4, stick=(SW))
            self.desc_label.configure(style="InfoValue.TLabel")
            if self.callback is not None:
                self.title_label.bind('<Button-1>', self.on_click)
                self.desc_label.bind('<Button-1>', self.on_click)

    def on_click(self, _info):
        """ info was clcked """
        self.callback(self.key)
