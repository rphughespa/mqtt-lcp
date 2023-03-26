#!/usr/bin/python3
#functions_pad.py

"""

FunctionsPad - Function pad screen

the MIT License (MIT)

Copyright © 2021 richard p hughes

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
# from PIL import Image, ImageTk

sys.path.append('../../lib')

#from utils.global_constants import Global
from components.local_constants import Local
# from components.image_button import ImageButton
from components.image_toggle_button import ImageToggleButton


class FunctionsPadFrame(ttk.Frame):
    """ function pad frame """

    def __init__(self, parent, parent_cab, callback=None, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_cab = parent_cab
        self.callback = callback
        self.function_pad = FunctionsPad(self, self.parent_cab, self.callback)
        self.function_pad.grid(row=0)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

#    def set_key_number(self, value):
#        """ set key number """
#        self.ids.key_number.text = value

#    def get_key_number(self):
#        """ get keu number """
#        return self.ids.key_number.text

#    def set_key_number_description(self, value):
#        """ set key description """
#        print("Value: "+ value)


class FunctionsPad(ttk.Frame):
    """ function pad """

    def __init__(self, parent,parent_cab, callback, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_cab = parent_cab
        self.callback = callback
        # self.grid_propagate(0)
        self.cols = 4
        self.spacing = 10
        self.num_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, \
                14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
        self.buttons = []
        self.create_buttons()

    def on_clicked(self, num, state):
        """ key clicked """
        if self.callback is not None:
            self.callback(str(num), state)

    def create_buttons(self):
        """ create buttons """
        kcol = 0
        krow = 0
        for num in self.num_list:
            if num == 0:
                button = ImageToggleButton(self, width=60, height=36, \
                        text=' '+Local.LIGHT.title(),
                        compound=LEFT, image_width=26, image_height=26,
                        image_file="img/buttons/lightbulb.png", \
                        on_image_file="img/buttons/lightbulb-yellow.png",
                        command=self.on_clicked, command_value=str(num))
            elif num == 1:
                button = ImageToggleButton(self, width=60, height=36, \
                        text=' '+Local.BELL.title(),
                        compound=LEFT, image_width=26, image_height=26,\
                        image_file="img/buttons/bell.png", \
                        on_image_file="img/buttons/bell-on.png", \
                        command=self.on_clicked, command_value=str(num))
            elif num == 2:
                button = ImageToggleButton(self, width=60, height=36, \
                        text=' '+Local.HORN.title(),
                         compound=LEFT, image_width=26, image_height=26, \
                        image_file="img/buttons/horn.png", \
                        on_image_file="img/buttons/horn-on.png", \
                        command=self.on_clicked, command_value=str(num))
            else:
                button = ImageToggleButton(self, text=str(num), width=70, height=36,
                        command=self.on_clicked, command_value=str(num))
            self.buttons.append(button)
            button.grid(column=kcol, row=krow, sticky=(E, W, N, S))
            kcol += 1
            if kcol > 3:
                kcol = 0
                krow += 1

    def refresh_page(self):
        """ refresh the page diplay """
        for num in self.num_list:
            func_state = self.parent_cab.get_function_state(num)
            self.buttons[num].set_state(func_state)
        if self.parent_cab.any_locos_selected():
            for button in self.buttons:
                button.set_normal()
        else:
            for button in self.buttons:
                button.set_disabled()
