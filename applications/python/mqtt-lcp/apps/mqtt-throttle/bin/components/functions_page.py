#!/usr/bin/python3
# functions_page.py

"""

FunctionsPage - functions screen

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

#import json


# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../../lib')

# from utils.global_constants import Global

from components.functions_pad import FunctionsPad

class FunctionsPage(ttk.Frame):
    """ Functions Screen """

    def __init__(self, parent, parent_node, parent_cab, **kwargs):
        """ Initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_node = parent_node
        self.parent_cab = parent_cab

        self.functions = FunctionsPad(self, self.parent_cab, callback=self.on_keypad_clicked)
        self.functions.grid(row=0, column=0)

    def on_keypad_clicked(self, key_number, state):
        """ keypad has been clicked """
        # print("Clicked: "+str(key_number) + " : " + str(state))
        self.parent_cab.set_function_state(key_number, state)
        self.parent_cab.publish_function_request(key_number)
        self.parent_cab.refresh_all_pages()

    def refresh_page(self):
        """ refesh this page """
        self.functions.refresh_page()
