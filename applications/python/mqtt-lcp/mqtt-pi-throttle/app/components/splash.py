#!/usr/bin/python3
# # splash.py

"""

    Splash - Splash screen


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

# from tkinter import font

# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../../lib')

# from utils.global_constants import Global
from  components.local_constants import Local

from components.image_clickable import ImageClickable

class Splash(ttk.Toplevel):
    """ Splash screen """

    def __init__(self, parent):
        """ INitialize """
        super().__init__(parent)
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = screen_width/2 - 320/2   # was 480x240
        y = screen_height/2 - 166/2
        print("X: "+str(x)+", Y: "+str(y))
        self.title("MQTT Throttle")
        self.geometry('320x166+' + str(int(x)) + '+'+str(int(y)))

        #style = ttk.Style()
        #style.configure("ttk.TFrame", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG)
        #style.configure("ttk.TLabel", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.configure(bg="black")
        self.frame = ttk.Frame(self, width=320, height=240)
        self.frame.grid(row=0, column=0)
        #self.frame.configure(style="ttk.TFrame")
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        image_one = ImageClickable.load_image("img/splash_small_black.png")

        self.canvas = ttk.Canvas(self.frame, width=320, height=240, bg=Local.DEFAULT_BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0)
        self.canvas.create_image(0, 0, image=image_one, anchor=NW)


        self.label = ttk.Label(self.frame, text="Initializing")
        self.label.grid(row=1, column=0)
        self.label.configure(style="ttk.TLabel")


        ## required to make window show before the program gets to the mainloop
        self.update()
