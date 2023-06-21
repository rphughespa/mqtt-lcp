#! /usr/bin/python3
# system_page.py

"""

SystemPage - Track power page screen

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
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
# from tkinter import messagebox


sys.path.append('../../lib')

from utils.global_constants import Global

from structs.gui_message  import GuiMessage
from structs.gui_message import  GuiMessageEnvelope

from components.local_constants import Local

# from image_button import ImageButton

class SystemPage(ttk.Frame):
    """ control misc layout features """

    def __init__(self, parent, parent_node, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)

        self.track_power =  False
        self.parent = parent
        self.parent_node = parent_node

        self.frame = ttk.Frame(self, width=720, height=250, padding=(2,2,2,2))
        self.frame.grid(row=0,column=0,sticky="N")
        self.frame.grid_propagate(0)

        self.power_frame = ttk.LabelFrame(self.frame, width=220, height=60, \
                text=Local.POWER.title(), relief="raised")
        self.power_frame.grid(row=0,column=0,padx=12,sticky="N")
        self.power_frame.grid_propagate(0)

        self.TrackPower = IntVar()

        self.track_power_checkbutton =  ttk.Checkbutton(self.power_frame,
                bootstyle="success-round-toggle",
                width=22, # padx=1,
                text=Local.TRACK_POWER.title(),
                variable=self.TrackPower,
                onvalue=1, offvalue=0,
                state="normal",
                command=self.on_track_power_changed)
        self.track_power_checkbutton.grid(row=0, column=0, padx=12, pady=12)

        self.power_frame.grid(row=0, column=0)

        self.fastclock_frame = ttk.LabelFrame(self.frame, width=220, height=160, \
                text=Local.FASTCLOCK.title(), relief="raised")
        self.fastclock_frame.grid(row=0,column=0,padx=12,sticky="N")
        self.fastclock_frame.grid_propagate(0)

        self.fastclock_run_button = ttk.Button(self.fastclock_frame,
                    bootstyle="outline-success",
                    text=Local.FASTCLOCK_RUN.title(), state=NORMAL, width=15,
                    command=self.on_fastclock_run_clicked)
        self.fastclock_run_button.grid(column=0,row=0,padx=6, pady=8)

        self.fastclock_pause_button = ttk.Button(self.fastclock_frame,
                    bootstyle="outline-warning",
                    text=Local.FASTCLOCK_PAUSE.title(), state=NORMAL, width=15,
                    command=self.on_fastclock_pause_clicked)
        self.fastclock_pause_button.grid(column=0,row=1,padx=6,pady=4)

        self.fastclock_reset_button = ttk.Button(self.fastclock_frame,
                    bootstyle="outline-danger",
                    text=Local.FASTCLOCK_RESET.title(), state=NORMAL, width=15,
                    command=self.on_fastclock_reset_clicked)
        self.fastclock_reset_button.grid(column=0,row=2,padx=6, pady=4)

        self.fastclock_frame.grid(row=1, column=0)

        self.shutdown_frame = ttk.LabelFrame(self.frame, width=200, height=220, \
                text=Local.SHUTDOWN.title(), relief="raised")
        self.shutdown_frame.grid_propagate(0)

        self.shutdown_button = ttk.Button(self.shutdown_frame,
                    bootstyle="outline-danger",
                    text=Local.SHUTDOWN.title(), state=NORMAL, width=12,
                    command=self.on_shutdown_clicked)
        self.shutdown_button.grid(column=0,row=0,padx=2, pady=2)

        self.text1 = ttk.Label(self.shutdown_frame,text=Local.MSG_SHUTDOWN_1, \
                justify="center", font="Helvetica,16")
        self.text1.grid(column=0,row=1, padx=4, pady=12)

        self.text2 = ttk.Label(self.shutdown_frame,text=Local.MSG_SHUTDOWN_2, justify="center")
        self.text2.grid(column=0,row=2,padx=4, pady=2)

        self.shutdown_frame.grid(row=0, column=1, rowspan=2,stick=(NE))

        self.control_frame = ttk.LabelFrame(self.frame, width=220, height=120, \
                text=Local.TRAFFIC_CONTROL.title(), relief="raised")
        self.control_frame.grid(row=0, column=2, rowspan=2, padx=12, stick=(NE))
        self.control_frame.grid_propagate(0)

        self.AutoSignals = IntVar()

        self.auto_signals_checkbutton =  ttk.Checkbutton(self.control_frame,
                bootstyle="success-round-toggle",
                width=22, # padx=1,
                text=Local.AUTO_SIGNALS.title(),
                variable=self.AutoSignals,
                onvalue=1, offvalue=0,
                state="normal",
                command=self.on_auto_signals_changed)
        self.auto_signals_checkbutton.grid(row=0, column=0, padx=8, pady=12)

        self.TrafficControl = IntVar()

        self.traffic_control_checkbutton =  ttk.Checkbutton(self.control_frame,
                bootstyle="success-round-toggle",
                width=22, # padx=1,
                text=Local.CTC_TRAFFIC_CONTROL.title(),
                variable=self.TrafficControl,
                onvalue=1, offvalue=0,
                state="normal",
                command=self.on_traffic_control_changed)
        self.traffic_control_checkbutton.grid(row=1, column=0, padx=8, pady=12)

        self.frame.grid(row=0, column=0, rowspan=2, sticky=(NW))

        self.local_hhmm = "0000"

    def on_auto_signals_changed(self):
        """ automatic signals change requested  """
        auto_signals = self.AutoSignals.get()
        auto_signals_message = GuiMessage()
        auto_signals_message.command =  Global.TOWER
        auto_signals_message.port_id = Global.AUTO_SIGNALS
        if auto_signals == 1:
            auto_signals_message.mode = Global.ON
        else:
            auto_signals_message.mode = Global.OFF
        self.parent_node.queue_tk_input( \
            GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=auto_signals_message))

    def on_traffic_control_changed(self):
        """ traffic control change requested  """
        traffic_control = self.TrafficControl.get()
        traffic_control_message = GuiMessage()
        traffic_control_message.command =  Global.TOWER
        traffic_control_message.port_id = Global.TRAFFIC
        if traffic_control == 1:
            traffic_control_message.mode = Global.ON
        else:
            traffic_control_message.mode = Global.OFF
        self.parent_node.queue_tk_input( \
            GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=traffic_control_message))

    def on_track_power_changed(self):
        """ track power change requested  """
        power = self.TrackPower.get()
        power_message = GuiMessage()
        power_message.command =  Global.SWITCH
        power_message.port_id = Global.POWER
        if power == 1:
            power_message.mode = Global.ON
        else:
            power_message.mode = Global.OFF
        self.parent_node.queue_tk_input( \
            GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=power_message))

    def on_fastclock_pause_clicked(self):
        """ fatclock pause key clicked """
        fastclock_message = GuiMessage()
        fastclock_message.command =  Global.FASTCLOCK
        fastclock_message.mode = Global.PAUSE
        self.parent_node.queue_tk_input( \
            GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=fastclock_message))
        messagebox.showinfo(message=Local.MSG_FASTCLOCK_PAUSED)

    def on_fastclock_run_clicked(self):
        """ fastclock run key clicked """
        fastclock_message = GuiMessage()
        fastclock_message.command =  Global.FASTCLOCK
        fastclock_message.mode = Global.RUN
        self.parent_node.queue_tk_input( \
            GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=fastclock_message))
        messagebox.showinfo(message=Local.MSG_FASTCLOCK_RUNNING)

    def on_fastclock_reset_clicked(self):
        """ fastclock reset key clicked """
        new_time = simpledialog.askinteger("Reset Fastclock", "Enter new Fastclock time. \n (HHMM)",
                                        initialvalue=int(self.local_hhmm), \
                                        minvalue=0, maxvalue=2400,
                                        parent=self)
        valid_time = self.__validate_time_input(new_time)
        if valid_time is None:
            messagebox.showerror(title="Invalid Time", \
                                 message="Time entered is not valid format.\nMust be 24 hr format HHMM")
        else:
            fastclock_message = GuiMessage()
            fastclock_message.command =  Global.FASTCLOCK
            fastclock_message.mode = Global.RESET
            fastclock_message.value = valid_time
            self.parent_node.queue_tk_input( \
                GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=fastclock_message))
            messagebox.showinfo(message=Local.MSG_FASTCLOCK_RESET)

    def on_shutdown_clicked(self):
        """ shutdown key clicked """
        okk = messagebox.askokcancel(message=Local.MSG_SHUTDOWN_CONFIRM)
        if okk is True:
            shutdown_message = GuiMessage()
            shutdown_message.command =  Global.NODE
            shutdown_message.mode = Global.SHUTDOWN
            self.parent_node.queue_tk_input( \
                GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=shutdown_message))

    def process_output_message(self, message):
        """ process output message """
        if message.msg_type == Global.POWER:
            if message.msg_data.command == Global.SWITCH and \
                    message.msg_data.port_id == Global.POWER:
                if message.msg_data.mode == Global.ON:
                    self.TrackPower.set(1)
                else:
                    self.TrackPower.set(0)

        if message.msg_type == Global.POWER:
            if message.msg_data.mode == Global.ON:
                self.track_power = True
            else:
                self.track_power = False
        if message.msg_type == Global.TOWER:
            if message.msg_data.port_id == Global.TRAFFIC:
                if message.msg_data.mode == Global.ON:
                    self.TrafficControl.set(1)
                else:
                    self.TrafficControl.set(0)
            elif message.msg_data.port_id == Global.AUTO_SIGNALS:
                if message.msg_data.mode == Global.ON:
                    self.AutoSignals.set(1)
                else:
                    self.AutoSignals.set(0)
        if message.msg_type == Global.TIME:
            date_time = message.msg_data.get(Global.DATETIME, "0T00:00")
            # datetime is iso datetime YYYYYY-MM-DDTHH:SS:ms
            date_time_object = datetime.fromisoformat(date_time)
            hour = str(date_time_object.hour)
            if len(hour) < 2:
                hour = "0"+hour
            mins = str(date_time_object.minute)
            if len(mins) < 2:
                mins = "0"+mins
            self.local_hhmm = hour+mins


#
# private functions
#

    def __validate_time_input(self, new_time):
        """ validate the new time entered: 00000 thru 2400"""
        valid_time = None
        if new_time in range (2401):
            time = "0000"+ str(new_time)  # pad front with zeros
            time = time[-4:] # pull out right most digits
            hour = time[0:2]
            mins = time[2:4]
            if int(hour) < 25 and int(mins) < 60:
                valid_time = hour + ":"+ mins
        return valid_time
