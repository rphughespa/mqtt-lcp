#!/usr/bin/python3
#keypad.py

"""

KeyPad - Key pad screen

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

# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../../lib')

# from utils.global_constants import Global

class KeyPadFrame(ttk.Frame):
    """ key pad frame """

    def __init__(self, parent, callback=None, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.callback = callback
        self.keypad = KeyPad(self, self.callback)
        self.keypad.grid(row=0)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

 #   def set_key_number(self, value):
 #       """ set key number """
 #       self.ids.key_number.text = value

 #   def get_key_number(self):
 #       """ get keu number """
 #       return self.ids.key_number.text

 #   def set_key_number_description(self, value):
 #       """ seyt key description """
 #       print("Value: "+ value)


class KeyPad(ttk.Frame):
    """ key pad """

    def __init__(self, parent, callback, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.callback = callback
        self.cols = 3
        self.spacing = 10
        self.buttons = []
        self.create_buttons()

    def on_clicked(self, num):
        """ key clicked """
        if self.callback is not None:
            self.callback(str(num))

    def create_buttons(self):
        """ create buttons """
        _list = [1, 2, 3, 4, 5, 6, 7, 8, 9, "CLR", 0, "<=="]
        kcol = 0
        krow = 0
        for num in _list:
            button = ttk.Button(self, text=num, state=NORMAL, width=4,
                    # command=self.callback(num))
                    padding=(4, 4, 4, 4), bootstyle="outline",
                    command=lambda i=num: self.on_clicked(i))
            self.buttons.append(button)
            button.grid(row=krow, column=kcol)
            # button.configure(style="KeyButton.TButton")
            kcol += 1
            if kcol > 2:
                kcol = 0
                krow += 1
