#!/usr/bin/python3
# command_slots.py
"""

    SignalsManager.py - Class for automating signals

the MIT License (MIT)

Copyright © 2022 richard p hughes

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
import os

sys.path.append('../lib')

from utils.json_utils import JsonUtils
from utils.global_constants import Global
from structs.signal_rules import SignalRules
# from structs.sensor_states import SensorStates


class SignalsManager(object):
    """ Class representing a manager of signals"""
    def __init__(self, app_queue, sensor_states, data_path, log_queue=None):
        self.log_queue = log_queue
        self.app_queue = app_queue
        self.data_path = data_path
        self.json_helper = JsonUtils()
        self.sensor_states = sensor_states
        self.signal_rules = None
        self.__load_signal_rules()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def update_signals(self, _message_root, state_data):
        """ a sensor has changed, update assoiated signals"""
        self.__log_info("sensor_changed: " + str(state_data.key))
        pass

    #
    # private functions
    #

    def __load_signal_rules(self):
        """ load signal rules json data from file system """
        signal_rules_path = self.data_path + "/signal-rules.json"
        if not os.path.exists(signal_rules_path):
            self.__log_error(
                "!!! Error: signal rules data path does not exists: " +
                str(signal_rules_path))
        else:
            signal_rules_map = self.json_helper.load_and_parse_file(
                signal_rules_path)
            # print("\n\n>>> signal_rules json: "+str(signal_rules_map))
            self.signal_rules = SignalRules(signal_rules_map)
            # print("\n\n>>> signal_rules: "+str(self.signal_rules))
            self.signal_rules.build_block_signals()
            # print("\n\n>>> signal blocks: " + str(self.signal_rules.block_signals))
            self.signal_rules.build_sensor_signals()
            # print("\n\n>>> signal sensors: " + str(self.signal_rules.sensor_signals))

    def __log_info(self, message):
        """ send a info log entry to log process """
        self.log_queue.put(
                (Global.LOG_LEVEL_INFO, "signals manager: " + message))

    def __log_error(self, message):
        """ send a error log entry to log process """
        self.log_queue.put(
                (Global.LOG_LEVEL_ERROR, "signals manager: " + message))
