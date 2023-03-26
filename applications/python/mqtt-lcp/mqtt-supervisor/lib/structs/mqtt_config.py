#!/usr/bin/python3
# mqtt_config.py
"""
    MqttConfig- helper class that is used when passing mqtt config items from config json file

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
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import sys

sys.path.append('../../lib')

from utils.global_constants import Global


class MqttConfig(object):
    """ Data class for Mqtt Config data """
    def __init__(self,
                 config=None,
                 node_name=None,
                 host_name=None,
                 log_queue=None):
        self.node_name = node_name
        self.config = config
        self.host_name = host_name
        self.log_queue = log_queue
        self.broker = None
        self.user_name = None
        self.user_password = None
        self.subscribe_topics = {}
        self.publish_topics = {}
        self.other_topics = {}
        self.fixed_subscribe_topics = {}
        self.__parse_mqtt_configs()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def __parse_mqtt_configs(self):
        """ parse various mqtt topics fron config data """
        if Global.CONFIG in self.config:
            if Global.IO in self.config[Global.CONFIG]:
                if Global.MQTT in self.config[Global.CONFIG][Global.IO]:
                    self.broker = self.config[Global.CONFIG][Global.IO][
                        Global.MQTT].get(Global.BROKER, None)
                    self.user_name = self.config[Global.CONFIG][Global.IO][
                        Global.MQTT].get(Global.USER, None)
                    self.user_password = self.config[Global.CONFIG][Global.IO][
                        Global.MQTT].get(Global.PASSWORD, None)
        if Global.CONFIG in self.config:
            if Global.IO in self.config[Global.CONFIG]:
                if Global.MQTT in self.config[Global.CONFIG][Global.IO]:

                    if Global.SUB_TOPICS in self.config[Global.CONFIG][
                            Global.IO][Global.MQTT]:
                        sub_topics = self.config[Global.CONFIG][Global.IO][
                            Global.MQTT][Global.SUB_TOPICS]
                        self.__parse_sub_topics(sub_topics)
                        self.__fix_subscribe_topics()

                    if Global.PUB_TOPICS in self.config[Global.CONFIG][
                            Global.IO][Global.MQTT]:
                        pub_topics = self.config[Global.CONFIG][Global.IO][
                            Global.MQTT][Global.PUB_TOPICS]
                        self.__parse_pub_topics(pub_topics)

                    if Global.OTHER_TOPICS in self.config[Global.CONFIG][
                            Global.IO][Global.MQTT]:
                        other_topics = self.config[Global.CONFIG][Global.IO][
                            Global.MQTT][Global.OTHER_TOPICS]
                        self.__parse_other_topics(other_topics)

    def __parse_sub_topics(self, sub_topics=None):
        """ parse subscribe topics """
        # print("sub_topics is a "+str(type(sub_topics)))
        for key, topic in sub_topics.items():
            #print("key is a "+str(type(key))+" ... "+key)
            #print("topic is a "+str(type(topic))+" ... "+topic)
            topic_topic = topic.replace("**" + Global.NODE + "**",
                                        self.node_name)
            if self.log_queue is not None:
                self.log_queue.put(
                    (Global.LOG_LEVEL_INFO, "topics: " + Global.SUBSCRIBE +
                     ": " + key + ", " + topic_topic))
            self.subscribe_topics.update({key: topic_topic})

    def __parse_pub_topics(self, pub_topics=None):
        """ parse subscribe topics """
        for key, topic in pub_topics.items():
            topic_topic = topic.replace("**" + Global.NODE + "**",
                                        self.node_name)
            if self.log_queue is not None:
                self.log_queue.put(
                    (Global.LOG_LEVEL_INFO, "topics: " + Global.PUBLISH +
                     ": " + key + ", " + topic_topic))
            self.publish_topics.update({key: topic_topic})

    def __parse_other_topics(self, other_topics=None):
        """ parse other topics """
        for key, topic in other_topics.items():
            topic_topic = topic.replace("**" + Global.NODE + "**",
                                        self.node_name)
            if self.log_queue is not None:
                self.log_queue.put(
                    (Global.LOG_LEVEL_DEBUG,
                     Global.OTHER_TOPICS + ": " + key + ", " + topic_topic))
            self.other_topics.update({key: topic_topic})

    def __fix_subscribe_topics(self):
        """ remove wildcards from subscribe topics """
        self.fixed_subscribe_topics = {}
        for _i, (key, topic) in enumerate(self.subscribe_topics.items()):
            self.fixed_subscribe_topics.update(
                {key: topic.replace("/+", "").replace("/#", "")})
