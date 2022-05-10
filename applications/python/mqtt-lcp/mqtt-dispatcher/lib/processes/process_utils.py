#!/usr/bin/python3
# process_utils.py
"""

process_utils - misc classes that help manage processes

The MIT License (MIT)

Copyright 2021 richard p hughes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OFSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys

sys.path.append('../lib')

import os
import select
import time
from random import randrange
import multiprocessing
from multiprocessing import Event

# from utils.utility import Utility
from utils.json_utils import JsonUtils
from utils.yaml_utils import YamlUtils
from utils.global_constants import Global

#  program normmally start at boot, wait for other services to start
time.sleep(3)


class ProcessSupervisor(object):
    """ supervise processes """
    def __init__(self):
        self.shutdown_event = Event()
        self.restart_event = Event()
        self.config = None
        self.events = {
            Global.SHUTDOWN: self.shutdown_event,
            Global.RESTART: self.restart_event
        }
        self.processes = {}
        self.__load_config_file()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def monitor_all_processes(self):
        """ monitor processes, restart if they crash """
        # loop checking if any worker process has crashed and restart it
        print('supervisor: monitoring worker processes')
        print("supervisor: type 'quit' to exit")
        while not self.shutdown_event.is_set() \
            and not self.restart_event.is_set():
            # non blobking check for keyboard input
            keyb_input = select.select([sys.stdin], [], [], 1)[0]
            if keyb_input:
                value = sys.stdin.readline().rstrip()
                if value == "quit":
                    print("Exiting")
                    self.shutdown_event.set()
                else:
                    print(f"You entered: {value}, unknown command")
            else:
                self.check_processes_are_running()
            time.sleep(0.5)

    def check_processes_are_running(self):
        """ check that each process is running, if not restart"""
        key_list = list(self.processes.keys())
        for process_key in key_list:
            if not self.shutdown_event.is_set():
                process_info = self.processes.get(process_key, None)
                if process_info is not None:
                    (process_func, process_pid) = process_info
                    if not process_pid.is_alive():
                        print("supervisor: process " + str(process_key) +
                              " crashed, restarting")
                        process_func()
                        time.sleep(1)

    def shutdown_all_processes(self):
        """ shutdown all processes """
        print("Shutting down ...")
        self.shutdown_event.set()
        time.sleep(2)

        for process in multiprocessing.active_children():
            print("Shutting down process %r", process)
            process.terminate()
            process.join()

        if self.restart_event.is_set():
            print("restarting application in 15 seconds")
            self.shutdown_event.clear()
            self.restart_event.clear()
            time.sleep(15)
    def perform_wait_countdown(self, wait_range):
        """ wait a random time within a range """
        wait_seconds = randrange(wait_range) + 3
        print("Waiting to start: ")
        for i in reversed(range(wait_seconds)):
            time.sleep(1)
            print("\r ... " + str(i) + "  ", end="")
        print("\n ... starting...")

    def log_critical(self, message=None):
        """ log an critical message """
        print("!!! Critical: " + str(message))

    #
    # private functions
    #

    def __load_config_file(self):
        """ load  configuration file """
        if os.path.exists('config.yaml'):
            self.__load_yaml_config_file(file="config.yaml")
        elif os.path.exists('config.yml'):
            self.__load_yaml_config_file(file="config.yml")
        else:
            self.__load_json_config_file()
        #  print(">>> config: "+str(self.config))

    def __load_yaml_config_file(self, file="config.yaml"):
        """ load config.yaml configuration file """
        config = None
        yaml_helper = YamlUtils()
        try:
            config = yaml_helper.load_and_parse_file(file)
        except Exception as exc:
            message = "Exception during YAML parsing, exiting: " \
                + str(exc) + "\n" + str("config.yaml")
            print(message)
            self.log_critical(message)
            # wait a few seconds to error to be logged
            time.sleep(2)
            self.events[Global.SHUTDOWN].set()
        self.config = config

    def __load_json_config_file(self):
        """ load config.json configuration file """
        config = None
        json_helper = JsonUtils()
        try:
            config = json_helper.load_and_parse_file("config.json")
        except Exception as exc:
            message = "Exception during JSON parsing, exiting: "\
                + str(exc) + "\n" + str("config.json")
            print(message)
            self.log_critical(message)
            # wait a few seconds to error to be logged
            time.sleep(2)
            self.events[Global.SHUTDOWN].set()
        self.config = config
