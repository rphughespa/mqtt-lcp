#!/usr/bin/python3
# main.py for mqtt-registry

"""
    mqtt-registry: Manages a registry of info about the layout:

        roster : definition of locos
        layout : definition of track segments
        signals : definition of signals
        switches : definition of track turnouts and other switches
        warrants : definition of layout warrants
        dashboard : collection of last ping times of noeds
        sensors : colection of sensor states

    The program resonds for mqtt cmd/requests for registry info by
    replying with a mqtt cmd/response message.

    The program also periodically publishes out a dt message with fastclock information

    To control the fastclock the program procsses cmd/requests with cmd/responses for:

        fastclock reset
        fastclock pause
        fastclock run

the MIT License (MIT)

Copyright © 2020 richard p hughes

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
sys.path[1] = '../lib'

import time
import random
import datetime
import json

from global_constants import Global
from local_constants import Local

from node_base_mqtt import NodeBaseMqtt
from io_data import IoData

from roster import Roster
from switches import Switches
from warrants import Warrants
from signals import Signals
from layout import Layout
from dashboard import Dashboard
from sensors import Sensors


class MqttRegistry(NodeBaseMqtt):
    """ Application that manages a registry of data objetc used in the networl"""

    def __init__(self):
        super().__init__()
        self.topic_fastclock_pub = None
        self.topic_dashboard_pub = None
        self.topic_backup_sub = None
        self.diff_seconds = 0
        self.fast_seconds = 0
        self.fast_paused = False
        self.fast_incr = 0
        self.fast_ratio = 0
        self.fast_interval = 0
        self.roster = None
        self.switches = None
        self.warrants = None
        self.signals = None
        self.layout = None
        self.dashboard = None
        self.sensors = None
        self.last_fasttime_seconds = 0
        self.topic_ping_sub = None
        self.topic_sensor_sub = None
        self.topic_backup_sub = None
        self.topic_node_pub = None
        self.dashboard_interval = 30
        self.last_dashboard_seconds = 0
        self.backup_path = None

    def initialize_threads(self):
        """ Initializes io threads"""
        super().initialize_threads()
        self.dashboard_interval = int(self.ping_interval * 2)
        self.topic_fastclock_pub = self.publish_topics[Global.FASTCLOCK]
        self.topic_dashboard_pub = self.publish_topics[Global.DASHBOARD]
        self.topic_node_pub = self.publish_topics[Global.NODE]
        self.topic_ping_sub = self.subscribed_topics[Global.PING]
        # print("!!! ping sub: "+self.topic_ping_sub)
        self.topic_sensor_sub = self.subscribed_topics[Global.SENSOR]
        self.topic_backup_sub = self.subscribed_topics[Global.BACKUP]
        # print("!!! backup sub: "+self.topic_backup_sub)
        if Global.CONFIG in self.config:
            if Global.OPTIONS in self.config[Global.CONFIG]:
                if Global.TIME in self.config[Global.CONFIG][Global.OPTIONS]:
                    if Global.FAST in self.config[Global.CONFIG][Global.OPTIONS][Global.TIME]:
                        if Global.RATIO in self.config[Global.CONFIG][Global.OPTIONS][Global.TIME][Global.FAST]:
                            self.fast_ratio = int(self.config[Global.CONFIG][Global.OPTIONS][Global.TIME][Global.FAST][Global.RATIO])
                        if Global.INTERVAL in self.config[Global.CONFIG][Global.OPTIONS][Global.TIME][Global.FAST]:
                            self.fast_interval = int(self.config[Global.CONFIG][Global.OPTIONS][Global.TIME][Global.FAST][Global.INTERVAL])
                if Global.PING in self.config[Global.CONFIG][Global.OPTIONS]:
                    self.ping_interval = self.config[Global.CONFIG][Global.OPTIONS][Global.PING]
                if Global.BACKUP in self.config[Global.CONFIG][Global.OPTIONS]:
                    self.backup_path = self.config[Global.CONFIG][Global.OPTIONS][Global.BACKUP]
        self.roster = Roster(self.log_queue, file_path=Global.DATA+"/"+Global.ROSTER+".json")
        self.switches = Switches(self.log_queue, file_path=Global.DATA+"/"+Global.SWITCHES+".json")
        self.warrants = Warrants(self.log_queue, file_path=Global.DATA+"/"+Global.WARRANTS+".json")
        self.signals = Signals(self.log_queue, file_path=Global.DATA+"/"+Global.SIGNALS+".json")
        self.layout = Layout(self.log_queue, file_path=Global.DATA+"/"+Global.LAYOUT+".json")
        self.dashboard = Dashboard(self.log_queue, file_path=Global.DATA+"/"+Global.DASHBOARD+".json")
        self.sensors = Sensors(self.log_queue, file_path=Global.DATA+"/"+Global.SENSORS+".json")

    def publish_inventory_request(self, io_data):
        """ request inventory from a none """
        now_seconds = self.now_seconds()
        session_id = 'req:'+str(int(now_seconds))
        topic = self.topic_node_pub + "/" + io_data.mqtt_node + "/" + Global.REPORT + "/" +Global.REQ
        new_state_message = self.format_state_body(self.node_name,
                Global.REGISTRY, session_id, None, {Global.REPORT:Global.INVENTORY},
                response_topic=self.topic_self_subscribed+"/"+Global.RES)
        self.send_to_mqtt(topic, new_state_message)
        self.log_queue.add_message("info", Global.PUBLISH+" "+Global.INVENTORY+" "+Global.REQUEST+": "+io_data.mqtt_node)
        self.write_log_messages()

    def publish_dashboard(self):
        """ publish fasttimes broadcast message"""
        now_seconds = self.now_seconds()
        self.dashboard.update_states(now_seconds - 3 - self.ping_interval)
        self.log_queue.add_message("info", Global.PUBLISH +": "+Global.STATE)
        session_id = Global.DT+str(int(now_seconds))
        self.last_dashboard_seconds = now_seconds
        new_message = self.format_state_body(self.node_name,
            Global.REGISTRY, session_id, {Global.REPORT:Global.DASHBOARD}, None,
            metadata=self.dashboard.dump())
        dashboard_topic = self.topic_dashboard_pub
        self.send_to_mqtt(dashboard_topic, new_message)

    def publish_fast_times(self):
        """ publish fasttimes broadcast message"""
        now_seconds = self.now_seconds()
        self.log_queue.add_message("info", Global.PUBLISH +": "+Global.FASTCLOCK)
        session_id = Global.DT+str(int(now_seconds))
        diff_seconds = now_seconds - self.last_fasttime_seconds
        self.last_fasttime_seconds = now_seconds
        if not self.fast_paused:
            self.fast_incr = self.fast_incr + (diff_seconds * self.fast_ratio)
        self.fast_seconds = now_seconds + self.fast_incr
        local_time = time.localtime(now_seconds)
        fast_time = time.localtime(self.fast_seconds)
        fast_ratio = self.fast_ratio
        fast_state = 'run'
        if self.fast_paused:
            fast_state = 'paused'
            fast_ratio = 0
        local_time_dict = {Global.EPOCH: int(now_seconds),
                Global.YEAR : local_time.tm_year,
                Global.MONTH : local_time.tm_mon,
                Global.DAY : local_time.tm_mday,
                Global.HOUR : local_time.tm_hour,
                Global.MINUTES : local_time.tm_min,
                Global.SECONDS : local_time.tm_sec}
        fast_time_dict = {Global.EPOCH: int(self.fast_seconds),
                Global.YEAR : fast_time.tm_year,
                Global.MONTH : fast_time.tm_mon,
                Global.DAY : fast_time.tm_mday,
                Global.HOUR : fast_time.tm_hour,
                Global.MINUTES : fast_time.tm_min,
                Global.SECONDS : fast_time.tm_sec,
                Global.RATIO : fast_ratio}

        fast_message = self.format_state_body(self.node_name, Global.FASTCLOCK, session_id,
                fast_state, None, metadata={Global.CURRENT : local_time_dict,
                Global.FASTCLOCK : fast_time_dict})
        fast_topic = self.topic_fastclock_pub
        self.send_to_mqtt(fast_topic, fast_message)

    def process_received_backup_message(self, _message_topic, io_data):
        """ process backup message received, a node wants to backup its config data """
        backup_node_id = None
        backup_node_config = None
        if io_data.mqtt_message_root == Global.BACKUP:
            backup_node_id = io_data.mqtt_node
            backup_node_config = io_data.mqtt_metadata
            if (backup_node_id is not None) and (backup_node_config is not None):
                # a backup has been received, save meta config to disk
                self.log_queue.add_message("info", Local.MSG_BACKUP_DATA_RECEIVED+" "+backup_node_id)
                timestamp = datetime.datetime.now().isoformat()
                if self.backup_path is not None:
                    file_path = self.backup_path + "/" + backup_node_id + "_" + timestamp + ".json"
                    with open(file_path, 'w') as json_file:
                        json.dump(backup_node_config, json_file)

    def process_received_ping_message(self, _message_topic, io_data):
        """ process ping message received"""
        #print("received ping")
        ping_node_id = None
        if io_data.mqtt_message_root == Global.PING:
            if io_data.mqtt_reported == Global.PING:
                # a ping has been received, store it in dashboard
                # print("ping OK!")
                timestamp = int(self.now_seconds())
                state = Global.RUN
                ping_node_id = io_data.mqtt_node
                if ping_node_id is not None:
                    if ping_node_id != self.node_name:
                        last_ping_time = self.dashboard.get_timestamp(ping_node_id)
                        if last_ping_time == 0:   # first ping from node, get inventory
                            self.publish_inventory_request(io_data)
                    #print("Ping from: "+ping_node_id)
                    self.log_queue.add_message("info", Local.MSG_PING_DATA_RECEIVED+": "+ping_node_id)
                    self.dashboard.update(ping_node_id, timestamp, state)

    def process_received_sensor_message(self, message_topic, io_data):
        """ process sensor message received"""
        self.log_queue.add_message("debug", Global.MSG_REQUEST_MSG_RECEIVED+": "+message_topic)
        if io_data.mqtt_message_root == Global.SENSOR:
            reported = io_data.mqtt_reported
            # a sensor has been received, store it in dashboard
            self.log_queue.add_message("info", Global.RECEIVED+": "+Global.SENSOR)
            node_id = io_data.mqtt_node
            port_id = io_data.mqtt_port
            stype = io_data.mqtt_type
            timestamp = int(self.now_seconds())
            if (node_id is not None) and (port_id is not None):
                self.sensors.update(node_id, port_id, reported, stype, timestamp)

    def process_fastclock_request(self, message_topic, io_data):
        """ process a request to mange fastclock"""
        new_state = "unknown"
        request_ok = False
        if io_data.mqtt_message_root == Global.FASTCLOCK:
            fastclock_value = io_data.get_desired_value_by_key(Global.FASTCLOCK)
            desired_state = io_data.mqtt_desired
            self.log_queue.add_message("debug",
                    Global.FASTCLOCK+': '+Global.STATE+' '+Global.REQ+' : '+str(desired_state))
            if fastclock_value == Global.RESET:
                self.fast_incr = 0
                new_state = Global.RESET
                request_ok = True
            elif fastclock_value == Global.PAUSE:
                self.fast_paused = True
                new_state = Global.PAUSE
                request_ok = True
            elif fastclock_value == Global.RUN:
                self.fast_paused = False
                new_state = Global.RUN
                request_ok = True
        if request_ok:
            state_topic = io_data.mqtt_resp_topic
            state_message = self.format_state_body(self.node_name, Global.FASTCLOCK,
                    io_data.mqtt_resp_topic,
                    {Global.FASTCLOCK:new_state}, desired_state)
            self.send_to_mqtt(state_topic, state_message)
        else:
            error_msg = (Global.UNKNOWN + " " +
                    Global.FASTCLOCK + " "+ Global.STATE+" : ["+ str(io_data.mqtt_desired)+"]")
            self.publish_error_reponse(error_msg, message_topic, io_data)


    def process_roster_request(self, _message_topic, io_data):
        """ process request for roster report """
        new_message = self.format_state_body(self.node_name,
            Global.REGISTRY, io_data.mqtt_session_id, {Global.REPORT:Global.ROSTER}, io_data.mqtt_desired,
            metadata=self.roster.dump())
        self.send_to_mqtt(io_data.mqtt_resp_topic, new_message)

    def process_switches_request(self, _message_topic, io_data):
        """ process request for switches report """
        new_message = self.format_state_body(self.node_name,
            Global.REGISTRY, io_data.mqtt_session_id, {Global.REPORT:Global.SWITCHES}, io_data.mqtt_desired,
            metadata=self.switches.dump())
        self.send_to_mqtt(io_data.mqtt_resp_topic, new_message)

    def process_warrants_request(self, _message_topic, io_data):
        """ process request for warrant report"""
        new_message = self.format_state_body(self.node_name,
            Global.REGISTRY, io_data.mqtt_session_id, {Global.REPORT:Global.WARRANTS}, io_data.mqtt_desired,
            metadata=self.warrants.dump())
        self.send_to_mqtt(io_data.mqtt_resp_topic, new_message)

    def process_signals_request(self, _message_topic, io_data):
        """ process request for signal report"""
        new_message = self.format_state_body(self.node_name,
            Global.REGISTRY, io_data.mqtt_session_id, {Global.REPORT:Global.SIGNALS}, io_data.mqtt_desired,
            metadata=self.signals.dump())
        self.send_to_mqtt(io_data.mqtt_resp_topic, new_message)

    def process_layout_request(self, _message_topic, io_data,):
        """ process request for layout report"""
        new_message = self.format_state_body(self.node_name,
            Global.REGISTRY, io_data.mqtt_session_id, {Global.REPORT:Global.LAYOUT}, io_data.mqtt_desired,
            metadata=self.layout.dump())
        self.send_to_mqtt(io_data.mqtt_resp_topic, new_message)

    def process_dashboard_request(self, _message_topic, io_data):
        """ process request for dashboard report"""
        now_seconds = self.now_seconds()
        self.dashboard.update_states(now_seconds - 3 - self.ping_interval)
        new_message = self.format_state_body(self.node_name,
            Global.REGISTRY, io_data.mqtt_session_id, {Global.REPORT:Global.DASHBOARD}, io_data.mqtt_desired,
            metadata=self.dashboard.dump())
        self.send_to_mqtt(io_data.mqtt_resp_topic, new_message)

    def process_sensors_request(self, _message_topic, io_data):
        """ process request for sensors report"""
        new_message = self.format_state_body(self.node_name,
            Global.REGISTRY, io_data.mqtt_session_id, {Global.REPORT:Global.SENSORS}, io_data.mqtt_desired,
            metadata=self.sensors.dump())
        self.send_to_mqtt(io_data.mqtt_resp_topic, new_message)

    def process_report_request(self, message_topic, io_data):
        """ process a request for repoting"""
        request_ok = False
        if io_data.mqtt_message_root == Global.REGISTRY:
            report_value = io_data.get_desired_value_by_key(Global.REPORT)
            desired_state = io_data.mqtt_desired
            self.log_queue.add_message("debug",
                    Global.REGISTRY+': '+Global.STATE+' '+Global.REQ+' : '+str(desired_state))
            if report_value is not None:
                if report_value == Global.ROSTER:
                    self.process_roster_request(message_topic, io_data)
                    request_ok = True
                elif report_value == Global.SWITCHES:
                    self.process_switches_request(message_topic, io_data)
                    request_ok = True
                elif report_value == Global.WARRANTS:
                    self.process_warrants_request(message_topic, io_data)
                    request_ok = True
                elif report_value == Global.SIGNALS:
                    self.process_signals_request(message_topic, io_data)
                    request_ok = True
                elif report_value == Global.LAYOUT:
                    self.process_layout_request(message_topic, io_data)
                    request_ok = True
                elif report_value == Global.DASHBOARD:
                    self.process_dashboard_request(message_topic, io_data)
                    request_ok = True
                elif report_value == Global.SENSORS:
                    self.process_sensors_request(message_topic, io_data)
                    request_ok = True
        if not request_ok:
            error_msg = (Global.UNKNOWN + " " +
                    Global.REPORT + " "+ Global.STATE+" : ["+ str(io_data.mqtt_desired)+"]")
            self.publish_error_reponse(error_msg, message_topic, io_data)

    def process_request_message(self, message_topic, io_data):
        """ prosess a request message"""
        self.log_queue.add_message("info", Global.MSG_REQUEST_MSG_RECEIVED+ message_topic)
        if message_topic != self.topic_broadcast_subscribed:
            # broadcasts handled in parent class, node_mqtt
            if message_topic.endswith("/"+Global.FASTCLOCK+"/"+Global.REQ):
                self.process_fastclock_request(message_topic, io_data)
            elif message_topic.endswith("/"+Global.REPORT+"/"+Global.REQ):
                self.process_report_request(message_topic, io_data)
            else:
                self.log_queue.add_message("critical", Global.MSG_UNKNOWN_REQUEST+ message_topic)
                self.publish_error_reponse(Global.MSG_UNKNOWN_REQUEST, message_topic, io_data)

    def process_response_message(self, message_topic, _io_data):
        """ process response message"""
        # add code to process inventory responses
        self.log_queue.add_message("debug", Global.MSG_RESPONSE_RECEIVED + message_topic)

    def received_from_mqtt(self, message_topic, io_data):
        """ process subscribed messages"""
        self.log_queue.add_message("debug", "mqtt nessage: "+message_topic)
        if message_topic.startswith(Global.CMD+"/"):
            if message_topic.endswith("/"+Global.RES):
                self.process_response_message(message_topic, io_data)
            else:
                self.process_request_message(message_topic, io_data)
        elif message_topic.startswith(self.topic_ping_sub):
            # print("found ping")
            self.process_received_ping_message(message_topic, io_data)
        elif message_topic.startswith(self.topic_backup_sub):
            self.process_received_backup_message(message_topic, io_data)
        elif message_topic.startswith(self.topic_sensor_sub):
            self.process_received_sensor_message(message_topic, io_data)
        else:
            self.log_queue.add_message("critical", Global.MSG_UNKNOWN_REQUEST + message_topic)

    def loop(self):
        """ main process loop"""
        self.log_queue.add_message("critical", Global.READY)
        self.last_ping_seconds = self.now_seconds()
        self.last_fasttime_seconds = self.now_seconds()
        while not self.shutdown_app:
            try:
                time.sleep(0.5)
                self.write_log_messages()
                #print("do input")
                # self.log_queue.add_message("debug", "process input")
                self.process_input()
                # self.log_queue.add_message("debug", " ... process input completed")
                #print("... done")
                now_seconds = self.now_seconds()
                if (now_seconds - self.last_ping_seconds) > self.ping_interval:
                    #print("process pub ping")
                    self.publish_ping_broadcast()
                    #print("... proces ping pub done")
                if (now_seconds - self.last_fasttime_seconds) > self.fast_interval:
                    #print("process pub ping")
                    self.publish_fast_times()
                    #print("... proces ping pub done")
                if (now_seconds - self.last_dashboard_seconds) > self.dashboard_interval:
                    self.publish_dashboard()

            except KeyboardInterrupt:
                self.shutdown_app = True

# this app normally starts at boot, allow tiem for mqtt-broker to initialize
time.sleep(30+random.randint(0, 2)) # delay a bit less less than other nodes

node = MqttRegistry()
node.initialize_threads()
time.sleep(2)
node.log_queue.add_message("critical", node.node_name+" "+Global.MSG_STARTING)
node.write_log_messages()

node.loop()

end_seconds = node.now_seconds()
node.log_queue.add_message("critical", node.node_name+" "+Global.MSG_COMPLETED)
node.log_queue.add_message("critical", node.node_name+" "+Global.MSG_EXITING)
node.write_log_messages()
node.shutdown_threads()
node.write_log_messages()
sys.exit(0)
