#!/usr/bin/python3
# roster_process.py
"""


roster_process - generate the requested rosters for static data for mqtt-tower



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

import json
import time
import os

import requests

from utils.json_utils import JsonUtils
from utils.global_constants import Global
# from utils.utility import Utility

from structs.roster import LocoFunctionData
from structs.roster import LocoData
from structs.roster import Roster

from processes.base_process import SendAfterMessage
from processes.base_process import BaseProcess





class RosterProcess(BaseProcess):
    """ Class that generates data for roster requests """

    def __init__(self, events=None, queues=None):
        super().__init__(name="roster",
                         events=events,
                         in_queue=queues[Global.ROSTER],
                         log_queue=queues[Global.LOGGER])
        self.app_queue = queues[Global.APPLICATION]
        self.events = events
        self.data_path = None
        self.dashboard_timeout = 60
        self.json_helper = JsonUtils()
        self.roster = None
        self.roster_server_refresh = None
        self.roster_server_host = None
        self.roster_server_port = None
        self.roster_server_path = None

    def initialize_process(self):
        """ load data from file system """
        super().initialize_process()
        (self.data_path) \
            = self.__parse_path_options_config(self.config)
        if self.data_path is None is None:
            self.log_critical(
                "!!!! Configuration file error: data and backup paths not found, exiting"
            )
            time.sleep(2)
            self.events[Global.SHUTDOWN].set()
        if self.data_path is None or \
                not os.path.exists(self.data_path):
            self.log_error("!!! Error: data path does not exists: " +
                           str(self.data_path))
        else:
            self.__load_roster()
        (self.roster_server_host, self.roster_server_port,
            self.roster_server_path, self.roster_server_refresh) \
            = self.__parse_roster_server_options_config(self.config)
        if self.roster_server_host is not None and \
                self.roster_server_path is not None:
            self.__import_roster_from_server()
            if self.roster_server_refresh > 0:
                self.__create_roster_import_send_after()

    def process_message(self, new_message):
        """ process received messages """
        # print(">>> roster: "+ str(new_message))
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            # print(">>> roster new message: " + str(new_message))
            (msg_type, msg_body) = new_message
            if msg_type == Global.REQUEST:
                self.__process_request(msg_body)
                msg_consummed = True
            elif msg_type == Global.IMPORT:
                self.__import_roster_from_server()
                if self.roster_server_refresh > 0:
                    self.__create_roster_import_send_after()
                msg_consummed = True
        return msg_consummed

    #
    # private functions
    #

    def __process_request(self, msg_body):
        """ process request to send inventory reports """
        report_desired = msg_body.get_desired_value_by_key(Global.REPORT)
        self.log_info("report desired: " + str(report_desired))
        reported = report_desired
        metadata = None
        if report_desired == Global.ROSTER:
            metadata = self.__generate_roster_report()
        else:
            self.log_unexpected_message(msg_body=msg_body)
            metadata = {Global.ERROR: "Unknown report requested"}
            reported = Global.ERROR
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.RESPONSE,
                                             Global.REPORTED: reported, Global.METADATA: metadata,
                                             Global.BODY: msg_body, Global.DATA: None}))

    def __generate_roster_report(self):
        """ generate report data for roster """
        rett = None
        if self.roster is not None:
            # print(">>> disp roster: " + str(self.roster))
            rett = self.roster.encode()
        # print(">>> disp roster rett: " + str(rett))
        return rett

    def __load_roster(self):
        """ load roster json data from file system """
        roster_path = self.data_path + "/roster.json"
        if not os.path.exists(roster_path):
            self.log_error("!!! Error: roster data path does not exists: " +
                           str(roster_path))
        else:
            roster_map = self.json_helper.load_and_parse_file(roster_path)
            self.roster = Roster(roster_map)

    def __parse_path_options_config(self, config):
        """ parse path options section of config file """
        data_path = None
        if Global.CONFIG in config:
            if Global.OPTIONS in config[Global.CONFIG]:
                data_path = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.DATA_PATH, None)
        return (data_path)

    def __parse_roster_server_options_config(self, config):
        """ parse roster server  options section of config file """
        roster_refresh = 0
        roster_host = None
        roster_port = None
        roster_path = None
        if Global.OPTIONS in config[Global.CONFIG]:
            if Global.TIME in config[Global.CONFIG][Global.OPTIONS]:
                roster_time_param = Global.ROSTER + "-" + Global.SERVER + "-" + Global.REFRESH
                if roster_time_param in config[Global.CONFIG][
                        Global.OPTIONS][Global.TIME]:
                    roster_refresh = config[Global.CONFIG][
                        Global.OPTIONS][Global.TIME][roster_time_param]
        if Global.IO in config[Global.CONFIG]:
            roster_server_param = Global.ROSTER + "-" + Global.SERVER
            if roster_server_param in config[Global.CONFIG][Global.IO]:
                roster_server_options = config[Global.CONFIG][Global.IO][roster_server_param]
                if Global.HOST in roster_server_options:
                    roster_host = roster_server_options[Global.HOST]
                if Global.PORT in roster_server_options:
                    roster_port = roster_server_options[Global.PORT]
                if Global.PATH in roster_server_options:
                    roster_path = roster_server_options[Global.PATH]
        self.log_info("Roster Server Refresh: " +
                      str(roster_refresh) + " ... " +
                      str(roster_host) + " ... " +
                      str(roster_port) + " ... " +
                      str(roster_path))
        return (roster_host, roster_port, roster_path, roster_refresh)

    def __import_roster_from_server(self):
        """ import roster locos from roster server """
        (response_code, response_locos) = \
            self.__perform_roster_server_import()
        server_locos = {}
        if response_code == 200:
            for loco in response_locos:
                new_loco = LocoData()
                data = loco.get("data", {})
                new_loco.name = data.get("name", None)
                new_loco.dcc_id = int(data.get("address", 0))
                if new_loco.name is None:
                    new_loco.name = str(new_loco.dcc_id)
                new_loco.description = new_loco.name
                new_loco.source = "import"
                if "functionKeys" in data:
                    function_keys = data["functionKeys"]
                    for func in function_keys:
                        func_label = func.get(Global.LABEL, None)
                        func_name = func.get(Global.NAME, None)
                        if func_name is not None and \
                                func_label is not None:
                            new_loco_func = LocoFunctionData()
                            new_loco_func.label = func_label.lower()
                            new_loco_func.name = func_name.lower()
                            new_loco_func.state = Global.UNKNOWN
                            new_loco.functions[new_loco_func.name] = new_loco_func
                if new_loco.dcc_id != 0:
                    server_locos[new_loco.name] = new_loco
        roster_updated = False
        roster_locos = self.roster.locos
        for name, loco in server_locos.items():
            if name not in roster_locos:
                roster_locos[name] = loco
                roster_updated = True
                self.log_info(
                    "roster: adding loco imported from server: " + str(name))
        if roster_updated:
            self.__save_roster_to_file()

    def __perform_roster_server_import(self):
        """ attempt to get roster from a REST server """
        rest_url = self.roster_server_host
        if self.roster_server_port is not None:
            rest_url += ":" + str(self.roster_server_port)
        rest_url += self.roster_server_path
        if rest_url.startswith("http") or \
                rest_url.startswith("HTTP"):
            pass
        else:
            rest_url = "http://" + rest_url
        response_code = 500
        response_locos = None
        try:
            response = requests.get(rest_url)
            response_code = response.status_code
            response_locos = response.json()
        except Exception:
            response_code = 500
        self.log_info("roster: import loco roster from server: " +
                      str(rest_url) + ", response: " + str(response_code))
        return(response_code, response_locos)

    def __create_roster_import_send_after(self):
        """ setup a send after message for roster import from server """
        # now_seconds = Utility.now_seconds()
        seconds_to_next_roster_import = self.roster_server_refresh
        # convert to millseconds
        milliseconds_to_next_fastclock = seconds_to_next_roster_import * 1000
        roster_import_send_after_message = SendAfterMessage(Global.IMPORT, None,
                                                            milliseconds_to_next_fastclock)
        self.send_after(roster_import_send_after_message)

    def __save_roster_to_file(self):
        """ save to roster to a file """
        new_roster_path = self.data_path + "/roster-new.json"
        old_roster_path = self.data_path + "/roster-old.json"
        roster_path = self.data_path + "/roster.json"
        # do a lot of nonsense to ensure we don't leave the roster file corrupted
        if os.path.exists(old_roster_path):
            # remove old backup
            os.remove(old_roster_path)
        if os.path.exists(roster_path):
            # make it a backup copy
            os.rename(roster_path, old_roster_path)
        # now create json and write to file
        roster_encoded = self.roster.encode()
        roster_json = json.dumps(roster_encoded)
        with open(new_roster_path, "w", encoding='utf8') as roster_file:
            roster_file.write(roster_json)
        # OK, write went OK, rename neww roster to roster
        os.rename(new_roster_path, roster_path)
        self.log_info("roster: saving updated roster")
