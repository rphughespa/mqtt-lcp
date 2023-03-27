#!/usr/bin/python3
# throttle_client.py

"""
    ThrottleClient - Implements tk screens for mqtt-throttle. Run as a thread.


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


sys.path.append('../lib')

# from utils.global_constants import Global
# from components.local_constants import Local

# from components.title_frame import TitleFrame
from components.main_notebook import MainNotebook
from components.message_frame import MessageFrame

# from components.splash import Splash


class ThrottleClient(ttk.Frame):
    """ throttle client """

    def __init__(self, parent, parent_thread, log_queue, parent_node):
        """ initialize """
        super().__init__()
        self.parent = parent
        self.log_queue = log_queue
        self.parent_thread = parent_thread
        self.parent_node = parent_node
        # self.parent.overrideredirect(1)  # remove outer frame/border
        self.parent.withdraw()
        #splash = Splash(self.parent)
        #self.parent.after(2000)
        #splash.destroy()
        ## show window again
        self.parent.deiconify()
        #self.parent.attributes("-fullscreen", True)
        #self.parent.attributes('-zoomed', True)
        self.init_interface()

    def set_app_style(self):
        """ set up application """
        _s = ttk.Style()
        # print("Platform: "+_platform)
        # style = ttk.Style()
        #style.configure("My.TFrame", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG)
        #style.configure("Test.TFrame", foreground=Local.DEFAULT_FG, background='white')
        # style.configure("My.TLabel", foreground=ttk.BLACK, background=ttk.WHITE)
        #style.configure('My.Vertical.TScale', sliderwidth=32,
        #    foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG,
        #    troughcolor="ghost white")
        #style.configure('My.Horizontal.TScale',
        #    foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG,
        #    troughcolor="ghost white")

        #style.configure("ttk.TFrame", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG,
        #    borderwidth=0, padding=(0, 0, 0, 0))
        #style.configure("TNotebook", background=Local.DEFAULT_BG, borderwidth=0,
        #        tabposition='ne')
        #style.configure("TNotebook.Tab", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG, borderwidth=1,
        #        tabposition='ne', font=("Helvetica", 12))
        #style.configure("TNotebook.Tab", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG, borderwidth=1,
        #        tabposition='ne', font=("Helvetica", 8))
        #style.configure("Left.TNotebook", background=Local.DEFAULT_BG, borderwidth=0,
        #            tabposition='nw')
        #style.configure("Right.TNotebook", background=Local.DEFAULT_BG, borderwidth=0,
        #        tabposition='ne')
        #style.configure("Center.TNotebook", background=Local.DEFAULT_BG, borderwidth=0,
        #        tabposition='n')
                #lightcolor="blue", borderwidth=0)
        #style.configure("TButton", padding=(1, 1), background=Local.DEFAULT_BG)
        #style.configure("ImageButton", padding=(1, 1, 1, 1),
        #        background=Local.DEFAULT_BG,
        #        foreground=Local.DEFAULT_FG,
        #        borderwidth=0, highlightthickness=0, relief="flat")
        #style.configure("ImageButton.TFrame", padding=(1, 1, 1, 1),
        #        background=Local.DEFAULT_BG,
        #        foreground=Local.DEFAULT_FG,
        #        borderwidth=0, highlightthickness=0, relief="flat")

        #style.configure("InfoBox.TFrame",
        #        relief="solid", borderwidth=1,
        #        padding=(2, 2, 2, 2),
        #        foreground=Local.DEFAULT_FG,
        #        background=Local.DEFAULT_BG)
        #style.configure("InfoTitle.TLabel",
        #        foreground=Local.DEFAULT_FG,
        #        background=Local.DEFAULT_BG,
        #        justify="left", font=("Helvetica", 9), padding=(2, 2, 2, 2))
        #style.configure("InfoValue.TLabel",
        #        foreground=Local.DEFAULT_FG,
        #        background=Local.DEFAULT_BG,
        #        justify="left", font=("Helvetica", 10), padding=(2, 2, 2, 2))
        #style.configure("Small.TLabel", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG,
        #        justify="right", font=("Helvetica", 8), padding=(2, 2, 2, 2))
        #style.configure("Medium.TLabel", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG,
        #        justify="right", font=("Helvetica", 12), padding=(2, 2, 2, 2))

        #style.configure("KeyButton.TButton", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG,
        #        font=("Helvetica", 16), padding=(2, 2, 2, 2), width=12)
        #style.configure("ImageButtonSmall.TButton", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG,
        #        font=("Helvetica", 8), padding=(2, 2, 2, 2), width=4)
        #style.configure("ImageButtonMedium.TButton", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG,
        #        font=("Helvetica", 16), padding=(2, 2, 2, 2), width=4)
        #style.configure("ImageButtonLarge.TButton", foreground=Local.DEFAULT_FG, background=Local.DEFAULT_BG,
        #        font=("Helvetica", 24), padding=(2, 2, 2, 2), width=4)
        #style.configure("Black.TFrame", foreground=Local.DEFAULT_FG,
        #        background="black", borderwidth=0, padding=(0, 0, 0, 0))
        #        #self.app_frame = AppFrame(self.parent, config, style='My.App.TFrame', padding=(3, 3, 3, 3),
                #               width=800, borderwidth=1, relief="raised")

    def init_interface(self):
        """ initialize interface """
        # helv36 = font.Font(family="Helvetica", size=16, weight="bold")
        self.set_app_style()

        #self.title_frame = TitleFrame(self, self.parent_node, padding=(2, 2, 2, 2),
        #                borderwidth=1, relief="flat",
        #                height=20, style="My.TFrame")#width=800,
        self.main_frame = MainNotebook(self, self.parent_node, padding=(2, 2, 2, 2),
                        borderwidth=1, relief="raised")
                        # style="My.TFrame")#width=800,
        self.message_frame = MessageFrame(self, self.parent_node, padding=(2, 2, 2, 2),
                        borderwidth=1, relief="raised",
                        height=20)
                        #, style="My.TFrame")#width=800,
        #self.parent.columnconfigure(0, weight=1)
        #self.parent.rowconfigure(0, weight=1)
        #self.columnconfigure(0, weight=1)
        #self.rowconfigure(0, weight=0)
        #self.rowconfigure(1, weight=1)
        #self.rowconfigure(2, weight=0)
        self.grid(row=0, column=0, sticky=(N, S, E, W))
        #self.title_frame.grid(row=0, column=0, sticky=(N, E, S, W))
        self.main_frame.grid(row=0, column=0, sticky=(N, E, S, W))
        self.message_frame.grid(row=1, column=0, sticky=(N, E, S, W))

    #def get_widget_attributes(self):
    #    """ get attributes of a widget """
    #    all_widgets = self.app_frame.winfo_children()
    #    for widg in all_widgets:
    #        # print('\nWidget Name: {}'.format(widg.winfo_class()))
    #        keys = widg.keys()
    #        for key in keys:
    #            print("Attribute: {:<20}".format(key), end=' ')
    #            value = widg[key]
    #            vtype = type(value)
    #            #print('Type: {:<30} Value: {}'.format(str(vtype), value))

    def process_output_message(self, message):
        """ process output message """
        # print(str(message))
        # self.title_frame.process_output_message(message)
        self.main_frame.process_output_message(message)
        self.message_frame.process_output_message(message)
        pass

    def on_closing(self):
        """ on closing """
        print("Closing... client")
        self.parent_thread.shutdown_app()
        #self.parent.destroy()
