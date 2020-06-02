# logger_py.py - log to console and file

"""

    logger_py - Log messages using python logger module.
    Employes a queue to manage messages to be written.  All threads queue up
    messages but the queue is only written by the main app thread.

The MIT License (MIT)

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

import logging
import logging.handlers

from global_constants import Global

class Logger():
    """
    Logger class - log to console and optionally to a file.
    Uses a queue to ensude thread safe
    """

    def __init__(self, app_name, log_file_name="", log_level="console"):
        """ Initialize """
        # init
        self.app_name = app_name
        self.display_queue = None
        self.log_file_name = log_file_name
        print("LogFile: "+log_file_name)
        self.log_level = self.set_log_level(log_level)
        # set log_level to "console" to only log to console, no file logging
        self.logger = logging.getLogger(self.app_name)
        if self.log_level != Global.LOG_LEVEL_CONSOLE:
            self.logger.setLevel(log_level)
            #set up file logging
            filehandler = logging.handlers.WatchedFileHandler(self.log_file_name)
            filehandler.setLevel(logging.DEBUG)
            fileformatter = logging.Formatter(
                '%(asctime)s %(name)s %(levelname)-8s: %(message)s')
            filehandler.setFormatter(fileformatter)
            self.logger.addHandler(filehandler)
        else:
            self.logger.setLevel(logging.INFO)

        # Set up logging to the console.
        streamhandler = logging.StreamHandler()
        streamhandler.setLevel(log_level)
        streamformatter = logging.Formatter(
            '%(asctime)s %(name)s %(levelname)-8s: %(message)s')
        # streamformatter = logging.Formatter('%(levelname)s: %(message)s')
        streamhandler.setFormatter(streamformatter)
        self.logger.addHandler(streamhandler)

    def set_log_level(self, level):
        """ set log level """
        level = level.upper()
        log_level = Global.LOG_LEVEL_DEBUG
        if level == "DEBUG":
            log_level = Global.LOG_LEVEL_DEBUG
        elif level == "INFO":
            log_level = Global.LOG_LEVEL_INFO
        elif level in ("WARN", "WARNING"):
            log_level = Global.LOG_LEVEL_WARNING
        elif level == "ERROR":
            log_level = Global.LOG_LEVEL_ERROR
        elif level == "CRITICAL":
            log_level = Global.LOG_LEVEL_CRITICAL
        elif level == "CONSOLE":
            log_level = Global.LOG_LEVEL_CONSOLE
        return log_level


    def info(self, new_line):
        """ log a message as an info message """
        self.logger.info(new_line)

    def debug(self, new_line):
        """ log a message as a debug message """
        self.logger.debug(new_line)

    def warn(self, new_line):
        """ log a message as a warning message """
        self.logger.warning(new_line)

    def error(self, new_line):
        """ log a message as an error message """
        self.logger.error(new_line)

    def critical(self, new_line):
        """ log a message as a critcal message """
        self.logger.critical(new_line)

    def write_log_messages(self, log_queue):
        """ write a log message to output """
        level, message = log_queue.get()
        while message is not None:
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
            if self.display_queue is not None:
                #print(">>> "+message)
                if level >= self.log_level:
                    #print(message)
                    self.display_queue.add_message(level, message)
            level, message = log_queue.get()
