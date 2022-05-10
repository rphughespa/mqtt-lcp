# title_frame.py

"""

TitleFrame- Title frame screen

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

# from utils.global_constants import Global

# from image_button import ImageButton
from components.image_clickable import ImageClickable

class TitleFrame(ttk.Frame):
    """ title frame """

    def __init__(self, parent, parent_node, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_node = parent_node
        self.menu_button = ImageClickable(self, height=24, width=24, command=self.on_gear_clicked,
                image_file="img/buttons/button_gear.png")
        self.label = ttk.Label(self, text="Title", anchor=CENTER, style="My.TLabel")
        self.exit_button = ImageClickable(self, height=24, width=24, command=self.on_exit_clicked,
                image_file="img/buttons/button_exit.png")
        self.grid_columnconfigure(1, weight=1)
        self.menu_button.grid(column=0, row=0, stick=(NW))
        self.label.grid(column=1, row=0, stick=(NW))
        self.exit_button.grid(column=2, row=0, stick=(NW))

    def on_gear_clicked(self):
        """ gear clicked """
        print("Gear clicked")

    def process_output_message(self, message):
        """ process output message """
        pass

    def on_exit_clicked(self):
        """ exit clicked """
        print("Exit clicked")
        self.parent.on_closing()
