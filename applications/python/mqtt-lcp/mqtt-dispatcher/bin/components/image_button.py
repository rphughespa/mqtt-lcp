#!/usr/bin/python3
# image_button.py

"""

ImageButton - Image Button

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
# import os


# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# from PIL import Image, ImageTk

sys.path.append('../../lib')

# from utils.global_constants import Global
# from components.local_constants import Local
from components.image_clickable import ImageClickable

class ImageButton(ImageClickable):
    """ image button """

    def __init__(self, parent, height=None, width=None,
                image_file=None,  image=None, image_height=None, image_width=None,
                text=None,  compound=None,
                command=None, command_value=None, bg=None,
                padding=(1,1,1,1), style="outline"):
        """ initialize """

        self.text = text
        self.padding=padding
        self.style=style
        self.image_file = None
        self.image = None
        self.compound = compound
        self.button = None
        super().__init__(parent, height=height, width=width,
                image_file=image_file,  image=image, image_height=image_height, image_width=image_width,
                command=command, command_value=command_value, bg=bg,
                padding=padding, style=self.style)

    def build_button(self):
        """ build the button """
        self.button = ttk.Button(self, text=self.text, \
                image=self.image, compound=self.compound,
                bootstyle=self.style,
                padding=self.padding,
                command=self.on_button_clicked)
        self.button.pack(fill=BOTH, expand=1)

    def replace_image(self, image=None, image_file=""):
        """ replave button image """
        self.image = image
        self.image_file = image_file
        if self.image is None:
            self.image = ImageClickable.load_image(self.image_file, \
                height=self.image_height, width=self.image_width)
        self.button.configure(image=self.image)

    def on_button_clicked(self):
        """ nutton has been clicked """
        super().on_button_clicked()
        pass
