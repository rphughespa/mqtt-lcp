#!/usr/bin/python3
# controls_page.py

"""

ControlsPage - Controls page  screen

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

from components.image_clickable import ImageClickable
from components.image_toggle_button import ImageToggleButton
from components.image_button import ImageButton
from components.gauge import Gauge
from components.status_frame import StatusFrame
from components.local_constants import Local




class ControlsPage(ttk.Frame):
    """ controls page """

    def __init__(self, parent, parent_node, parent_cab, cab_id, **kwargs):
        """ initialize """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.parent_node = parent_node
        self.parent_cab = parent_cab
        self.cab_id = cab_id
        self.speedo_value = 0

        self.signal_off_image = None
        self.signal_clear_image = None
        self.signal_approach_image = None
        self.signal_stop_image = None
        self.power_increase = None
        self.power_decrease = None
        self.speed_dial = None
        self.forward_button = None
        self.stop_button = None
        self.reverse_button = None
        self.bell = None
        self.horn = None

        self.power_frame = ttk.Frame(self, height=280, padding=(2, 2, 4, 2))
        self.speed_frame = ttk.Frame(
            self, height=280, width=200,  padding=(4, 4, 4, 2))
        self.functions_frame = ttk.Frame(self.speed_frame, padding=(2, 4, 2, 2),
                                         height=44, width=180)
        self.dial_frame = ttk.Frame(
            self.speed_frame, height=240, width=180,  padding=(4, 4, 4, 2))
        self.signal_frame = ttk.Frame(self.dial_frame, height=120, width=48)
        self.direction_frame = ttk.Frame(
            self.speed_frame, height=44, width=180,  padding=(4, 4, 4, 2))

        self.__load_all_images()

        self.power_increase.grid(row=0, column=0, sticky=(N))
        self.power_increase.set_disabled()

        self.power_slider = ttk.Scale(self.power_frame,
                                      orient='vertical', length=190, command=self.scale_changed,
                                      from_=100, to=0)  # , sliderwidth=32)
        self.power_slider.grid(row=1, column=0)
        self.power_slider.configure(state='disabled')

        self.power_level = ttk.Label(
            self.power_frame, text="0", width=3, anchor='s')
        self.power_level.grid(row=2, column=0)
        self.power_level.configure(state='disabled')

        self.power_decrease.grid(row=3, column=0, sticky=(S))
        self.power_decrease.set_disabled()

        self.power_frame.grid(row=0, column=0, sticky=(NW))

        self.speed_dial.grid(row=0, column=0, sticky=(NW))

        self.cab_signal = ImageButton(self.signal_frame, width=40, height=100, compound=CENTER,
                                      image=self.signal_off_image, image_width=32, image_height=96)
        self.cab_signal.grid(row=0, column=0, padx=2, sticky=(N))
        self.cab_signal.set_disabled()

        self.signal_frame.grid(row=0, column=1, sticky=(NE))

        self.dial_frame.grid(row=0, column=0, sticky=(N))

        self.forward_button.grid(row=0, column=0, sticky=(NW))
        self.forward_button.set_disabled()

        self.stop_button.grid(row=0, column=1, sticky=(N))
        self.stop_button.set_disabled()

        self.reverse_button.grid(row=0, column=2, sticky=(NE))
        self.reverse_button.set_disabled()

        self.direction_frame.grid(row=1, column=0, pady=12)

        self.bell.grid(row=0, column=0, sticky=(SW))
        self.bell.set_disabled()

        self.horn.grid(row=0, column=1, sticky=(SE))
        self.horn.set_disabled()

        self.functions_frame.grid(row=2, column=0, sticky=(N))

        self.speed_frame.grid(row=0, column=1, sticky=(N))

        self.status_frame = StatusFrame(self, self.parent_cab, self.parent_node, padding=(2, 2, 2, 2),
                                        width=102, height=280)

        self.status_frame.grid(row=0, column=2, sticky=(NE))

        self.power_update_in_progress = False
        self.parent_cab.loco_current_speed = 0
        self.speedo_value = 0
        self.update_power_displays()

    def update_power_displays(self):
        """ update power display """
        self.power_level.config(text=str(self.parent_cab.loco_current_speed))
        self.power_update_in_progress = True  # prevent recursion
        self.power_slider.set(self.parent_cab.loco_current_speed)
        self.power_update_in_progress = False
        self.speed_dial.set_value(self.speedo_value)

    def scale_changed(self, new_value):
        """ scale changed """
        if not self.power_update_in_progress:  # prevent recursion
            new_int = int(float(new_value)+0.5)
            new_int = max(new_int, 0)
            new_int = min(new_int, 100)
            # print(">>> speed: "+str(new_int))
            self.parent_cab.loco_current_speed = new_int
            self.update_power_displays()
            self.parent_cab.publish_speed_request()
            self.refresh_page()

    def increment_power(self, direction):
        """ increment power """
        increment = 0
        curr_value = self.parent_cab.loco_current_speed
        if curr_value > 30:
            increment = 4
        elif curr_value > 20:
            increment = 3
        elif curr_value > 10:
            increment = 2
        else:
            increment = 1
        new_value = (direction * increment)+curr_value
        new_value = max(new_value, 0)
        new_value = min(new_value, 100)
        self.parent_cab.loco_current_speed = new_value
        self.parent_cab.publish_speed_request()
        self.update_power_displays()
        self.refresh_page()

    def on_increase_clicked(self, _state):
        """ increase clicked """
        self.increment_power(1)

    def on_decrease_clicked(self, _state):
        """ decrease clicked """
        self.increment_power(-1)

    def on_forward_clicked(self, _state):
        """ forward clicked """
        #print("Forward Clicked")
        self.parent_cab.loco_current_direction = Global.FORWARD
        self.reverse_button.set_state(Global.OFF)
        self.parent_cab.publish_direction_request()
        self.refresh_page()

    def on_stop_clicked(self, _state):
        """ stop clicked """
        #print("Stop Clicked")
        self.parent_cab.loco_current_speed = -1
        self.parent_cab.loco_current_direction = None
        self.forward_button.set_state(Global.OFF)
        self.reverse_button.set_state(Global.OFF)
        self.parent_cab.publish_speed_request()
        self.parent_cab.loco_current_speed = 0
        self.update_power_displays()
        self.refresh_page()

    def on_reverse_clicked(self, _state):
        """ reverse clicked """
        #print("Reverse Clicked: " + str(state))
        self.parent_cab.loco_current_direction = Global.REVERSE
        self.forward_button.set_state(Global.OFF)
        self.parent_cab.publish_direction_request()
        self.refresh_page()

    def on_bell_clicked(self, state):
        """ bell clicked """
        #print("Bell Clicked: "+ str(state))
        self.parent_cab.set_function_state(1, state)
        self.parent_cab.publish_function_request(1)
        self.parent_cab.refresh_all_pages()

    def on_horn_clicked(self, state):
        """ horn clicked """
        #print("horn Clicke: " + str(state))
        self.parent_cab.set_function_state(2, state)
        self.parent_cab.publish_function_request(2)
        self.parent_cab.refresh_all_pages()

    def refresh_page(self):
        """ refresh the display page """
        self.bell.set_state(self.parent_cab.get_function_state(1))
        self.horn.set_state(self.parent_cab.get_function_state(2))

        if self.parent_cab.any_locos_selected():
            if self.parent_cab.loco_current_direction is not None:
                self.power_increase.set_normal()
                self.power_decrease.set_normal()
                self.power_slider.configure(state='normal')
                self.power_level.configure(state='normal')
                loco_cab_signal_state = \
                    self.parent_cab.loco_cab_signals.get(
                        self.parent_cab.lead_loco, None)
                self.cab_signal.set_normal()
                if loco_cab_signal_state is None:
                    self.cab_signal.replace_image(
                        image=self.signal_approach_image)
                elif loco_cab_signal_state == Global.STOP:
                    self.cab_signal.replace_image(image=self.signal_stop_image)
                elif loco_cab_signal_state == Global.CLEAR:
                    self.cab_signal.replace_image(
                        image=self.signal_clear_image)
                else:
                    self.cab_signal.replace_image(
                        image=self.signal_approach_image)
            else:
                self.power_increase.set_disabled()
                self.power_decrease.set_disabled()
                self.power_slider.configure(state='disabled')
                self.power_level.configure(state='disabled')
                self.cab_signal.set_disabled()
                self.cab_signal.replace_image(image=self.signal_off_image)
            self.bell.set_normal()
            self.horn.set_normal()
            self.stop_button.set_normal()
            if self.parent_cab.loco_current_speed == 0:
                self.forward_button.set_normal()
                self.reverse_button.set_normal()
            else:
                if self.parent_cab.loco_current_direction == Global.FORWARD:
                    self.forward_button.set_normal()
                    self.reverse_button.set_disabled()
                else:
                    self.forward_button.set_disabled()
                    self.reverse_button.set_normal()
        else:
            self.power_increase.set_disabled()
            self.power_decrease.set_disabled()
            self.power_slider.configure(state='disabled')
            self.power_level.configure(state='disabled')
            self.bell.set_disabled()
            self.horn.set_disabled()
            self.forward_button.set_disabled()
            self.stop_button.set_disabled()
            self.reverse_button.set_disabled()

    def process_output_message(self, message):
        """ process output message """
        # print(">>> message: " + str(message))
        if message.msg_type == Global.SPEED:
            self.speedo_value = message.msg_data.speed
            if message.msg_data.speed is None:
                self.speedo_value = 0
            elif message.msg_data.speed < 0:
                self.speedo_value = 0
            elif message.msg_data.speed > 100:
                self.speedo_value = 100
            else:
                self.speedo_value = message.msg_data.speed
            self.speed_dial.set_value(self.speedo_value)
        self.status_frame.process_output_message(message)

    def __load_all_images(self):
        """ load images info application """
        image_path = None
        signal_type = "color"
        if "options" in self.parent_node.config[Global.CONFIG]:
            if Global.SIGNAL + "-" + Global.TYPE in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                signal_type = self.parent_node.config[Global.CONFIG][
                    Global.OPTIONS][Global.SIGNAL + "-" + Global.TYPE]
            if Global.IMAGE + "-" + Global.PATH in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                image_path = self.parent_node.config[Global.CONFIG][Global.OPTIONS][Global.IMAGE + "-" + Global.PATH]

        if image_path is not None:
            # load "cab" signals
            signal_image_path = image_path + "/" + Global.SIGNAL + \
                "/" + signal_type + "/" + Global.CAB

            self.signal_off_image = ImageClickable.load_image(
                signal_image_path + "/signal-none.png")
            self.signal_clear_image = ImageClickable.load_image(
                signal_image_path + "/signal-clear.png")
            self.signal_approach_image = ImageClickable.load_image(
                signal_image_path + "/signal-approach.png")
            self.signal_stop_image = ImageClickable.load_image(
                signal_image_path + "/signal-stop.png")

            buttons_image_path = image_path + "/" + Global.BUTTONS
            self.power_increase = ImageButton(self.power_frame, width=32, height=32, compound=CENTER, \
                                                image_file=buttons_image_path + "/triangle-up.png", \
                                                image_width=24, image_height=24, \
                                                style="link", \
                                                command=self.on_increase_clicked)

            self.speed_dial = Gauge(self.dial_frame, max_value=100, max_rotation=270, \
                                    gauge_height=160, gauge_width=160,\
                                    gauge_image_file=image_path+"/gauge-small.png", \
                                    needle_height=140, needle_width=140, \
                                    needle_image_file=image_path+"/needle-medium.png")

            self.power_decrease = ImageButton(self.power_frame, width=32, height=32, compound=CENTER, \
                                                image_file=buttons_image_path + "/triangle-down.png",  \
                                                image_width=24, image_height=24, \
                                                style="link", \
                                                command=self.on_decrease_clicked)

            self.forward_button = ImageToggleButton(self.direction_frame, width=80, height=40,
                                                    compound=CENTER,
                                                    image_file=buttons_image_path + "/triangle-forward.png",
                                                    on_image_file=buttons_image_path + "/triangle-forward-on.png",
                                                    image_width=75, image_height=27,
                                                    # style="link",
                                                    command=self.on_forward_clicked)

            self.stop_button = ImageButton(self.direction_frame, width=40, height=40,
                                           compound=CENTER, image_file=buttons_image_path+"/stop.png",
                                           image_width=30, image_height=30,
                                           command=self.on_stop_clicked,
                                           style="link",
                                           padding=(3, 1, 1, 1))

            self.reverse_button = ImageToggleButton(self.direction_frame, width=80, height=40,
                                                    compound=CENTER, image_width=75, image_height=27,
                                                    image_file=buttons_image_path+"/triangle-reverse.png",
                                                    on_image_file=buttons_image_path+"/triangle-reverse-on.png",\
                                                    # style="link",
                                                    command=self.on_reverse_clicked)

            self.bell = ImageToggleButton(self.functions_frame, width=80, height=36,
                                          text=' '+Local.BELL.title(),
                                          compound=LEFT, image_width=26, image_height=26,
                                          image_file=buttons_image_path+"/bell.png",
                                          on_image_file=buttons_image_path+"/bell-on.png",
                                          command=self.on_bell_clicked)

            self.horn = ImageToggleButton(self.functions_frame, width=80, height=36,
                                          text=' '+Local.HORN.title(),
                                          compound=LEFT, image_width=26, image_height=26,
                                          image_file=buttons_image_path+"/horn.png",
                                          on_image_file=buttons_image_path+"/horn-on.png",
                                          command=self.on_horn_clicked)
