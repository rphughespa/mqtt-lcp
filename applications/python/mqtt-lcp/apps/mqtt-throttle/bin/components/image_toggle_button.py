#!/usr/bin/python3
# image_toggle_button.py

"""

ImageToggleButton - Image Button tahe taggle from on to off etc

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
#import os
#import tkinter as tk
# import tkinter.ttk as ttk
#from PIL import Image, ImageTk

sys.path.append('../../lib')

from utils.global_constants import Global
# from components.local_constants import Local
from components.image_button import ImageButton
# from image_clickable import ImageClickable

class ImageToggleButton(ImageButton):
    """ image button """

    def __init__(self, parent, height=None, width=None,
                image_file=None,  image=None, image_height=None, image_width=None,
                text=None, compound=None,
                command=None, command_value=None, bg=None,
                on_image=None, on_image_file=None,
                style="outline"):
        """ initialize """

        self.state = Global.OFF
        self.on_image = on_image
        self.on_image_file = on_image_file
        self.off_image = image
        self.off_image_file = image_file
        self.style=style
        super().__init__(parent, height=height, width=width,
                image_file=image_file,  image=image, image_height=image_height,\
                image_width=image_width,style=self.style,
                command=command, command_value=command_value, bg=bg, \
                text=text, compound=compound)

        if (self.off_image is None) and (self.off_image_file is not None):
            height=self.image_height
            width=self.image_width
        if (self.on_image is None) and (self.on_image_file is not None):
            height=self.image_height
            width=self.image_width
        self.set_state(self.state)

    def set_state(self, new_state):
        """ set state """
        if new_state == Global.ON:
            # print(">>> button on")
            self.button.state(['pressed'])
            self.state = new_state
            if self.on_image_file is not None:
                self.replace_image(image=self.on_image, image_file=self.on_image_file)
        elif new_state == Global.OFF:
            # print(">>> button off")
            self.button.state(['!pressed'])
            self.state = new_state
            if self.off_image_file is not None:
                self.replace_image(image=self.off_image, image_file=self.off_image_file)

    def on_button_clicked(self):
        """ button has been clicked """
        if self.state == Global.ON:
            self.set_state(Global.OFF)
        else:
            self.set_state(Global.ON)
        super().on_button_clicked()
