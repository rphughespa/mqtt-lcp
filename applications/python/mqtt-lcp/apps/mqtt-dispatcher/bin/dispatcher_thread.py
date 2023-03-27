#!/usr/bin/python3
# dispatcher_thread.py

"""

    DispatcherThread : class to manage tk screens for mqtt_dispatcher


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

from threading import Thread
import time


# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

sys.path.append('../lib')

from utils.global_constants import Global

from dispatcher_client import DispatcherClient

BUFFER_LENGTH = 4096

class DispatcherThread(Thread):
    """ class to manage stk screens via a thread"""

    def __init__(self, log_queue, thread_name, parent_node, events, tk_exit_event):
        """ init dispatcher thread """
        Thread.__init__(self)
        self.thread_name = thread_name
        self.log_queue = log_queue
        self.parent_node = parent_node
        self.tk_root = None
        self.tk_client = None
        self.tk_exit_event = tk_exit_event
        self.exit = False
        self.events = events

    def xxx_run(self):
        """ run the thread """
        time.sleep(0.5)
        self.log_queue.put(Global.LOG_LEVEL_INFO, 'Client Thread Started...')
        while not self.exit:
            try:
                time.sleep(0.3)
            except (KeyboardInterrupt, SystemExit):
                raise

    def loop_back(self):
        """ thread loop """
        # print("... loop")
        self.tk_root.after(100, self.loop_back)

    def run(self):
        """ Run the threads"""
        self.tk_root = ttk.Window(themename="litera")
        self.tk_root.title("MQTT Dispatcher")
        # self.tk_root.iconbitmap('./img/mqtt-lcp.ico')
        self.tk_client = DispatcherClient(self.tk_root, self, self.log_queue, self.parent_node)
        #root.minsize(800, 360)
        #root.minsize(800, 360)
        #if self.parent_node.screensize == Global.SMALL:
        #    self.tk_root.attributes('-zoomed', True)
        #elif self.parent_node.screensize == Global.MEDIUM:
        #    self.tk_root.attributes('-zoomed', True)
        #else:  # large
            # .geometry('320x200')
        self.tk_root.minsize(780, 380)
        # rw.get_widget_attributes()
        # self.tk_root.protocol("WM_DELETE_WINDOW", self.shutdown_app())
        self.tk_root.protocol("WM_DELETE_WINDOW", self.shutdown_app)
        self.tk_root.after(100, self.loop_back)
        # messy trying to shutdown tk when app is aexiting
        while not self.exit:
            if not self.parent_node.tk_out_queue.empty():
                message = self.parent_node.tk_out_queue.get()
                self.tk_client.process_output_message(message)
            if not self.exit:
                self.tk_root.update_idletasks()
            if not self.exit:
                self.tk_root.update()
            else:
                self.tk_root.destroy()
            # let this process sleep so other processes can run
            time.sleep(0.006)

    def shutdown(self):
        """ Shutdown both reader and writer threads"""
        self.log_queue.put((Global.LOG_LEVEL_INFO, Global.MSG_EXITING))
        self.exit = True
        self.join()

    def shutdown_app(self):
        """ thread shuting down """
        print("Closing ... process")
        # end_seconds = self.parent_node.now_seconds()
        self.log_queue.put((Global.LOG_LEVEL_ERROR,
                str(self.parent_node.node_name) +" "+str(Global.MSG_COMPLETED)))
        self.log_queue.put((Global.LOG_LEVEL_ERROR,
            str(self.parent_node.node_name)+" "+str(Global.MSG_EXITING)))
        self.tk_exit_event.set()
