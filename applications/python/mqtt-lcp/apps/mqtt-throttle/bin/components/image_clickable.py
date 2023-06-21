#!/usr/bin/python3
# image_clickable.py

"""

ImageButton - A flat, clickable image canvas type button

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

import os


# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from PIL import Image, ImageTk

sys.path.append('../../lib')
from components.local_constants import Local

# from utils.global_constants import Global


class ImageClickable(ttk.Frame):
    """ image button """

    def __init__(self, parent, height=None, width=None,
                 image_file=None,  image=None, image_height=None, image_width=None,
                 _text=None,
                 command=None, command_value=None, bg=None,
                 padding=(1, 1, 1, 1), style="outline"):
        """ initialize """
        self.parent = parent
        self.image_file = image_file
        self.image = image
        self.height = height
        self.width = width
        self.padding = padding
        self.style = style
        self.image_height = image_height
        self.image_width = image_width
        if self.image_height is None and self.image is not None:
            self.image_height = self.image.height()
        if self.image_width is None and self.image is not None:
            self.image_width = self.image.width()
        if self.image_height is None:
            self.image_height = self.height
        if self.image_width is None:
            self.image_width = self.width
        self.relief = "flat"
        if self.style == "outline":
            self.refief = "raised"
        super().__init__(parent, height=height, width=width,
                         padding=self.padding, relief=self.relief, borderwidth=-2)
        # , borderwidth=self.borderwidth, relief=self.relief)
        self.command = command
        self.command_value = command_value
        self.cavnvas = None
        self.button = None
        self.state = None
        self.bg = bg
        if self.bg is None:
            self.bg = Local.DEFAULT_BG
        if (self.image is None) and (self.image_file is not None):
            self.image = ImageClickable.load_image(self.image_file, height=self.image_height,
                                                   width=self.image_width)
        self.pack_propagate(0)
        self.build_button()
        self.canvas_image = None

    def build_button(self):
        """ build the button """
        self.canvas = ttk.Canvas(self, width=self.width, height=self.height,
                                 bg=self.bg, highlightthickness=0)
        self.canvas.pack()
        self.canvas_image = self.canvas.create_image(
            0, 0, image=self.image, anchor=NW)
        self.canvas.bind('<Button-1>', self.on_canvas_clicked)

    def set_disabled(self):
        """ set button to disabled """
        self.button.configure(state="disabled")

    def set_normal(self):
        """ set the button to normal """
        self.button.configure(state="normal")

    def on_button_clicked(self, state=None):
        """ button has been clicked """
        rett = state
        if rett is None:
            rett = self.state
        if self.command is not None:
            if self.command_value is not None and rett is not None:
                self.command(self.command_value, rett)
            elif self.command_value is not None:
                self.command(self.command_value)
            else:
                self.command(rett)

    def on_canvas_clicked(self, _event):
        """ canvas clicked """
        self.on_button_clicked()

    def replace_image(self, image=None, image_file=""):
        """ replace image """
        self.image = image
        self.image_file = image_file
        if self.image is None:
            self.image = ImageClickable.load_image(
                self.image_file, height=self.height, width=self.width)
        self.canvas.delete(self.canvas_image)
        self.canvas_image = self.canvas.create_image(
            0, 0, image=self.image, anchor=NW)

    @classmethod
    def load_image(cls, image_file_name, height=None, width=None, rotate_angle=None):
        """ class level method to load an image """
        photo_image = None
        image_file_path = os.getcwd()+"/"+image_file_name
        # print(">>> ### load image path: "+str(image_file_path))
        if os.path.exists(image_file_path):
            image = Image.open(image_file_path)
            if height is not None and width is not None:
                # print(">>> image resize: " + str(image_file_name)+" : "+str(height)+" : "+str(width))
                image = image.resize((width, height), Image.ANTIALIAS)
            if rotate_angle is not None:
                photo_image = ImageTk.PhotoImage(image.rotate(rotate_angle))
            else:
                photo_image = ImageTk.PhotoImage(image)
        else:
            print("!!! Error: Image file not found: " + image_file_path)
        return photo_image
