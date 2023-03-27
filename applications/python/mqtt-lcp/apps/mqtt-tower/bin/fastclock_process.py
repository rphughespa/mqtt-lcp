#!/usr/bin/python3
# fastclock_process.py
"""


fastclock_process - maintains and published a fast clock




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

import datetime

from structs.io_data import IoData
from structs.mqtt_config import MqttConfig
from utils.global_constants import Global
from utils.global_synonyms import Synonyms
from utils.utility import Utility

from processes.base_process import BaseProcess
from processes.base_process import SendAfterMessage


class FastclockProcess(BaseProcess):
    """ Class that maintain and publishes a fastclock """
    def __init__(self, events=None, queues=None):
        super().__init__(name="fastclock",
                         events=events,
                         in_queue=queues[Global.FASTCLOCK],
                         log_queue=queues[Global.LOGGER])
        self.events = events
        self.mqtt_config = None
        self.app_queue = queues[Global.APPLICATION]
        self.fastclock_topic = Global.UNKNOWN
        self.fastclock_interval = 30
        self.fastclock_ratio = 2
        self.fastclock_seconds = 0
        self.fastclock_last_seconds = 0
        self.fastclock_paused = False
        self.fastclock_incr = 0

    def initialize_process(self):
        """ load data from file system """
        super().initialize_process()
        self.mqtt_config = MqttConfig(self.config, self.node_name,
                                      self.host_name, self.log_queue)
        (self.fastclock_interval, self.fastclock_ratio)\
             = self.__parse_time_options_config(self.config)
        (self.fastclock_topic) \
             = self.__parse_mqtt_options_config(self.mqtt_config)
        if self.fastclock_interval > 0:
            self.__create_fastclock_send_after()
            self.__publish_fastclock()

    def process_message(self, new_message):
        """ process received messages """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            (msg_type, msg_body) = new_message
            if msg_type == Global.FASTCLOCK:
                self.__create_fastclock_send_after()
                self.__publish_fastclock()
                msg_consummed = True
            elif msg_type == Global.REQUEST:
                self.log_info("Fastclock: " + str(msg_body.mqtt_desired))
                (reported, metadata) = self.__process_request(msg_body)
                self.app_queue.put(
                    (Global.PUBLISH, {Global.TYPE: Global.RESPONSE, Global.REPORTED: reported, \
                        Global.METADATA: metadata, Global.BODY: msg_body}))
                msg_consummed = True
        return msg_consummed

    #
    # private functions
    #

    def __process_request(self, msg_body):
        """ process request to modify fastclock """
        change_desired = msg_body.get_desired_value_by_key(Global.FASTCLOCK)
        reported = {
            Global.FASTCLOCK: Synonyms.desired_to_reported(change_desired)
        }
        metadata = None
        if change_desired == Global.RUN:
            self.fastclock_paused = False
        elif change_desired == Global.PAUSE:
            self.fastclock_paused = True
        elif change_desired == Global.RESET:
            self.fastclock_incr = 0
            self.fastclock_paused = False
        else:
            reported = {Global.FASTCLOCK: Global.ERROR}
            metadata = {
                Global.MESSAGE:
                Global.UNKNOWN + " " + Global.DESIRED + ": " +
                str(change_desired)
            }
        self.__publish_fastclock()
        return (reported, metadata)

    def __publish_fastclock(self):
        """ publish fasttimes broadcast message"""
        now_seconds = Utility.now_seconds()

        self.log_debug(Global.PUBLISH + ": " + Global.FASTCLOCK)

        if not self.fastclock_paused:
            diff_seconds = 0
            if self.fastclock_last_seconds > 0:
                diff_seconds = now_seconds - self.fastclock_last_seconds
            self.fastclock_last_seconds = now_seconds
            self.fastclock_incr = self.fastclock_incr + (diff_seconds *
                                                         self.fastclock_ratio)
            self.fastclock_seconds = now_seconds + self.fastclock_incr

        local_time_epoch = now_seconds
        local_time = datetime.datetime.fromtimestamp(
            local_time_epoch).isoformat()

        fast_time_epoch = self.fastclock_seconds
        fast_time = datetime.datetime.fromtimestamp(
            fast_time_epoch).isoformat()

        fast_state = Global.RUN
        fast_ratio = self.fastclock_ratio
        if self.fastclock_paused:
            fast_state = Global.PAUSED
            fast_ratio = 0
        current_map = {
            Global.EPOCH: local_time_epoch,
            Global.DATETIME: local_time
        }
        fast_time_map = {
            Global.EPOCH: fast_time_epoch,
            Global.DATETIME: fast_time
        }
        metadata = {
            Global.FASTCLOCK: fast_time_map,
            Global.CURRENT: current_map,
            Global.RATIO: fast_ratio
        }
        new_message = IoData()
        new_message.mqtt_message_root = Global.FASTCLOCK
        new_message.mqtt_metadata = metadata
        new_message.mqtt_port_id = Global.FASTCLOCK
        new_message.mqtt_reported = fast_state
        # print(">>> ... :" + str(new_message)+"\n")
        self.app_queue.put(
            (Global.PUBLISH, {Global.TYPE:Global.DATA, \
                    Global.TOPIC: self.fastclock_topic, Global.BODY: new_message}))

    def __create_fastclock_send_after(self):
        """ setup a send after message for fastclock """
        now_seconds = Utility.now_seconds()
        seconds_to_next_fastclock = self.fastclock_interval
        if self.fastclock_interval == 60:
            # publish on the minute
            # reound time up to next minute
            next_minute = Utility.now_seconds_rounded_up(60)
            # calc how many seconds until next minute
            seconds_to_next_fastclock = next_minute - now_seconds
            if seconds_to_next_fastclock < 1:
                seconds_to_next_fastclock = self.fastclock_interval
        # convert to millseconds
        milliseconds_to_next_fastclock = seconds_to_next_fastclock * 1000
        fastclock_send_after_message = SendAfterMessage(Global.FASTCLOCK, None, \
                        milliseconds_to_next_fastclock)
        # print(">>> starting fastclock " + str(self.fastclock_interval))
        self.send_after(fastclock_send_after_message)

    def __parse_time_options_config(self, config):
        """ parse time options section of config file """
        fastclock_interval = 10
        fastclock_ratio = 4
        if Global.CONFIG in config:
            if Global.OPTIONS in config[Global.CONFIG]:
                option_time = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.TIME, {})
                fastclock_options = option_time.get(Global.FASTCLOCK, {})
                fastclock_interval = fastclock_options.get(Global.INTERVAL, 10)
                fastclock_ratio = fastclock_options.get(Global.RATIO, 4)
        return (fastclock_interval, fastclock_ratio)

    def __parse_mqtt_options_config(self, mqtt_config):
        """ parse topics section of config file """
        topic = mqtt_config.publish_topics.get(Global.FASTCLOCK,
                                               Global.UNKNOWN)
        return topic
