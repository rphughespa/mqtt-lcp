#!/usr/bin/python3
# report_process.py
"""


report_process - generate the requested reports for static data for mqtt-tower



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
import time

from utils.global_constants import Global
from utils.json_utils import JsonUtils
from utils.utility import Utility

from structs.panels import Panels
from structs.warrants import Warrants
from structs.dashboard import Dashboard
from structs.sensor_states import SensorStates

from processes.base_process import BaseProcess


class ReportProcess(BaseProcess):
    """ Class that generates data for reports requests """
    def __init__(self, events=None, queues=None):
        super().__init__(name="report",
                         events=events,
                         in_queue=queues[Global.REPORT],
                         log_queue=queues[Global.LOGGER])
        self.app_queue = queues[Global.APPLICATION]
        self.inventory_queue = queues[Global.INVENTORY]
        self.events = events
        self.data_path = None
        self.dashboard_timeout = 60
        self.json_helper = JsonUtils()
        self.panels = None
        self.warrants = None
        self.dashboard = None
        self.sensor_states = None

    def initialize_process(self):
        """ load data from file system """
        super().initialize_process()
        (self.data_path, _backup_path) \
            = self.__parse_path_options_config(self.config)
        if self.data_path is None is None:
            self.log_critical(
                "!!!! Configureation file error: data and backup paths not found, exiting"
            )
            time.sleep(2)
            self.events[Global.SHUTDOWN].set()
        (self.dashboard_timeout) \
             = self.__parse_time_options_config(self.config)

        if self.data_path is None or \
                not os.path.exists(self.data_path):
            self.log_error("!!! Error: data path does not exists: " +
                           str(self.data_path))
        else:
            self.__load_panels()
            self.__load_warrants()
            self.__load_dashboard()
            self.__load_sensor_states()

    def process_message(self, new_message):
        """ process received messages """
        # print(">>> report: "+ str(new_message))
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            # print(">>> report new message: " + str(new_message))
            (msg_type, msg_body) = new_message
            if msg_type == Global.REQUEST:
                self.__process_request(msg_body)
                msg_consummed = True
            if msg_type == Global.PING:
                self.__record_ping(msg_body)
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
        if report_desired == Global.DASHBOARD:
            metadata = self.__generate_dashboard_report()
        elif report_desired == Global.PANELS:
            metadata = self.__generate_panels_report()
        elif report_desired == Global.WARRANTS:
            metadata = self.__generate_warrants_report()
        elif report_desired == Global.STATES:
            metadata = self.__generate_sensor_states_report()
        else:
            self.log_unexpected_message(msg_body=msg_body)
            metadata = {Global.ERROR: "Unknown report requested"}
            reported = Global.ERROR
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.RESPONSE, \
            Global.REPORTED: reported, Global.METADATA: metadata, Global.BODY: msg_body}))

    def __generate_panels_report(self):
        """ generate report data for panels """
        rett = None
        if self.panels is not None:
            rett = self.panels.encode()
        return rett

    def __generate_sensor_states_report(self):
        """ generate report data for sensor states """
        rett = None
        if self.sensor_states is not None:
            rett = self.sensor_states.encode()
        return rett

    def __generate_warrants_report(self):
        """ generate report data for warrants"""
        rett = None
        if self.warrants is not None:
            rett = self.warrants.encode()
        # print(">>> warrants: " + str(rett))
        return rett

    def __generate_dashboard_report(self):
        """ generate report data for dashboard"""
        # calc time value to be used to mark  nodes that have timed out
        # nodes that have not pinged since this time will be marked as ERROR
        timeout_milliseconds = Utility.now_milliseconds() - \
                self.dashboard_timeout * 1000
        rett = None
        self.dashboard.timeout_nodes(timeout_milliseconds)
        if self.dashboard is not None:
            rett = self.dashboard.encode()
        return rett

    def __record_ping(self, msg_body):
        """ record a ping received from an applcation """
        node_id = msg_body.mqtt_node_id
        if self.dashboard is not None:
            node_activated = self.dashboard.update_node_state(
                node_id, Global.ACTIVE, Utility.now_milliseconds())
            if node_activated:
                self.inventory_queue.put((Global.ACTIVATED, node_id))

    def __load_panels(self):
        """ load panels json data from file system """
        panels_path = self.data_path + "/panels.json"
        if not os.path.exists(panels_path):
            self.log_error("!!! Error: panels data path does not exists: " +
                           str(panels_path))
        else:
            panels_map = self.json_helper.load_and_parse_file(panels_path)
            #print("\n\n>>> panels 1: "+str(panels_map))
            self.panels = Panels(panels_map)
            #print("\n\n>>> panels 2: "+str(self.panels))
            #panels_map_2 = self.panels.encode()
            #print("\n\n>>>panels 3: "+str(panels_map_2))

    def __load_sensor_states(self):
        """ load sensor states json data from file system """
        sensor_states_path = self.data_path + "/sensor-states.json"
        if not os.path.exists(sensor_states_path):
            self.log_error(
                "!!! Error: sensor states data path does not exists: " +
                str(sensor_states_path))
        else:
            sensor_states_map = self.json_helper.load_and_parse_file(
                sensor_states_path)
            self.sensor_states = SensorStates(sensor_states_map)

    def __load_warrants(self):
        """ load warrants json data from file system """
        warrants_path = self.data_path + "/warrants.json"
        if not os.path.exists(warrants_path):
            self.log_error("!!! Error: warrants data path does not exists: " +
                           str(warrants_path))
        else:
            warrants_map = self.json_helper.load_and_parse_file(warrants_path)
            #print("\n\n>>>Warrants 1: "+str(warrants_map))
            self.warrants = Warrants(warrants_map)
            #print("\n\n>>> Warrants 2: "+str(self.warrants))
            #warrants_map_2 = self.warrants.encode()
            #print("\n\n>>> Warrants 3: "+str(warrants_map_2))

    def __load_dashboard(self):
        """ load dashboard json data from file system """
        dashboard_path = self.data_path + "/dashboard.json"
        if not os.path.exists(dashboard_path):
            self.log_error("!!! Error: dashboard data path does not exists: " +
                           str(dashboard_path))
        else:
            dashboard_map = self.json_helper.load_and_parse_file(
                dashboard_path)
            #print("\n\n>>> dashboard 1: "+str(dashboard_map))
            self.dashboard = Dashboard(dashboard_map)
            #print("\n\n>>> dashboard 2: "+str(self.dashboard))
            #dashboard_map_2 = self.dashboard.encode()
            #print("\n\n>>>dashboard 3: "+str(dashboard_map_2))

    def __parse_path_options_config(self, config):
        """ parse path options section of config file """
        data_path = None
        backup_path = None
        if Global.CONFIG in config:
            if Global.OPTIONS in config[Global.CONFIG]:
                data_path = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.DATA_PATH, None)
                backup_path = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.BACKUP_PATH, None)
        return (data_path, backup_path)

    def __parse_time_options_config(self, config):
        """ parse time options section of config file """
        dashboard_timeout = 60
        if Global.CONFIG in config:
            if Global.OPTIONS in config[Global.CONFIG]:
                option_time = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.TIME, {})
                dashboard_options = option_time.get(Global.DASHBOARD, {})
                dashboard_timeout = dashboard_options.get(Global.TIMEOUT, 60)
        return (dashboard_timeout)
