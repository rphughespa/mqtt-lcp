#!/usr/bin/python3
# locos_notebook.py

"""

LocosNotebook - Locos notebook screen

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

#import os
#import json

# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../../lib')

# from utils.global_constants import Global

from components.local_constants import Local

# from image_button import ImageButton
# from panel_page import PanelPage
from components.locos_available_page import LocosAvailablePage
from components.locos_selected_page import LocosSelectedPage
from components.locos_keypad_page import LocosKeypadPage


class LocosNotebook(ttk.Frame):
    """ panel notbook screen """

    def __init__(self, parent, parent_node, parent_cab, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.grid_propagate(0)
        self.parent = parent
        self.parent_node = parent_node
        self.parent_cab = parent_cab
        #self.panels = []
        #self.label = ttk.Label(self, text=Local.PANELS, style="My.TLabel")
        #self.label.grid(row=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='NESW')
        self.notebook.configure(style="Center.TNotebook")
        self.locos_selected_page = LocosSelectedPage(self.notebook, \
                self.parent_node, self.parent_cab, padding=(2, 2, 2, 2),
                borderwidth=1, relief="flat",
                style="My.TFrame")
        self.notebook.add(self.locos_selected_page, text=' '+Local.ACQUIRED.title()+' ')
        self.locos_available_page = LocosAvailablePage(self.notebook, self.parent_node, \
                self.parent_cab, padding=(2, 2, 2, 2),
                borderwidth=1, relief="flat",
                style="My.TFrame")
        self.notebook.add(self.locos_available_page, text=' '+Local.ROSTER.title()+' ')
        self.locos_keypad_page = LocosKeypadPage(self.notebook, self.parent_node, self.parent_cab, padding=(2, 2, 2, 2),
                borderwidth=1, relief="flat",
                style="My.TFrame")
        self.notebook.add(self.locos_keypad_page, text=' '+Local.KEYPAD.title()+' ')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)


    def refresh_page(self):
        """ refresh page display """
        self.locos_selected_page.refresh_page()
        self.locos_available_page.refresh_page()
        self.locos_keypad_page.refresh_page()

    def process_output_message(self, message):
        """ process output message """
        self.locos_selected_page.process_output_message(message)
        self.locos_available_page.process_output_message(message)
        self.locos_keypad_page.process_output_message(message)
