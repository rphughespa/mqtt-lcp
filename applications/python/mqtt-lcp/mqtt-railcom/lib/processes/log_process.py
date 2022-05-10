#!/usr/bin/python3
# log_process.py
"""

log_process - a process that logs messages


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

sys.path.append('../../lib')

import logging
import logging.handlers
import colorlog

from utils.global_constants import Global

from processes.base_process import BaseProcess


class LogProcess(BaseProcess):
    """ Class that waits for an event to occur """
    def __init__(self, events=None, queues=None):
        BaseProcess.__init__(self,
                             name="log",
                             events=events,
                             in_queue=queues[Global.LOGGER])
        print("init logger")
        self.display_queue = None
        self.log_file_name = None
        self.logger = None

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        if self.node_name is None:
            print(
                "Logger: !!!! Configureation file error: node name not specified, exiting"
            )
            self.events[Global.SHUTDOWN].set()
        if Global.CONFIG in self.config:
            if Global.LOGGER in self.config[Global.CONFIG]:
                self.log_file_name = self.config[Global.CONFIG][
                    Global.LOGGER].get(Global.FILE, None)

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)
        if self.log_file_name is not None:
            # set up file logging
            self.log_file_name = self.log_file_name.replace(
                "**" + Global.NODE + "**", self.node_name)
            filehandler = logging.handlers.WatchedFileHandler(
                self.log_file_name)
            filehandler.setLevel(logging.DEBUG)
            fileformatter = logging.Formatter(
                '%(asctime)s %(name)s %(levelname)-8s: %(message)s')
            filehandler.setFormatter(fileformatter)
            self.logger.addHandler(filehandler)
        # Set up logging to the console.
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(
            colorlog.ColoredFormatter(
                fmt='%(log_color)s%(levelname)-8s:%(asctime)s %(name)s: %(message)s',
                log_colors={
		            'DEBUG':    'cyan',
		            'INFO':     'green',
		            'WARNING':  'yellow',
		            'ERROR':    'red',
		            'CRITICAL': 'red,bg_white'
	            }
            ))

        console_handler.setLevel(self.log_level)
        console_handler.setLevel(self.log_level)
        self.logger.addHandler(console_handler)


    def process_message(self, new_message=None):
        """ process message from queue """
        (log_level, log_message) = new_message
        # print("())() "+str(log_message))
        self.__write_log_messages(log_level, log_message)

    def __write_log_messages(self, level, message=None):
        """ write a log message to output """
        if message is not None:
            if level >= self.log_level:
                if level == Global.LOG_LEVEL_DEBUG:
                    self.logger.debug(message)
                elif level == Global.LOG_LEVEL_WARNING:
                    self.logger.warning(message)
                elif level == Global.LOG_LEVEL_ERROR:
                    self.logger.error(message)
                elif level == Global.LOG_LEVEL_CRITICAL:
                    self.logger.critical(message)
                else:
                    self.logger.info(message)
