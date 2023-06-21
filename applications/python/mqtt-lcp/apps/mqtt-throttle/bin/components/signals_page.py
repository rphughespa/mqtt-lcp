#!/usr/bin/python3
# signals_page.py

"""

SignalsPage - Display / change the stat of signals

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
import copy

sys.path.append('../../lib')

# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


from utils.global_constants import Global
# from utils.global_synonyms import Synonyms

from structs.gui_message import GuiMessage
from structs.gui_message import GuiMessageEnvelope

from components.image_clickable import ImageClickable
from components.image_button import ImageButton
from components.signals_info_list import SignalsInfoList



# from components.local_constants import Local

# from select_list_data import SelectListData
# from key_pad import KeyPadFrame


class SignalsPage(ttk.Frame):
    """ Signals Screen """

    def __init__(self, parent, parent_node, tower_data, **kwargs):
        """ Initialize """
        super().__init__(parent, **kwargs)
        self.grid_propagate(0)
        self.parent = parent
        self.parent_node = parent_node
        self.tower_data = tower_data
        self.signal_type = "color"
        self.signal = None
        self.signal_image = None
        self.signal_key = None

        self.info_unknown_image = None
        self.info_clear_image = None
        self.info_approach_image = None
        self.info_stop_image = None

        self.signal_unknown_image = None
        self.signal_image_path = None
        self.signal_image = None
        self.signal_clear_image = None
        self.signal_approach_image = None
        self.signal_stop_image = None
        self.signal_blank_image = None

        self.__load_all_images()

        self.top_frame = ttk.Frame(
            self, width=340, height=64, padding=(2, 2, 2, 2))

        self.top_frame.grid_propagate(False)

        self.signal_frame = ttk.Frame(self.top_frame, relief="raised", width=236,  height=58,
                                      padding=(4, 2, 4, 2))
        self.signal_frame.grid_propagate(False)

        self.title_label = ttk.Label(self.signal_frame,
                                     text="",
                                     width=27, anchor='w')
        self.title_label.grid(row=0, column=0, padx=1)

        self.name_label = ttk.Label(self.signal_frame, text="",
                                    width=27, anchor='w')
        self.name_label.grid(row=1, column=0, padx=4)

        self.signal_frame.grid(row=0, column=0, sticky=(NW))

        self.button_frame = ttk.Frame(self.top_frame, relief="raised",
                                      height=116, width=98, padding=(2, 2, 2, 2))

        self.signal_button = ImageButton(self.button_frame, width=54, height=54,
                                         image=self.signal_blank_image,
                                         image_width=48, image_height=48,
                                         command=self.on_signal_clicked)
        self.signal_button.set_disabled()
        self.signal_button.grid(row=0, column=0, sticky=(NE))

        self.button_frame.grid(row=0, column=1, padx=2, sticky=(NE))

        self.top_frame.grid(row=0, column=0, sticky=(NW))

        self.list_frame = ttk.Frame(
            self, padding=(2, 2, 2, 2), relief="raised")

        self.signals_list = SignalsInfoList(self.list_frame, None,
                                            width=330, height=220, row_height=80,
                                            callback=self.on_list_item_clicked)
        self.signals_list.grid(row=0, column=0)

        self.list_frame.grid(row=1, column=0, sticky=(SE))

    def on_list_item_clicked(self, key):
        """ List item clicked """
        # print("signal.mode Clicked: "+ str(key))
        self.signal_key = key
        self.__populate_top_frame()

    def on_signal_clicked(self, _state):
        """ selection clicked """
        # print(">>> Signal: " + str(self.signal.name))
        if self.signal.mode is not None:
            #print(">>> signal selected: " +str(self.signal))
            new_mode = Global.APPROACH
            if self.signal.mode == Global.APPROACH:
                new_mode = Global.CLEAR
            elif self.signal.mode == Global.CLEAR:
                new_mode = Global.STOP
            signal_message = GuiMessage()
            signal_message.command = Global.SIGNAL
            signal_message.port_id = self.signal.port_id
            signal_message.node_id = self.signal.node_id
            signal_message.text = self.signal.text  # command topic
            signal_message.mode = new_mode
            self.parent_node.queue_tk_input(
                GuiMessageEnvelope(msg_type=Global.PUBLISH, msg_data=signal_message))

    def refresh_page(self):
        """ refresh the display page """
        self.__rebuild_signals_list()
        if self.signal is not None:
            self.__populate_top_frame()
        else:
            self.__clear_top_frame()
        pass

    def process_output_message(self, message):
        """ process output message """
        if message.msg_type == Global.SIGNAL:
            #print(">>> signal.modees page: " + str(message.msg_data))
            # an update of a signle signal.mode state
            skey = message.msg_data.node_id + ":" + message.msg_data.port_id
            if message.msg_data is None:
                # clear out signals table
                self.tower_data.signalss = {}
                self.signal = None
                self.refresh_page()
            else:
                signal = self.tower_data.signals.get(skey, None)
                if signal is None:
                    signal = copy.deepcopy(message.msg_data)
                    self.tower_data.signals[skey] = signal
                    self.refresh_page()
                else:
                    signal.mode = message.msg_data.mode
                    signal = self.__set_signal_image(signal)
                    self.refresh_page()

    #
    # private functions
    #

    def __set_signal_image(self, signal):
        """ set signal image based on mode """
        if signal.mode == Global.CLEAR:
            signal.image = self.info_clear_image
        elif signal.mode == Global.STOP:
            signal.image = self.info_stop_image
        elif signal.mode == Global.APPROACH:
            signal.image = self.info_approach_image
        else:
            signal.image = self.info_unknown_image
        return signal

    def __rebuild_signals_list(self):
        """ build display list box """
        self.signals_list.populate(self.tower_data.signals)

    def __populate_top_frame(self):
        """ populate top frame """
        self.signal = self.tower_data.signals[self.signal_key]
        self.title_label.config(text=self.signal.port_id)
        self.name_label.config(text=self.signal.name)
        #print(">>> signal mode: " + str(self.signal.mode))
        if self.signal.mode == Global.APPROACH:
            self.signal_button.replace_image(image=self.signal_approach_image)
        elif self.signal.mode == Global.CLEAR:
            self.signal_button.replace_image(image=self.signal_clear_image)
        elif self.signal.mode == Global.STOP:
            self.signal_button.replace_image(image=self.signal_stop_image)
        else:
            self.signal_button.replace_image(image=self.signal_unknown_image)
        self.signal_button.set_normal()

    def __clear_top_frame(self):
        """ clear top frame """
        self.signal = None
        self.title_label.config(text="")
        self.name_label.config(text="")
        self.signal_button.replace_image(image=self.signal_blank_image)
        self.signal_button.set_disabled()

    def __load_all_images(self):
        """ load images info application """
        image_path = None
        self.signal_type = "color"
        if "options" in self.parent_node.config[Global.CONFIG]:
            if Global.SIGNAL + "-" + Global.TYPE in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                self.signal_type = self.parent_node.config[Global.CONFIG][
                    Global.OPTIONS][Global.SIGNAL + "-" + Global.TYPE]
            if Global.IMAGE + "-" + Global.PATH in self.parent_node.config[Global.CONFIG][Global.OPTIONS]:
                image_path = self.parent_node.config[Global.CONFIG][Global.OPTIONS][Global.IMAGE + "-" + Global.PATH]
        if image_path is not None:

            # load "info" signals
            info_image_path = image_path + "/" + Global.INFO

            self.info_unknown_image = ImageClickable.load_image(
                info_image_path + "/info-unknown.png")
            self.info_clear_image = ImageClickable.load_image(
                info_image_path + "/info-green.png")
            self.info_approach_image = ImageClickable.load_image(
                info_image_path + "/info-yellow.png")
            self.info_stop_image = ImageClickable.load_image(
                info_image_path + "/info-red.png")

            self.signal_image_path = image_path + "/" + Global.SIGNAL + \
                "/" + self.signal_type + "/" + Global.SIGNAL_HEAD
            self.signal_unknown_image = ImageClickable.load_image(self.signal_image_path + "/signal-none.png",
                                                                  height=48, width=48)
            self.signal_image = ImageClickable.load_image(self.signal_image_path + "/signal-none.png",
                                                          height=48, width=48)
            # print(">>>> >>>> "+str(self.signal_image_path))
            self.signal_clear_image = ImageClickable.load_image(self.signal_image_path + "/signal-clear.png",
                                                                height=48, width=48)
            self.signal_approach_image = ImageClickable.load_image(self.signal_image_path + "/signal-approach.png",
                                                                   height=48, width=48)
            self.signal_stop_image = ImageClickable.load_image(self.signal_image_path + "/signal-stop.png",
                                                               height=48, width=48)
            self.signal_blank_image = ImageClickable.load_image(self.signal_image_path + "/signal-none.png",
                                                                height=48, width=48)
