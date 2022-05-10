# tower_notebook.py

"""

TowerNotebook - Tower notebook screen

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

sys.path.append('../../lib')

# from utils.global_constants import Global
from components.local_constants import Local
from components.system_page import SystemPage
from components.switches_page import SwitchesPage
# from components.panels_notebook import PanelsNotebook

class TowerNotebook(ttk.Frame):
    """ tower notebook screen """

    def __init__(self, parent, parent_node, **kwargs):
        """ initailize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_node = parent_node
        self.notebook = ttk.Notebook(self) #, style='MyL.Notebook')
        self.notebook.grid(row=0, column=0, sticky='NESW')
        self.notebook.configure(style="Left.TNotebook")

        self.switches_page = SwitchesPage(self.notebook, parent_node, padding=(2, 2, 2, 2),
                borderwidth=1, relief="flat", style="My.TFrame")
        self.notebook.add(self.switches_page, text=' '+Local.SWITCHES.title()+' ')

        #self.panels_notebook = PanelsNotebook(self.notebook, parent_node, padding=(2, 2, 2, 2),
        #        borderwidth=1, relief="flat", style="My.TFrame")
        #self.notebook.add(self.panels_notebook, text=' '+Local.PANELS.title()+' ')

        self.system_page = SystemPage(self.notebook, self.parent_node,
                padding=(2, 2, 2, 2), borderwidth=1, relief="flat",
                width=340, height=360, style="My.TFrame")
        self.notebook.add(self.system_page, text=' '+Local.SYSTEM.title()+' ')


        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

    def process_output_message(self, message):
        """ process output message"""
        self.switches_page.process_output_message(message)
        # self.panels_notebook.process_output_message(message)
        self.system_page.process_output_message(message)
