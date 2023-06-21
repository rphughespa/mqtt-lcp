#!/usr/bin/python3
# report_process.py
"""


report_process - generate the requested reports for static data for mqtt-tower



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

import time
import os
import sys

sys.path.append('../lib')

from utils.global_constants import Global
from utils.json_utils import JsonUtils
from utils.utility import Utility

from structs.io_data import IoData
from structs.mqtt_config import MqttConfig
from structs.panels import PanelData
from structs.panels import Panels
from structs.dashboard import Dashboard

from processes.base_process import SendAfterMessage
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
        self.mqtt_config = None
        self.data_path = None
        self.dashboard_timeout = 60
        self.dashboard_interval = 60
        self.dashboard_topic = None
        self.dashboard_send_after_message = None
        self.json_helper = JsonUtils()
        self.panels = None
        self.dashboard = None
        self.sensor_states = None
        self.dashboard_changed = False
        self.check_timeout_send_after_message = None
        self.check_dashboard_send_after_message = None

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
        self.mqtt_config = MqttConfig(self.config, self.node_name,
                                      self.host_name, self.log_queue)
        (self.dashboard_topic) \
            = self.__parse_mqtt_options_config(self.mqtt_config)
        (self.dashboard_timeout, self.dashboard_interval) \
            = self.__parse_time_options_config(self.config)

        if self.data_path is None or \
                not os.path.exists(self.data_path):
            self.log_error("!!! Error: data path does not exists: " +
                           str(self.data_path))
        else:
            self.__load_dashboard()

        self.check_timeout_send_after_message = \
            SendAfterMessage(Global.TIMEOUT, None, self.dashboard_timeout*1000)
        self.send_after(self.check_timeout_send_after_message)

        self.check_dashboard_send_after_message = \
            SendAfterMessage(Global.DASHBOARD, None, 1000)  # 1 seconds
        self.send_after(self.check_dashboard_send_after_message)

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
            elif msg_type == Global.DASHBOARD:
                if self.__check_for_dashboard_changes():
                    self.log_info(
                        "Dashboard data has changed, notify other apps]")
                    self.__publish_dashboard_changed()
                self.send_after(self.check_dashboard_send_after_message)
                msg_consummed = True
            elif msg_type == Global.TIMEOUT:
                self.__update_dashboard_timeouts()
                self.send_after(self.check_timeout_send_after_message)
                msg_consummed = True
        return msg_consummed

    def get_topic_node_id(self, topic):
        """ parse out node id from topic """
        node_id = Global.UNKNOWN
        if topic is not None:
            topic_parts = topic.split("/")
            if len(topic_parts) > 3:
                node_id = topic_parts[3]
        return node_id
    #
    # private functions
    #

    def __check_for_dashboard_changes(self):
        """ check for changes to dashboard is necessary"""
        changed = False
        if self.dashboard_changed:
            changed = True
            self.dashboard_changed = False
        return changed

    def __publish_dashboard_changed(self):
        """ send a data message notifing dashboard has changed """
        self.log_info("Publish Dashboard changed...")
        topic = self.mqtt_config.publish_topics.get(Global.DASHBOARD,
                                                    Global.UNKNOWN)
        data_msg_body = IoData()
        data_msg_body.mqtt_message_root = Global.TOWER
        data_msg_body.mqtt_node_id = self.get_topic_node_id(topic)
        data_msg_body.mqtt_port_id = Global.DASHBOARD
        data_msg_body.mqtt_reported = Global.CHANGED
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.DATA,
                                             Global.TOPIC: topic,
                                             Global.BODY: data_msg_body}))

    def __process_request(self, msg_body):
        """ process request to send inventory reports """
        report_desired = msg_body.mqtt_desired
        port_id = msg_body.mqtt_port_id
        self.log_info("report desired: " +
                      str(report_desired) + " ... "+str(port_id))
        reported = report_desired
        metadata = None
        msg_consummed = False
        if report_desired == Global.REPORT:
            if port_id == Global.DASHBOARD:
                metadata = self.__generate_dashboard_report()
                msg_consummed = True
            elif port_id == Global.PANEL:
                panels = self.__load_panels()
                metadata = self.__generate_panels_report(panels)
                msg_consummed = True
        # elif report_desired == Global.STATE:
        #    metadata = self.__generate_sensor_states_report()
        if not msg_consummed:
            self.log_unexpected_message(msg_body=msg_body)
            metadata = {
                Global.ERROR: "Unknown report requested: "+str(port_id)}
            reported = Global.ERROR
        self.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.RESPONSE,
                                             Global.REPORTED: reported,
                                             Global.METADATA: metadata,
                                             Global.BODY: msg_body}))

    def __generate_panels_report(self, panels):
        """ generate report data for panels """
        rett = None
        if panels is not None:
            rett = panels.encode()
        return rett

    def __update_dashboard_timeouts(self):
        """ timeoute nodes that are not pinging """
        # calc time value to be used to mark  nodes that have timed out
        # nodes that have not pinged since this time will be marked as ERROR
        timeout_milliseconds = Utility.now_milliseconds() - \
            self.dashboard_timeout * 1000
        dashboard_changed = self.dashboard.timeout_nodes(timeout_milliseconds)
        # print(">>> dashboard_changed: "+str(dashboard_changed))
        if dashboard_changed is True:
            self.dashboard_changed = True

    def __generate_dashboard_report(self):
        """ generate report data for dashboard"""
        self.__update_dashboard_timeouts()
        if self.dashboard is not None:
            rett = self.dashboard.encode()
        return rett

    def __record_ping(self, msg_body):
        """ record a ping received from an applcation """
        node_id = msg_body.mqtt_node_id
        if self.dashboard is not None:
            (node_activated, dashboard_changed) = \
                self.dashboard.update_node_state(
                    node_id, Global.ON, Utility.now_milliseconds())
            # print(">>> dashboard_changed 2: "+str(dashboard_changed))
            if dashboard_changed:
                self.dashboard_changed = True
            if node_activated:
                self.inventory_queue.put((Global.ON, node_id))

    def __load_panels(self):
        """ load panels json data from file system """
        # print("\n\n>>> loading panel...")
        panels = None
        panels_path = os.path.join(self.data_path, Global.PANEL)
        if not os.path.exists(panels_path):
            self.log_error("!!! Error: panels data path does not exists: " +
                           str(panels_path))
        else:
            if os.path.isdir(panels_path):
                for file_name in os.listdir(panels_path):
                    full_file_name = os.path.join(panels_path, file_name)
                    if ".json" in full_file_name:
                        panel_map = self.json_helper.parse_one_json_file(
                            panels_path)
                        # print("\n\n>>> panels 1: "+str(panels_map))
                        new_panel = PanelData(panel_map)
                        if panels is None:
                            panels = Panels()
                        panels.panels.update({new_panel.name: new_panel})
                        # print("\n\n>>> panels 2: "+str(self.panels))
                        # panels_map_2 = self.panels.encode()
        # print("\n\n>>> ... panels : "+str(panels))
        return panels

    def __load_dashboard(self):
        """ load dashboard json data from file system """
        dashboard_path = self.data_path + "/dashboard.json"
        if not os.path.exists(dashboard_path):
            self.log_error("!!! Error: dashboard data path does not exists: " +
                           str(dashboard_path))
        else:
            dashboard_map = self.json_helper.load_and_parse_file(
                dashboard_path)
            # print("\n\n>>> dashboard 1: "+str(dashboard_map))
            self.dashboard = Dashboard(dashboard_map)
            # print("\n\n>>> dashboard 2: "+str(self.dashboard))
            # dashboard_map_2 = self.dashboard.encode()
            # print("\n\n>>>dashboard 3: "+str(dashboard_map_2))

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
        dashboard_interval = 60
        if Global.CONFIG in config:
            if Global.OPTIONS in config[Global.CONFIG]:
                option_time = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.TIME, {})
                dashboard_options = option_time.get(Global.DASHBOARD, {})
                dashboard_timeout = dashboard_options.get(Global.TIMEOUT, 60)
                dashboard_interval = dashboard_options.get(Global.INTERVAL, 60)
        return (dashboard_timeout, dashboard_interval)

    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse topics of config file """
        topic = mqtt_config.publish_topics.get(Global.DASHBOARD,
                                               Global.UNKNOWN)
        return topic
