#!/usr/bin/python3
# base_process.py
"""

base_process - parent class for processes


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
import traceback
import locale
import time
import os.path
from multiprocessing import Process
import sys

sys.path.append('../../lib')

from utils.utility import Utility
from utils.json_utils import JsonUtils
from utils.yaml_utils import YamlUtils
from utils.global_constants import Global
from structs.io_config import IoConfig


INACTIVE_LOOP_WAIT = 0.025
# INACTIVE_LOOP_WAIT = 1
MAX_MESSAGE_BLOCK = 5


class SendAfterMessage(object):
    """ class to store a message to be deliverd after a delay """

    def __init__(self, topic=None, message_body=None, send_after=0):
        self.key = 0  # unique identifer for this message
        self.topic = topic
        self.message_body = message_body
        self.send_after = send_after  # delay in milliseconds
        self.expires = 0

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"


class BaseProcess(Process):
    """ base class for processes """

    def __init__(self,
                 name="base",
                 events=None,
                 suffix=None,
                 in_queue=None,
                 app_queue=None,
                 log_queue=None):
        Process.__init__(self)
        self.name = name
        self.events = events
        self.in_queue = in_queue
        self.log_queue = log_queue
        self.app_queue = app_queue
        self.reversed_globals = self.__reverse_globals()
        self.config = None
        self.io_config = None
        self.suffix = suffix
        self.node_name = None
        self.host_name = None
        # store at this level so all process can see it
        self.log_level = Global.LOG_LEVEL_INFO
        self.is_logging_debug = False
        self.send_after_message_queue = {}
        self.__load_config_file()
        self.__load_host_name()
        self.__parse_node_name()
        self.io_config = IoConfig(self.config, self.log_queue)
        # print("base ok: " + str(self.name))

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def run(self):
        """ loop reading input from queue """
        # print(">>> run: " + str(self.name))
        try:
            self.initialize_process()
            # max messages to process in a row
            # alows other processing to happen
            # even if a messages are waiting to be processed
            while not self.events[Global.SHUTDOWN].is_set():
                new_message = None
                try:
                    new_message = self.in_queue.get(True, 0.1)  # was 0.03
                    #if self.in_queue.empty():
                    #    time.speep(0.01)
                    #else:
                    #    new_message = self.in_queue.get()
                except Exception as _error:
                    # ignore exception from timeout on get
                    pass
                if new_message is not None:
                    # print(">>> queue " + str(self.name) + ": " + str(new_message))
                    if not self.preprocess_message(new_message):
                        self.process_message(new_message)
                else:
                    self.process_other()
                    self.__process_send_after_messages()

            # print(">>> shutdown from base: " + str(self.name))
            self.shutdown_process()
        except Exception as exc:
            print("!!! Exception: " + str(exc))
            traceback.print_exc()

    def initialize_process(self):
        """ initialize the process
        --- override in derived class """
        print("base init start: [ " + str(self.node_name) + " ] ... [ " +
              str(self.name) + " ]")
        if Global.CONFIG in self.config:
            if Global.LOGGER in self.config[Global.CONFIG]:
                log_level = self.config[Global.CONFIG][Global.LOGGER].get(
                    Global.LEVEL, None)
        self.log_level = self.__set_log_level(log_level)
        #print(">>> log level:"+str(self.log_level))
        if self.log_level == Global.LOG_LEVEL_DEBUG:
            self.is_logging_debug = True
        #print(">>> log level:"+str(self.is_logging_debug))

    def preprocess_message(self, _new_message):
        """ preprocess message before normal process.
            Return True if message has been consummed and no further processing needed """
        return False

    def process_message(self, _new_message):
        """ process a new message
        --- override in derived class """
        return False

    def process_other(self):
        """ do processing other than a new message received
        --- override in derived class """
        pass

    def shutdown_process(self):
        """ shutdown the process
        --- override in derived class """
        pass

    def send_after(self, send_after_message):
        """ queue message to be send after a delay """
        # print(">>> send after: "+str(topic)+" ... "+str(send_after))
        key = Utility.now_milliseconds()
        loop = 10
        while loop > 0:
            if key in self.send_after_message_queue:
                # key already in use, try again
                key += 1
                loop -= 1
            else:
                # print(">>> add to send after queue: " +
                #     str(send_after_message.topic))
                send_after_message.key = key
                send_after_message.expires = Utility.now_milliseconds(
                ) + send_after_message.send_after
                self.send_after_message_queue[key] = send_after_message
                break
        if loop == 0:
            # could not add message to queue
            self.log_error("Error: can not add send after message to queue: " +
                           str(send_after_message.topic))

    def log_debug(self, message=None):
        """ log a debug message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_DEBUG, self.name + ": " + message))

    def log_info(self, message=None):
        """ log an info message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_INFO, self.name + ": " + message))

    def log_warning(self, message=None):
        """ log an warn message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_WARNING, self.name + ": " + message))

    def log_error(self, message=None):
        """ log an error message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_ERROR, self.name + ": " + message))

    def log_critical(self, message=None):
        """ log an critical message """
        if self.log_queue is not None:
            self.log_queue.put(
                (Global.LOG_LEVEL_CRITICAL, self.name + ": " + message))

    def log_unexpected_message(self, msg_body=None):
        """ log an unexpected message """
        self.log_warning("base: Unexpected Message Received: " + str(msg_body))

    def send_to_application(self, message):
        """ send message to application queue """
        self.app_queue.put(message)

    #
    # private functions
    #

    def __reverse_globals(self):
        return Global.generate_reversed_list()

    def __process_send_after_messages(self):
        """ process expired send after message to message queue """
        # check to see if send after  queue has any messages in it
        now = Utility.now_milliseconds()
        if self.send_after_message_queue:
            message_keys = list(self.send_after_message_queue.keys())
            for key in message_keys:
                send_after_message = self.send_after_message_queue[key]
                if send_after_message.expires < now:
                    # print(">>> process send after:" +
                    #      str(send_after_message.topic))
                    # message wait time has expired, post it to message queue
                    self.in_queue.put((send_after_message.topic,
                                       send_after_message.message_body))
                    # clean up, remove message from send_after queue
                    del self.send_after_message_queue[key]

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

    def __parse_node_name(self):
        """ parse node_name from config data """
        # print(">>> config: " + str(self.config))
        if Global.CONFIG in self.config:
            if Global.NODE in self.config[Global.CONFIG]:
                self.node_name = self.config[Global.CONFIG][Global.NODE].get(
                    Global.NAME, None)
        if self.node_name is not None and self.suffix is not None:
            self.node_name = self.node_name.replace(
                "**" + Global.SUFFIX + "**", self.suffix)
        if self.node_name is not None and self.host_name is not None:
            self.node_name = self.node_name.replace("**" + Global.HOST + "**",
                                                    self.host_name)
        # print(">>> Node: " + str(self.node_name))

    def __load_host_name(self):
        """ load unix host name """
        response = None
        with open('/etc/hostname',
                  encoding=locale.getpreferredencoding(False)) as f:
            response = (f.readlines()[0]).strip()
            # print(str(response))
            self.host_name = response

    def __set_log_level(self, level):
        """ set log level """
        log_level = Global.LOG_LEVEL_DEBUG
        if level == Global.DEBUG:
            log_level = Global.LOG_LEVEL_DEBUG
        elif level == Global.INFO:
            log_level = Global.LOG_LEVEL_INFO
        elif level == Global.WARNING:
            log_level = Global.LOG_LEVEL_WARNING
        elif level == Global.ERROR:
            log_level = Global.LOG_LEVEL_ERROR
        elif level == Global.CRITICAL:
            log_level = Global.LOG_LEVEL_CRITICAL
        return log_level
