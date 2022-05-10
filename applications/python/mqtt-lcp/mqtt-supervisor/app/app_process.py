#!/usr/bin/python3
# appe_process.py
"""


app_process - the application process for mqtt_supervisor


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

from subprocess import call
import time
import locale

from processes.base_mqtt_process import BaseMqttProcess
from utils.global_constants import Global


class AppProcess(BaseMqttProcess):
    """ Class that waits for an event to occur """
    def __init__(self, events=None, queues=None):
        super().__init__(name="app",
                         events=events,
                         in_queue=queues[Global.APPLICATION],
                         mqtt_queue=queues[Global.MQTT],
                         log_queue=queues[Global.LOGGER])
        self.shutdown_command = None
        self.reboot_command = None
        self.info_command = None
        self.log_info("Starting")
        # print(">>> app start init: " + str(self.name))

    def initialize_process(self):
        """ initialize the process """
        # print(">>> app init start")
        super().initialize_process()
        # print(">>> app super init OK")
        (self.shutdown_command, self.reboot_command, self.info_command) \
            = self.__parse_options_config(self.config)
        if self.shutdown_command is None or self.reboot_command is None:
            self.log_critical(
                "!!!! Configureation file error: reboot and shutdown commands not found, exiting"
            )
            time.sleep(2)  # allow time for logger to write
            self.events[Global.SHUTDOWN].set()
        # print(">>> app init OK")

    def process_message(self, new_message=None):
        """ Process received message """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            msg_consummed = True
        return msg_consummed

    def process_other(self):
        """ perform other none message relared tasks """
        super().process_other()
        _now = time.mktime(time.localtime())
        # if now > self.exit_time:
        #    print("crashing app_process")
        #    raise ValueError("app_process - time expired")

    def publish_ping_message(self, _metadata=None):
        """ override normal pin, add sysinfo to metdata """
        meta = None
        if self.info_command is not None:
            commands = self.info_command.split("&&")
            meta = {}
            for command in commands:
                if command.strip():
                    call(command + '> /var/tmp/sysinfo.txt', shell=True)
                    with open(
                            '/var/tmp/sysinfo.txt',
                            encoding=locale.getpreferredencoding(False)) as f:
                        sysinfo = f.readlines()
                        if "landscape-sysinfo" in command:
                            meta.update(
                                self.__parse_landscape_command(sysinfo))
                        elif "vcgencmd" in command:
                            meta.update(
                                self.__parse_landscape_command(sysinfo))
                        else:
                            meta.update(
                                {"sys info": sysinfo.replace("\n", ' ')})

        super().publish_ping_message(meta)

    def process_request_shutdown_message(self, msg_body=None):
        """ process request shutdown message """
        self.log_critical(
            "Shutdown Request received, shutting down, waiting for other apps to terminate ..."
        )
        time.sleep(30)
        self.log_critical("Shutdown computer ...")
        call(self.shutdown_command, shell=True)
        # call super method to do default processing
        super().process_request_shutdown_message(msg_body)
        self.events[Global.SHUTDOWN].set()

    def process_request_reboot_message(self, msg_body=None):
        """ process request reboot message """
        self.log_critical(
            "Reboot Request received, rebooting, waiting for other apps to terminate ..."
        )
        time.sleep(30)
        self.log_critical("Rebooting computer ...")
        call(self.reboot_command, shell=True)
        # call super method to do default processing
        super().process_request_reboot_message(msg_body)
        self.events[Global.SHUTDOWN].set()

    def process_request_registry_message(self, msg_body=None):
        """ process request registry message """
        report_desired = msg_body.get_desired_value_by_key(Global.REPORT)
        if report_desired == Global.INVENTORY:
            self.report_inventory(msg_body=msg_body)
        else:
            self.log_unexpected_message(msg_body=msg_body)

    def __parse_options_config(self, config):
        """ parse options section of config file """
        shutdown = None
        reboot = None
        info = None
        if Global.CONFIG in config:
            if Global.OPTIONS in config[Global.CONFIG]:
                shutdown = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.SHUTDOWN_COMMAND, None)
                reboot = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.REBOOT_COMMAND, None)
                info = config[Global.CONFIG][Global.OPTIONS].get(
                    Global.INFO_COMMAND, None)
        return (shutdown, reboot, info)

    def __parse_landscape_command(self, sysinfo):
        """ parse the results from lanscape-sysinfo command """
        # print(">>> : "+str(sysinfo))
        info_map = {"hostname": self.host_name}
        for sysline in sysinfo:
            fixed_info_string = sysline.replace(
                "System information", "\nDescription: System information")
            fixed_info_string = fixed_info_string.replace(
                "Temperature", "\nTemperature")
            fixed_info_string = fixed_info_string.replace(
                "Processes", "\nProcesses")
            fixed_info_string = fixed_info_string.replace(
                "Storage", "\nStorage")
            fixed_info_string = fixed_info_string.replace("Users", "\nUsers")
            fixed_info_string = fixed_info_string.replace("IP", "\nIP")
            # some fixes for vcgencmd
            fixed_info_string = fixed_info_string.replace(
                "temp=", "Temperature:")
            fixed_info_string = fixed_info_string.replace("'C", " C")

            info_lines = fixed_info_string.splitlines()

            other_num = 0
            for line in info_lines:
                line_trimmed = line.strip()
                if line_trimmed:
                    #  print(">>> : "+str(line_trimmed))
                    (first, _sep, second) = line_trimmed.partition(":")
                    second_trimmed = second.strip()
                    first_trimmed = first.strip().lower()
                    # print(">>> "+str(first_trimmed))
                    if first_trimmed.startswith("ip"):
                        info_map["ip-address"] = second_trimmed
                    elif first_trimmed == "description":
                        info_map[first_trimmed] = second_trimmed
                    elif first_trimmed == "temperature":
                        info_map[first_trimmed] = second_trimmed
                    elif first_trimmed == "processes":
                        info_map[first_trimmed] = second_trimmed
                    elif first_trimmed.startswith("storage"):
                        info_map["storgae-usage"] = second_trimmed
                    elif first_trimmed == "system load":
                        info_map["system-load"] = second_trimmed
                    elif first_trimmed == "memory usage":
                        info_map["memory-usage"] = second_trimmed
                    elif first_trimmed == "swap usage":
                        info_map["swap-usage"] = second_trimmed
                    else:
                        other_num += 1
                        key = "other:" + str(other_num)
                        info_map[key] = line_trimmed
        # print(">>> : "+str(info_map))
        return info_map
