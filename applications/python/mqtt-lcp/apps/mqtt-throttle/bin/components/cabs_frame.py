#!/usr/bin/python3
#cabs_frame.py

"""

CabsFrame - Cabs frame screem

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

# #import os
import sys

# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
sys.path.append('../../lib')

from utils.global_constants import Global
from components.local_constants import Local

# from components.image_clickable import ImageClickable
from components.cab_notebook import CabNotebook

class CabsFrame(ttk.Frame):
    """ cabs frame screen """

    def __init__(self, parent, parent_node, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_node = parent_node
        self.cab_frame_a = None
        self.cab_frame_b = None
        self.cab_frame_a = CabNotebook(self, self.parent_node, Global.CAB_A,
                        padding=(2, 2, 2, 2),
                        borderwidth=5, relief="flat")
        self.cab_frame_a.grid(row=0, column=0, sticky=(NW))
        self.columnconfigure(0, weight=1)
        if self.parent_node.screensize != Global.SMALL:
            self.cab_frame_b = CabNotebook(self, self.parent_node, Global.CAB_B,
                            padding=(2, 2, 2, 2),
                            borderwidth=5, relief="flat")
            self.cab_frame_b.grid(row=0, column=1, sticky=(NW))
            self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)


    def process_output_message(self, message):
        """ process output message """
        if ((message.cab == Global.CAB_ALL) and
                (message.msg_type == Global.ROSTER)):
            #if self.locos_images is None:
            #    self.load_locos_images()
            #self.load_roster_images(message)
            pass
        if message.cab in [Global.CAB_A, Global.CAB_ALL]:
            self.cab_frame_a.process_output_message(message)
        if self.cab_frame_b is not None:
            if message.cab in [Global.CAB_B, Global.CAB_ALL]:
                self.cab_frame_b.process_output_message(message)
