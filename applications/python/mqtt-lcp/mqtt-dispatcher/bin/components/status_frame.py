#!/usr/bin/python3
# status_frame.py
"""

StatusFrame - Status frame screen

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

from utils.global_constants import Global
from components.local_constants import Local
from components.image_clickable import ImageClickable
# from tk_message import TkMessage
#from components.info_box import InfoBox


class StatusFrame(ttk.Frame):
    """ status frame """

    def __init__(self, parent, parent_cab, parent_node, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_cab = parent_cab
        self.parent_node = parent_node
        self.grid_propagate(0)

        self.loco_id = None
        self.loco_blank_image = ImageClickable.load_image("img/locos/blank.png")
        self.loco_image = self.loco_blank_image

        self.cab_id = ttk.Label(self, text="Cab " + str(self.parent_cab.cab_id).upper(),\
                font=("HELVETICA", 20), width=5, anchor='nw')
        self.cab_id.grid(row=0, column=0, stick=(NW), padx=1)

        self.loco_frame = ttk.LabelFrame(self, width=100, height=90, \
                text=Local.LOCO.title(), relief="raised")
        self.loco_frame.grid_propagate(0)

        self.loco_box = ttk.Label(self.loco_frame, text="", \
                width=5, anchor='w')
        self.loco_box.grid(row=0, column=0, stick=(NW), padx=1)

        self.image_label = ImageClickable(self.loco_frame, image=self.loco_image,
                height=Local.LOCO_IMAGE_HEIGHT, \
                # width=Local.LOCO_IMAGE_WIDTH)
                width=90)
        self.image_label.grid(row=1, column=0,  padx=1, pady=2, sticky=(W))

        self.loco_frame.grid(row=1, column=0,padx=2, sticky=(NW))

        self.location_frame = ttk.LabelFrame(self, width=100, height=65, \
                text=Local.LOCATION.title(), relief="raised")
        self.location_frame.grid_propagate(0)

        self.location_railcom = ttk.Label(self.location_frame, text=" ", \
                width=10, anchor='w')
        self.location_railcom.grid(row=0, column=0, stick=(NW), padx=1)

        self.location_rfid = ttk.Label(self.location_frame, text=" ", \
                width=10, anchor='w')
        self.location_rfid.grid(row=1, column=0, stick=(NW), padx=1)

        self.location_frame.grid(row=2, column=0, stick=(W), padx=2)

        self.fastclock_frame = ttk.LabelFrame(self, width=100, height=40, \
                text=Local.FASTCLOCK.title(), relief="raised")
        self.fastclock_frame.grid_propagate(0)

        self.fastclock_box = ttk.Label(self.fastclock_frame, text="00:00", \
                width=5, anchor='w')
        self.fastclock_box.grid(row=0, column=0, stick=(NW), padx=16)

        self.fastclock_frame.grid(row=3, column=0,padx=2, sticky=(NW))

        self.localtime_frame = ttk.LabelFrame(self, width=100, height=40, \
                text=Local.LOCALTIME.title(), relief="raised")
        self.localtime_frame.grid_propagate(0)

        self.localtime_box = ttk.Label(self.localtime_frame, text="00:00", \
                width=5, anchor='w')
        self.localtime_box.grid(row=0, column=0, stick=(NW), padx=16)

        self.localtime_frame.grid(row=4, column=0,padx=2, sticky=(NW))

        self.columnconfigure(0, weight=1)

    def set_loco(self, loco_id):
        """ set the loco id status box """
        self.loco_id = loco_id
        self.loco_box.config(text=str(self.loco_id))
        self.loco_image = self.loco_blank_image
        if self.loco_id:
            roster_loco = self.parent_cab.locos_roster_map.get(int(self.loco_id), None)
            if roster_loco is not None and roster_loco.image is not None:
                self.loco_image = roster_loco.image
            self.image_label.replace_image(self.loco_image)

    def process_output_message(self, message):
        """ proces output message """
        if message.msg_type == Global.FASTCLOCK:
            _fast_time_string = "00:00"
            # print(">>> fastclock: " + str(message.msg_data))
            date_time = message.msg_data.get(Global.DATETIME, "0T00:00")
            # datetime is iso datetime YYYYYY-MM-DDTHH:SS:ms
            splits = date_time.split("T")
            if len(splits) > 1:
                time = splits[1]
                HHMM = time[0:5]
                self.fastclock_box.configure(text=HHMM)
        elif message.msg_type == Global.TIME:
            date_time = message.msg_data.get(Global.DATETIME, "0T00:00")
            # datetime is iso datetime YYYYYY-MM-DDTHH:SS:ms
            splits = date_time.split("T")
            if len(splits) > 1:
                time = splits[1]
                HHMM = time[0:5]
                self.localtime_box.configure(text=HHMM)
        elif message.msg_type == Global.LOCATOR:
            self.__process_location_message(message.msg_data)

    #
    # private functions
    #

    def __process_location_message(self, message_data):
        """ location  message received """
        lead_loco = self.parent.parent_cab.lead_loco
        # print(">>> lead loco:" + str(lead_loco))
        if lead_loco is None:
            self.location_railcom = ""
            self.location_rfid = ""
        else:
            if lead_loco == message_data.dcc_id:
                if message_data.sub_command == Global.RFID:
                    self.location_rfid.configure(text=message_data.port_id)
                else:
                    if message_data.reported == Global.EXITED:
                        if message_data.port_id == self.location_railcom:
                            self.location_railcom.configure(text="")
                    else:
                        self.location_railcom.configure(text=message_data.port_id)
                        self.location_rfid.configure(text="")
