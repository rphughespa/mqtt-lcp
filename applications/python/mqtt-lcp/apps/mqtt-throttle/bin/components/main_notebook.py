#!/usr/bin/python3
# main_notebook.py

"""

MainNotebook - Main notebook screen

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

from utils.global_constants import Global

from components.cabs_frame import CabsFrame
from components.tower_notebook import TowerNotebook

class MainNotebook(ttk.Frame):
    """ Main notebok screen """

    def __init__(self, parent, parent_node, **kwargs):
        """ Initialize """

        super().__init__(parent, **kwargs)
        self.parent = parent
        # self.grid_propagate(False)
        self.parent_node = parent_node
        self.notebook = ttk.Notebook(self) #,style='My.R.Notebook')
        self.notebook.grid(row=0, column=0, sticky='NESW')
        self.notebook.configure(style="Right.TNotebook")
        width = 380 # width of cab (a, b) window
        height = 340
        if self.parent_node.screensize == Global.SMALL:
            width = 310
            height = 230
        self.cabs_frame = CabsFrame(self.notebook, self.parent_node, padding=(2, 2, 2, 2),
                    borderwidth=1, relief="flat",
                    width=width*2, height=height, style="My.TFrame")
        self.cabs_frame.grid_propagate(False)
        self.tower_notebook = TowerNotebook(self.notebook, self.parent_node, padding=(2, 2, 2, 2),
                    borderwidth=1, relief="flat",
                    width=width*2, height=height, style="My.TFrame")
        self.tower_notebook.grid_propagate(False)
        self.notebook.add(self.cabs_frame, text=' '+Global.CAB.title()+' ') #, state="hidden")
        self.notebook.add(self.tower_notebook, text=' '+Global.TOWER.title()+' ') #, state="hidden")
        # for i in self.notebook.tabs():
            # print("Tab: " + str(i))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

    def process_output_message(self, message):
        """ process output message """
        self.cabs_frame.process_output_message(message)
        self.tower_notebook.process_output_message(message)
