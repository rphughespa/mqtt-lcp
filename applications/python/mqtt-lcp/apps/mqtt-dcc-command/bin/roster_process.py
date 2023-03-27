#!/usr/bin/python3
# roster_process.py
"""


roster_process - Generate the requested rosters for for mqtt-lcp apps.

                The roster data is stored as indiviual JSON file in a configurable directory,
                one loco per file.  The json data files are loaded and parsed on program start. Then when
                requested the loco roster is published as a roster response message.

                The application monitors the directory the loco json files are stored.  Periodiucally the files
                in the folder are checked for changes, files added, files deleted or files modified. If changes are
                detected, all of the files are reloaded and a new roster is build.  When this happens, a
                data messesge is published indicating the roster has changed.

                Optionally, the application can import date from the loco roster in JMRI.  To enable the import
                turn on the web server option in decoder pro.  Periodically, the application will
                attempt of import the JMRI roster.  If the web read is sucessful, the JMRI roster
                is evaluated and any loco in the JMRI roster that is not already in the applications
                roster is added by writing a new roster loco file to the loco directory.
                Note:  the import operation only adds new locos, it don't chane or delete any locos.



The MIT License (MIT)

Copyright 2023 richard p hughes

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
from utils.dir_watcher import DirWatcher


from structs.roster import LocoFunctionData
from structs.roster import LocoData
from structs.roster import ConsistData
from structs.roster import Roster
from structs.io_data import IoData
from structs.mqtt_config import MqttConfig

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
        self.roster_data_path = None
        self.consists_data_path = None
        self.dashboard_timeout = 60
        self.json_helper = JsonUtils()
        self.roster = None
        self.roster_server_refresh = None
        self.roster_server_host = None
        self.roster_server_port = None
        self.roster_server_path = None
        self.roster_dir_watcher = None
        self.consists_dir_watcher = None
        self.import_roster_send_after_message = None
        self.check_roster_send_after_message = None
        self.mqtt_config = None

    def initialize_process(self):
        """ load data from file system """
        super().initialize_process()
        self.mqtt_config = MqttConfig(self.config, self.node_name,
                                      self.host_name, self.log_queue)
        (self.roster_data_path, self.consists_data_path) \
            = self.__parse_path_options_config(self.config)
        if self.roster_data_path is None is None:
            self.log_critical(
                "!!!! Configuration file error: roster data path not defined, exiting"
            )
            time.sleep(2)
            self.events[Global.SHUTDOWN].set()
        if self.roster_data_path is None or \
                not os.path.exists(self.roster_data_path):
            self.log_error("!!! Error: roster data path does not exists: " +
                           str(self.roster_data_path))
        else:
            self.roster_dir_watcher = DirWatcher(self.roster_data_path)
            self.consists_dir_watcher = DirWatcher(self.consists_data_path)
            self.__check_for_roster_changes()
            self.__load_roster()
        (self.roster_server_host, self.roster_server_port,
            self.roster_server_path, self.roster_server_refresh) \
            = self.__parse_roster_server_options_config(self.config)
        self.check_roster_send_after_message = \
                    SendAfterMessage(Global.ROSTER, None, 60000) # one minute
        self.send_after(self.check_roster_send_after_message)
        if self.roster_server_host is not None and \
                        self.roster_server_path is not None:
            self.import_roster_send_after_message = \
                    SendAfterMessage(Global.IMPORT, None, 180000) # three minutes
            self.send_after(self.import_roster_send_after_message)

    def process_message(self, new_message):
        """ process received messages """
        # print(">>> roster: "+ str(new_message))
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            # print(">>> roster new message: " + str(new_message))
            (msg_type, msg_body) = new_message
            if msg_type == Global.ROSTER:
                if self.__check_for_roster_changes():
                    self.log_info("Roster data has changed, reloading locos and consists files")
                    self.__load_roster()
                self.send_after(self.check_roster_send_after_message)
                msg_consummed = True
            if msg_type == Global.IMPORT:
                if self.roster_server_host is not None and \
                        self.roster_server_path is not None:
                    self.__import_roster_from_server()
                    self.send_after(self.import_roster_send_after_message)
                msg_consummed = True
            elif msg_type == Global.REQUEST:
                self.__process_request(msg_body)
                msg_consummed = True
        return msg_consummed

    #
    # private functions
    #

    def __process_request(self, msg_body):
        """ process request to send inventory reports """
        self.log_info("Report desired: " + str(msg_body.mqtt_port_id))
        metadata = None
        reported = msg_body.mqtt_desired
        if msg_body.mqtt_port_id == Global.ROSTER:
            metadata = self.__generate_roster_report()
        elif msg_body.mqtt_port_id == Global.RFID:
            metadata = self.__generate_roster_rfid_report()
        else:
            self.log_unexpected_message(msg_body=msg_body)
            metadata = {Global.ERROR: "Unknown report requested"}
            reported = Global.ERROR
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.RESPONSE, \
                                             Global.REPORTED: reported, \
                                             Global.METADATA: metadata, \
                                             Global.BODY: msg_body, \
                                             Global.DATA: None}))

    def __check_for_roster_changes(self):
        """ check for chnages to roster and reload is necessary"""
        if self.roster_server_host is not None and \
                self.roster_server_path is not None:
            self.__import_roster_from_server()
        return (self.roster_dir_watcher.has_changed() or\
                self.consists_dir_watcher.has_changed())

    def __generate_roster_report(self):
        """ generate report data for roster """
        rett = None
        if self.roster is not None:
            # print(">>> disp roster: " + str(self.roster))
            rett = self.roster.encode()
        # print(">>> disp roster rett: " + str(rett))
        return rett

    def __generate_roster_rfid_report(self):
        """ generate rfid report data for roster """
        rett = None
        if self.roster is not None:
            rfid_locos = []
            for loco_dcc_id, loco in self.roster.locos.items():
                if loco.rfid_id is not None:
                    rfid_locos.append({Global.DCC_ID: loco_dcc_id, Global.RFID_ID
                                       : loco.rfid_id})
            rett = {Global.RFID: rfid_locos}
        # print(">>> rfid roster: " + str(rett))
        return rett

    def __load_roster(self):
        """ load roster json data from file system """
        #roster_map = self.json_helper.load_and_parse_file(roster_path)
        #print(">>> roster_map: " + str(roster_map))
        self.roster = Roster()
        self.__load_loco_files()
        self.__load_consists_files()
        self.__publish_roster_changed()

    def __load_loco_files(self):
        """ load loco data from json data files """
        if os.path.isdir(self.roster_data_path):
            for file_name  in os.listdir(self.roster_data_path):
                full_file_name = os.path.join(self.roster_data_path, file_name)
                # print(">>> roster file: "+str(full_file_name))
                loco_parsed = self.json_helper.load_and_parse_file(full_file_name)
                new_loco = LocoData(init_map=loco_parsed)
                self.roster.locos.update({new_loco.dcc_id: new_loco})
                self.log_info("Loaded Loco: "+str(new_loco.dcc_id))
        # print(">>> rosterclass: "+ str(self.roster))

    def __load_consists_files(self):
        """ load consists data from json data files """
        if os.path.isdir(self.consists_data_path):
            for file_name  in os.listdir(self.consists_data_path):
                full_file_name = os.path.join(self.consists_data_path, file_name)
                # print(">>> consists file: "+str(full_file_name))
                consist_parsed = self.json_helper.load_and_parse_file(full_file_name)
                new_consist = ConsistData(init_map=consist_parsed)
                self.roster.consists.update({new_consist.dcc_id: new_consist})
                self.log_info("Loaded Consist: "+str(new_consist.dcc_id))
        #print(">>> rosterclass: "+ str(self.roster))


    def __parse_path_options_config(self, config):
        """ parse path options section of config file """
        roster_data_path = None
        consists_data_path = None
        if Global.CONFIG in config:
            if Global.OPTIONS in config[Global.CONFIG]:
                roster_data_path = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.ROSTER + "-"+Global.DATA_PATH, None)
                consists_data_path = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.CONSISTS + "-"+Global.DATA_PATH, None)
        return (roster_data_path, consists_data_path)

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
                    existing_loco = self.roster.locos.get(new_loco.dcc_id, None)
                    if existing_loco is None:
                        # only add new locos
                        self.__add_new_loco_to_folder(new_loco)

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
            response = requests.get(rest_url, timeout=3)
            response_code = response.status_code
            response_locos = response.json()
        except Exception:
            response_code = 500
        self.log_info("attempt import loco data from server: " +
                      str(rest_url) + ", response: " + str(response_code))
        return(response_code, response_locos)

    def __add_new_loco_to_folder(self, new_loco):
        """ save a new loco to file folder """
        #print(">>> new jmri loco: "+str(new_loco))
        dcc_id = new_loco.dcc_id
        loco_encoded = new_loco.encode()
        #print(">>>  ... new loco text: "+str(loco_encoded))
        loco_json = json.dumps(loco_encoded)
        loco_file_name = os.path.join(self.roster_data_path, "loco-"+str(dcc_id)+".json")
        self.log_info("Add imported Loco: "+str(dcc_id))
        with open(loco_file_name, "w", encoding='utf8') as loco_roster_file:
            loco_roster_file.write(loco_json)

    def __publish_roster_changed(self):
        """ send a data message notifing thta roster has changed """
        self.log_info("Publish roster changed...")
        topic = self.mqtt_config.publish_topics.get(Global.ROSTER,
                                                    Global.UNKNOWN)
        data_msg_body = IoData()
        data_msg_body.mqtt_message_root = Global.ROSTER
        data_msg_body.mqtt_node_id = self.node_name
        data_msg_body.mqtt_port_id = Global.ROSTER
        data_msg_body.mqtt_reported = Global.CHANGED
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.DATA, \
                                             Global.TOPIC: topic, \
                                             Global.BODY: data_msg_body}))
