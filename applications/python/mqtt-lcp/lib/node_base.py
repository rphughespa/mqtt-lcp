# node_base.py - base class for nodes
"""

    node_base - Base class used by nodes.

The MIT License (MIT)

Copyright 2020 richard p hughes

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

import time
import sys
# platforms for esp32 = esp32, for lobo esp32 = esp32_LoBo, for pi = linux

if sys.platform.startswith("esp32_LoBo"):
    import utime
    import ujson
    import uio
    from logger_go import Logger
    from netservices import NetServices
    #from display_go import DisplayGo
    from odroid_go import GO
elif sys.platform.startswith("esp32"):
    import utime
    import ujson
    import uio
    from logger_esp32 import Logger
    from netservices import NetServices
else:
    import json
    from logger_py import Logger

# sys.path[1] = '../lib'



from log_queue import LogQueue
from global_constants import Global
from display_queue import DisplayQueue


class NodeBase():
    """
        Base class for node programs
    """

    def __init__(self):
        """ Initialize """
        self.shutdown_app = False
        self.config = None
        self.log_queue = None
        self.log_file = None
        self.log_level = None
        self.logger = None
        self.display_queue =  None
        self.node_name = None
        self.netservices = None
        self.global_data = {}
        with open('config.json') as json_file:
            if sys.platform.startswith("esp32"):
                self.config = ujson.load(json_file)
            else:
                self.config = json.load(json_file)
        if self.config is None:
            print("! Config ERROR !")
            assert (self.config is not None), "Error: config.json!"
        if sys.platform.startswith("esp32_LoBo"):
            self.lcd = GO.lcd

    def initialize_threads(self):
        """ init threads """
        # see if we hve a display configured
        self.node_name = self.config[Global.CONFIG][Global.NODE][Global.NAME]
        self.parse_display_config_data()
        self.start_logging()
        if sys.platform.startswith("esp32"):
            self.initialize_network()

    def start_logging(self):
        """ use a queue of log messages for threaded routines """
        self.log_queue = LogQueue()
        self.log_file = ""
        self.log_level = "console"
        if Global.LOGGER in self.config[Global.CONFIG]:
            if Global.FILE in self.config[Global.CONFIG][Global.LOGGER]:
                self.log_file = self.config[Global.CONFIG][Global.LOGGER][Global.FILE]
                self.log_file = self.log_file.replace("**node**", self.node_name)
            if Global.LEVEL in self.config[Global.CONFIG][Global.LOGGER]:
                self.log_level = self.config[Global.CONFIG][Global.LOGGER][Global.LEVEL]
            if sys.platform.startswith("esp32_LoBo"):
                self.logger = Logger(self.lcd, self.node_name, log_level=self.log_level,
                        log_file_name=self.log_file)
                self.logger.set_colors(self.lcd.WHITE, self.lcd.BLACK, self.lcd.RED)
            else:
                print(str(self.log_file))
                self.logger = Logger(self.node_name,
                        log_file_name=self.log_file,
                        log_level=self.log_level)
            self.logger.display_queue = self.display_queue
        self.log_queue.add_message("debug", self.node_name+" "+Global.START+" ...")

    def parse_display_config_data(self):
        """ Parse out display I2C items from config json data to see if a display is defined """
        if sys.platform.startswith("esp32_LoBo"):
            # self.display = DisplayGo()
            pass
        elif Global.IO in self.config[Global.CONFIG]:
            if Global.I2C in self.config[Global.CONFIG][Global.IO]:
                config_data = self.config[Global.CONFIG][Global.IO][Global.I2C]
                for i2c_node in config_data:
                    if Global.DEVICE_TYPE in i2c_node:
                        dev_type = i2c_node[Global.DEVICE_TYPE]
                        if dev_type == Global.DISPLAY:
                            self.display_queue = DisplayQueue()
                        elif dev_type == Global.MUX:
                            # check devices on mux
                            if Global.PORTS in i2c_node:
                                for port in i2c_node[Global.PORTS]:
                                    if Global.DEVICE_TYPE in port:
                                        port_dev_type = port[Global.DEVICE_TYPE]
                                        if port_dev_type == Global.DISPLAY:
                                            self.display_queue = DisplayQueue()

    def write_log_messages(self):
        """ write log message """
        if self.logger is not None and self.log_queue is not None:
            self.logger.write_log_messages(self.log_queue)
        else:
            # we don't have a logger, so just empty log_queue
            _level, message = self.log_queue.get()
            while message is not None:
                _level, message = self.log_queue.get()

    def initialize_network(self):
        """ init network """
        if sys.platform.startswith("esp32"):
            self.net_services = NetServices(self.log_queue, self.config)
            self.net_services.start_wifi()
            self.write_log_messages()
            if self.net_services.is_connected():
                if sys.platform.startswith("esp32_LoBo"):
                    self.net_services.start_net_time()
                _mdns = self.net_services.get_mdns()
            self.write_log_messages()
        else:
            pass

    def dstTime(self):
        """ set dst time """
        year = time.localtime()[0] #get current year
        # print(year)
        HHMarch = time.mktime((year,3 ,(14-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of March change to DST
        HHNovember = time.mktime((year,10,(7-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of November change to EST
        # print(HHNovember)
        now=time.time()
        if now < HHMarch : # we are before last sunday of march
            dst=time.localtime(now-18000) # EST: UTC-5H
        elif now < HHNovember : # we are before last sunday of october
            dst=time.localtime(now-14400) # DST: UTC-4H
        else: # we are after last sunday of october
            dst=time.localtime(now-18000) # EST: UTC-5H
        return(dst)

    def daylight(self, now, offset):
        """ daylight time """
        rt = time.localtime(now)
        nows = now + (11 - rt[1]) * 2592000 # about mid November
        # work back to find Sunday Oct
        while time.localtime(nows)[1] != 10: #Oct
            nows -= 86400
        while time.localtime(nows)[6] != 6: #Sun
            nows -= 86400
        nowsOct = nows
        # work back to find Sunday Mar
        while time.localtime(nows)[1] != 3: #Mar
            nows -= 86400
        while time.localtime(nows)[6] != 6: #Sun
            nows -= 86400
        nowsMar = nows
        # saving is used between dates
        if (now > nowsMar) and (now < nowsOct):
            now += (3600 * offset)
        return now

    def now_seconds(self):
        """ calc now seconds """
        now_sec = 0
        if sys.platform.startswith("esp32_LoBo"):
            now_sec = time.mktime(time.localtime())
        elif sys.platform.startswith("esp32"):
            # to-do adj for 200 vs 1970 epoch add 946684800?
            now_sec = time.mktime(time.localtime()) + 946684800
        else:
            now_sec = time.mktime(time.localtime())
        return now_sec

