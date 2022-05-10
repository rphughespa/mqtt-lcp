#!/usr/bin/python3
# i2c_process.py
"""


I2cProcess - interface to devices on an I2C bus.  Devices tio be used are are specified in the config file

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

from inspect import currentframe
import time
import locale
from subprocess import call


from utils.global_constants import Global
from structs.io_data import IoData

from i2c.drivers.i2c_rfid import I2cRfid
from i2c.drivers.i2c_mux import I2cMux
from i2c.drivers.i2c_encoder import I2cEncoder
from i2c.drivers.i2c_port_expander import I2cPortExpander
from i2c.drivers.i2c_servo_controller import I2cServoController
from i2c.devices.i2c_bus import I2cBus
from processes.base_process import BaseProcess




# from roster_data import LocoData
# from roster_data import RosterData

# from i2c.i2c_servo_controller import I2cServoController


class I2cProcess(BaseProcess):
    """ Class that waits for an event to occur """

    def __init__(self, events=None, queues=None):
        super().__init__(name="i2c",
                         events=events,
                         in_queue=queues[Global.I2C],
                         app_queue=queues[Global.APPLICATION],
                         log_queue=queues[Global.LOGGER])
        self.i2c_device_driver_map = {}  # devices mapped by io_address
        self.i2c_mux_map = {}  # mux devices by i2_adddress
        self.i2c_bus = None
        self.loco_rfid_map = {}
        self.locator_topic = None
        self.log_info("Starting")
        self.device_errors = 10

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def initialize_process(self):
        """ initialize the process """
        super().initialize_process()
        # self.locator_topic = \
        #    self.mqtt_config.publish_topics.get(Global.LOCATOR, Global.UNKNOWN)
        #print(">>> io_config")
        if not isinstance(self.io_config.i2c_bus_number, int):
            message = "Configuration error, invalid i2c bus_number: " + \
                str(self.io_config.i2c_bus_number)
            if self.log_queue is not None:
                self.log_queue.put((Global.LOG_LEVEL_ERROR, message))
            else:
                print("IoConfig: Error: " + message)
        self.__log_i2c_addresses_detected()
        self.i2c_bus = I2cBus(self.io_config.i2c_bus_number, self.log_queue)
        time.sleep(2)  # wait for i2c bus to "settle"
        self.log_info("... I2C Devices ...")
        self.log_info("I2c Bus: " + str(self.io_config.i2c_bus_number))
        if self.io_config.io_device_map is not None:
            self.__build_drivers_maps()
        else:
            self.log_warning("No I2C devices configured")

    def shutdown_process(self):
        """ process shutdown is in progress """
        if self.i2c_bus is not None:
            self.i2c_bus.close()
        super().shutdown_process()

    def process_message(self, new_message=None):
        """ process messages from async message queue """
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            self.log_debug("New Message Received: " + str(new_message))
            (operation, io_message) = new_message
            # print("())() "+str(log_message))
            if operation == Global.IO_REQUEST:
                self.__send_io_device_request_message(io_message)
                msg_consummed = True
        return msg_consummed

    def process_other(self):
        """ perform other than message queue tasks"""
        super().process_other()
        # check for any input frrom i2c device
        self.__perform_async_io()
        # perform  device other periodic processing
        self.__perform_device_other()

    #
    # private functions
    #

    def __send_io_device_request_message(self, message):
        """ send request message to an i2c device """
        response_reported = Global.ERROR
        data_reported = None
        error_msg = None
        send_after_message = None
        self.log_debug("IO Device Request: [" + str(self.__get_linenumber())+"] : "
                       + str(message.mqtt_port_id) + " ... "
                       + str(message.mqtt_desired))
        device_object_key = self.io_config.io_port_map.get(
            message.mqtt_port_id, None)
        if device_object_key is None:
            error_msg = "IO Device Port not found for: [" + str(self.__get_linenumber())+"] : "\
                + str(message.mqtt_port_id)
        else:
            device_object = self.i2c_device_driver_map.get(
                device_object_key, None)
            if device_object is None:
                error_msg = "IO Device not found for: [" + str(self.__get_linenumber())+"] : "\
                    + str(device_object_key) + " [" + str(hex(device_object_key)) + "]"
            else:
                (response_reported, error_msg, data_reported, send_after_message) = \
                    device_object.request_device_action(message)
        response = None
        respond_to = None
        data_response = None
        if response_reported is not None:
            respond_to = message.mqtt_respond_to
            response = IoData()
            response.mqtt_message_root = message.mqtt_message_root
            response.mqtt_version = message.mqtt_version
            response.mqtt_session_id = message.mqtt_session_id
            response.mqtt_port_id = message.mqtt_port_id
            response.mqtt_desired = message.mqtt_desired
            response.mqtt_reported = response_reported
            if error_msg is not None:
                response.mqtt_metadata = {Global.MESSAGE: str(error_msg)}
                self.device_errors -= 1
                if self.device_errors < 1:
                    # too many errors, quit
                    self.events[Global.SHUTDOWN].set()
        if data_reported is not None:  # and mqtt-send-sensor-message:
            data_response = IoData()
            data_response.mqtt_message_root = message.mqtt_message_root
            data_response.mqtt_port_id = message.mqtt_port_id
            data_response.mqtt_reported = data_reported
        if response is not None or data_response is not None:
            self.send_to_application((Global.RESPONSE, {
                Global.RESPOND_TO: respond_to,
                Global.RESPONSE: response,
                Global.DATA: data_response
            }))
        if send_after_message is not None:
            # add a message to send after  queue
            # print(">>> send_after i2c_process: " +
            #     str(send_after_message.topic))
            self.send_after(send_after_message)

    def __perform_async_io(self):
        """ perform async I/O: read from i2c device without first sending data """
        self.__poll_input_devices()

    def __poll_input_devices(self):
        """ poll device for input """
        if self.io_config.io_port_map:
            for key, device_object_key in self.io_config.io_port_map.items():
                device_object = self.i2c_device_driver_map.get(
                    device_object_key, None)
                if device_object is None:
                    self.log_error("IO Device not found for: : [" + str(self.__get_linenumber())+"] : " \
                                   + str(key) + " .{}.. "+str(device_object_key))
                                   # + " [" + str(hex(int(device_object_key))) + "]")
                    self.device_errors -= 1
                else:
                    if isinstance(device_object, I2cRfid):
                        self.__poll_rfid_device(device_object)
                    elif isinstance(device_object, I2cEncoder):
                        self.__poll_encoder_device(device_object)
                    elif isinstance(device_object, I2cPortExpander):
                        self.__poll_port_expander_device(device_object)
                    elif isinstance(device_object, I2cServoController):
                        self.__poll_servo_controller_device(device_object)
                    else:
                        self.log_error(
                            "IO Device not reconized : [" +
                            str(self.__get_linenumber())+"] : "
                            + str(type(device_object)))

        if self.device_errors < 1:
            # too many errors, quit
            self.events[Global.SHUTDOWN].set()

    def __perform_device_other(self):
        """ allow device a chance to do periodic operations """
        if self.io_config.io_port_map:
            for key, device_key in self.io_config.io_port_map.items():
                device_object = self.i2c_device_driver_map.get(
                    device_key, None)
                if device_object is None:
                    self.log_error("IO Device not found for: : [" + str(self.__get_linenumber())+"] : "
                                   + str(key) + " .[]. "+str(device_key) )
                                   # + " [" + str(hex(device_key)) + "]")
                    self.device_errors -= 1
                else:
                    device_object.perform_other()
        if self.device_errors < 1:
            # too many errors, quit
            self.events[Global.SHUTDOWN].set()

    def __poll_rfid_device(self, device_object):
        """ poll a single rfid device """
        if device_object.io_devices.io_mux_address is not None:
            self.i2c_mux_map[device_object.io_devices.io_mux_address].\
                enable_mux_port(device_object.io_devices.io_sub_address)
        tag_io_list = device_object.read_input()
        if device_object.io_devices.io_mux_address is not None:
            self.i2c_mux_map[device_object.io_devices.io_mux_address].\
                disable_all_mux_ports()
        # return data read via app queue
        for tag_io_data in tag_io_list:
            self.log_debug("RFID Tag Read: " + str(tag_io_data.mqtt_reported))
            self.send_to_application((Global.RFID, {Global.DATA: tag_io_data}))

    def __poll_encoder_device(self, device_object):
        """ poll a single encoder device """
        if device_object.io_devices.io_mux_address is not None:
            self.i2c_mux_map[device_object.io_devices.io_mux_address].\
                enable_mux_port(device_object.io_devices.io_sub_address)
        (counter_io_data, clicked_io_data) = device_object.read_input()
        if device_object.io_devices.io_mux_address is not None:
            self.i2c_mux_map[device_object.io_devices.io_mux_address].\
                disable_all_mux_ports()
        if counter_io_data is not None:
            self.log_debug("Encoder: Counter: " +
                           str(counter_io_data.mqtt_reported))
            self.send_to_application((Global.ENCODER, {
                Global.DATA: counter_io_data
            }))
        if clicked_io_data is not None:
            self.log_debug("Encoder: Clicked: " +
                           str(clicked_io_data.mqtt_reported))
            self.send_to_application((Global.ENCODER, {
                Global.DATA: clicked_io_data
            }))

    def __poll_port_expander_device(self, device_object):
        """ poll a single port_expander device """
        changed_pins = device_object.read_input()
        if changed_pins is not None:
            for pin_io_data in changed_pins:
                self.send_to_application((Global.PORT_EXPANDER, {
                    Global.DATA: pin_io_data
                }))

    def __poll_servo_controller_device(self, device_object):
        """ poll a single servo_controller device """
        pass

    def __build_drivers_maps(self):
        """ build a map of device by port id """
        self.i2c_mux_map = {}
        self.i2c_device_driver_map = {}
        for key, dev in self.io_config.io_device_map.items():
            # print("\n\n\n>>> dev: "+str(key) + "\n"+str(dev))
            self.__add_device_driver_to_map(key, dev)
            if dev.io_mux_address is not None:
                self.__add_mux_to_map(dev.io_mux_address)
        #print("\n\n\n>>> Drivers Map:" + str(self.i2c_device_driver_map))
        #print("\n\n\n>>> Mux Map:" + str(self.i2c_mux_map))

    def __add_device_driver_to_map(self, key, device):
        dev_object = None
        device_type = device.io_device
        #print(">>> dev type: "+str(device_type))
        if device_type == Global.RFID:
            dev_object = I2cRfid(io_devices=device,
                                 i2c_bus=self.i2c_bus,
                                 log_queue=self.log_queue)
        elif device_type == Global.ENCODER:
            dev_object = I2cEncoder(io_devices=device,
                                    i2c_bus=self.i2c_bus,
                                    log_queue=self.log_queue)
        elif device_type == Global.PORT_EXPANDER:
            dev_object = I2cPortExpander(io_devices=device,
                                         i2c_bus=self.i2c_bus,
                                         log_queue=self.log_queue)
        elif device_type == Global.PORT_EXPANDER_RELAY_16:
            dev_object = I2cPortExpander(io_devices=device,
                                         i2c_bus=self.i2c_bus,
                                         log_queue=self.log_queue)
        elif device_type == Global.PORT_EXPANDER_RELAY_QUAD:
            # print(">>> port relay quad found")
            dev_object = I2cPortExpander(io_devices=device,
                                         i2c_bus=self.i2c_bus,
                                         log_queue=self.log_queue)
        elif device_type == Global.SERVO_CONTROLLER:
            dev_object = I2cServoController(io_devices=device,
                                        i2c_bus=self.i2c_bus,
                                        log_queue=self.log_queue)
        else:
            self.log_warning("Error: Unknown device type: " +
                             str(type(device_type)))
        self.i2c_device_driver_map[key] = dev_object

    def __add_mux_to_map(self, mux_address):
        """ add a mux to the mux map """
        mux_dev = self.i2c_mux_map.get(mux_address, None)
        if mux_dev is None:
            # print(">>> mux: "+str(mux_address))
            mux_dev = I2cMux(i2c_address=mux_address,
                             i2c_bus=self.i2c_bus,
                             log_queue=self.log_queue)
            self.i2c_mux_map[mux_address] = mux_dev

    def __get_linenumber(self):
        """ get current line number """
        cf = currentframe()
        return cf.f_back.f_lineno

    def __log_i2c_addresses_detected(self):
        """ log all i2c addresses detected on the i2c bus """
        if isinstance(self.io_config.i2c_bus_number, int):
            cmd_out_file = "/var/tmp/i2cdetect.txt"
            command = "i2cdetect -y " + str(self.io_config.i2c_bus_number) + \
                    " " + "> /var/tmp/i2cdetect.txt"
            i2c_address_list = []
            call(command, shell=True)
            with open(cmd_out_file, \
		            encoding=locale.getpreferredencoding(False)) as f:
                i2c_lines = f.readlines()
                for line in i2c_lines:
                    if len(line) > 4 and \
                            line[2] == ":":
                        line_parts = line[3:].split()
                        for part in line_parts:
                            if part != "--":
                                i2c_address_list += [part]

            self.log_info("I2C Addresses Detected: " + " ".join(map(str,i2c_address_list)))
