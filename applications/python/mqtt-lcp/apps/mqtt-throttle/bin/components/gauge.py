#!/usr/bin/python3
# gauge.py

"""

Guage - Guage screen

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


#from utils.global_constants import Global
from components.local_constants import Local

from components.image_clickable import ImageClickable

class Gauge(ttk.Frame):
    """ guage
    This class displays a gauge back ground image and a separtae needle image
    The needle image will be rotated around center point n the background and on the needle.
    """

    def __init__(self, parent, max_value=100, max_rotation=180,
                gauge_height=None, gauge_width=None, gauge_image_file="",
                needle_height=None, needle_width=None, needle_image_file="",
                bg=None):
        """ initialize """
        super().__init__(parent, height=gauge_height, width=gauge_width, style="ImageButton.TFrame")
        self.parent = parent
        self.max_value = max_value
        self.max_rotation = max_rotation
        self.gauge_height = gauge_height
        self.gauge_width = gauge_width
        self.needle_height = needle_height
        self.needle_width = needle_width
        self.gauge_image_file = gauge_image_file
        self.needle_image_file = needle_image_file
        self.bg = bg
        if self.bg is None:
            self.bg = Local.DEFAULT_BG
        self.gauge_image = ImageClickable.load_image(self.gauge_image_file,
                height=self.gauge_height, width=self.gauge_width)
        self.needle_image = ImageClickable.load_image(self.needle_image_file,
                height=self.needle_height, width=self.needle_width)
        self.configure(style="Black.TFrame")
        self.canvas = ttk.Canvas(self, width=self.gauge_width,
                height=self.gauge_height, bg=self.bg, highlightthickness=0)
        self.canvas.pack()
        self.canvas_gauge_image = self.canvas.create_image(0, 0, image=self.gauge_image, anchor=NW)
        self.needle_x = (self.gauge_width - self.needle_width) / 2
        self.needle_y = (self.gauge_height - self.needle_height) / 2
        self.canvas_needle_image = None
        self.canvas_value_text = None
        self.set_value(0)

    def set_value(self, new_value):
        """image rotate method does positive rotation clockwise from 12 o'clock(straight up),
            negatine rotation is counter clockwise from 12 o'clock """

        half_rotation = self.max_rotation / 2
        percent_value = new_value / self.max_value
        new_angle = self.max_rotation * percent_value
        if new_angle > half_rotation:
            new_angle = new_angle - half_rotation
        else:
            new_angle = 0 - half_rotation + new_angle
        self.needle_image = ImageClickable.load_image(self.needle_image_file,
                height=self.needle_height, width=self.needle_width, rotate_angle=0-new_angle)
        if self.canvas_value_text is not None:
            self.canvas.delete(self.canvas_value_text)
        if self.canvas_needle_image is not None:
            self.canvas.delete(self.canvas_needle_image)
        self.canvas_needle_image = self.canvas.create_image(self.needle_x,
                self.needle_y, image=self.needle_image, anchor=NW)
        self.canvas_value_text = self.canvas.create_text(self.gauge_width/2,
                self.gauge_height-20, text=str(int(new_value + 0.5)), fill=self.bg)
