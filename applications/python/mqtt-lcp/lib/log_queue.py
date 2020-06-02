# log_queue.py

"""

    log_queue.py - a queue used to manage log entries

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



import sys
if sys.platform.startswith('esp32'):
    from queue_esp32 import Queue
else:
    from queue_py import Queue

from global_constants import Global

class LogQueue:
    """ A class to manage log entries"""

    def __init__(self):
        self.queue = Queue(500)

    def get(self):
        """ Get next log entry"""
        message = None
        level = None
        if not self.queue.empty():
            msg_dict = self.queue.get()
            if "message" in msg_dict:
                message = msg_dict["message"]
            if "level" in msg_dict:
                level = msg_dict["level"]
        return level, message

    def convert_log_level(self, log_level_string):
        level_code = Global.LOG_LEVEL_DEBUG
        level_string_upper = log_level_string.upper()
        if level_string_upper == "CRITICAL":
            level_code = Global.LOG_LEVEL_CRITICAL
        elif level_string_upper == "ERROR":
            level_code = Global.LOG_LEVEL_ERROR
        elif level_string_upper == "WARNING":
            level_code = Global.LOG_LEVEL_WARNING
        elif level_string_upper == "INFO":
            level_code = Global.LOG_LEVEL_INFO
        elif level_string_upper == "DEBUG":
            level_code = Global.LOG_LEVEL_DEBUG
        return level_code

    def add_message(self, log_level, message):
        """ Add an entry to log queue"""
        if isinstance(log_level, int):
            log_level_code = log_level
        else:
            log_level_code = self.convert_log_level(log_level)
        self.queue.put({"level":log_level_code, "message": message})
