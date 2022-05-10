#!/usr/bin/python3
# io_config.py
"""
IocConfig- helper class that is used when passing io device config items from config json file

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
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import os
import sys

sys.path.append('../../lib')

p = os.path.abspath('../../../')
if p not in sys.path:
    sys.path.append(p)

from utils.global_constants import Global

from structs.io_data import IoData


class IoConfig(object):
    """ Data class for IO Config data """
    def __init__(self, config=None, log_queue=None):
        self.config = config
        self.log_queue = log_queue
        self.i2c_bus_number = None
        self.io_device_map = None
        self.io_port_map = None
        self.io_mux_map = None
        self.__parse_io_configs()
        self.__build_port_map()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    #
    # private functions
    #

    def __parse_io_configs(self):
        """ parse various io items fron config data """
        devices_config = None
        if Global.CONFIG in self.config:
            if Global.IO in self.config[Global.CONFIG]:
                if Global.I2C in self.config[Global.CONFIG][Global.IO]:
                    if Global.I2C_BUS_NUMBER in self.config[Global.CONFIG][
                            Global.IO][Global.I2C]:
                        self.i2c_bus_number = self.config[Global.CONFIG][
                            Global.IO][Global.I2C][Global.I2C_BUS_NUMBER]
                if Global.IO_DEVICES in self.config[Global.CONFIG][Global.IO]:
                    devices_config = self.config[Global.CONFIG][Global.IO][
                        Global.IO_DEVICES]

        #print(">>> devices: "+str(devices_config))
        if devices_config is not None:
            devices = self.__parse_devices_config(devices_config)
            #print(">>> devices 2: "+str(devices))
            if devices:
                self.io_device_map = devices

    def __parse_devices_config(self, devices_config):
        """ parse device config details  """
        devices = None
        if isinstance(devices_config, list):
            devices = {}
            for dev_config in devices_config:
                #print(">>> io config: "+str(dev_config))
                new_dev = self.__parse_one_dev_config(dev_config)
                if new_dev is not None:
                    if new_dev.io_device_key not in devices:
                        devices[new_dev.io_device_key] = new_dev
                    else:
                        self.__log_warning("Configuration error: Duplicate device address: " + \
                                 str(new_dev.io_device_key))
        return devices

    def __parse_one_dev_config(self, dev_config):
        """ parse a device configuration """
        io_data = None
        io_address = dev_config.get(Global.IO_ADDRESS, None)
        io_sub_address = dev_config.get(Global.IO_SUB_ADDRESS, None)
        io_mux_address = dev_config.get(Global.IO_MUX_ADDRESS, None)
        io_device = dev_config.get(Global.IO_DEVICE, None)
        io_device_type = dev_config.get(Global.IO_DEVICE_TYPE, None)
        okk = self.__check_config(io_device, io_device_type, io_address,
                                  io_sub_address, dev_config)
        if okk:
            io_dev_key = str(io_address)
            if io_mux_address is not None:
                io_dev_key += ":" + str(io_mux_address)
            else:
                io_dev_key += ":"
            if io_sub_address is not None:
                io_dev_key += ":" + str(io_sub_address)
            io_data = IoData()
            io_data.io_device_key = io_dev_key
            io_data.io_address = io_address
            io_data.io_sub_address = io_sub_address
            io_data.io_device = io_device
            io_data.io_device_type = io_device_type
            io_data.io_mux_address = dev_config.get(Global.IO_MUX_ADDRESS,
                                                    None)
            io_data.mqtt_message_root = dev_config.get(
                Global.MESSAGE + "-" + Global.ROOT, None)
            io_data.mqtt_port_id = dev_config.get(Global.PORT_ID, None)
            # ">>>>>> : "+str(io_data.mqtt_port_id))
            io_data.mqtt_description = dev_config.get(Global.DESCRIPTION, None)
            send_sensor_message = \
                dev_config.get(Global.SEND + "-" +
                               Global.SENSOR + "-" + Global.MESSAGE, Global.NO)
            io_data.mqtt_send_sensor_message = bool(
                send_sensor_message in (Global.YES, Global.TRUE))
            io_data.io_metadata = dev_config.get(Global.IO_METADATA, None)
            io_sub_devices = dev_config.get(Global.IO_SUB_DEVICES, None)
            if isinstance(io_sub_devices, list):
                #print("[[" + str(type(io_sub_devices))+"]]")
                sub_devices = {}
                for sub_dev_config in io_sub_devices:
                    sub_dev_config[Global.IO_DEVICE] = io_data.io_device
                    sub_dev_config[Global.IO_ADDRESS] = io_data.io_address
                    new_sub_dev = self.__parse_one_dev_config(sub_dev_config)
                    if new_sub_dev is not None:
                        sub_devices.update(
                            {new_sub_dev.mqtt_port_id: new_sub_dev})
                io_data.io_sub_devices = sub_devices
        return io_data

    def __is_valid_io_device_type(self, dev_type):
        """ if the device type valid """
        return dev_type in (Global.BLOCK, Global.DCC_ACCESSORY, Global.ENCODER,
                            Global.LOCATOR, Global.MULTIPLE,
                            Global.PORT_EXPANDER, Global.PORT_EXPANDER_RELAY_16,
                            Global.PORT_EXPANDER_RELAY_QUAD,
                            Global.RAILCOM, Global.RFID, Global.SENSOR,
                            Global.SERVO, Global.SERVO_CONTROLLER,
                            Global.SIGNAL, Global.SWITCH)

    def __build_port_map(self):
        """ build a map of device by port id """
        self.io_port_map = {}
        if self.io_device_map:
            for key, dev in self.io_device_map.items():
                self.__add_port_to_map(dev.mqtt_port_id, key)
                if isinstance(dev.io_sub_devices, dict):
                    for _sub_key, sub_device in dev.io_sub_devices.items():
                        self.__add_port_to_map(sub_device.mqtt_port_id, key)

    def __add_port_to_map(self, port_id, key):
        if port_id is not None:
            if port_id in self.io_port_map:
                self.__log_warning("Configuration error: duplicate ite with same port: ["+\
                            str(port_id)+"]")
            else:
                self.io_port_map[port_id] = key
                self.__log_debug("I2C Device: " + str(key) +\
                            " : " + str(port_id))

    def __check_config(self, io_device, io_device_type, io_address,
                       io_sub_address, dev_config):
        okk = True
        if io_address is None and io_sub_address is None:
            self.__log_warning(
                "Configuration error, io_address, io-sub-address missing: " +
                str(dev_config))
            okk = False
        if io_device is None:
            self.__log_warning("Configuration error, io-device missing: " +
                               str(dev_config))
            okk = False
        elif not self.__is_valid_io_device_type(io_device):
            self.__log_warning("Configuration error, io-device invalid: " +
                               str(dev_config))
            okk = False
        if io_device_type is None:
            self.__log_warning(
                "Configuration error, io-device-type missing: " +
                str(dev_config))
            okk = False
        elif not self.__is_valid_io_device_type(io_device_type):
            self.__log_warning(
                "Configuration error, io-device-type invalid: " +
                str(dev_config))
            okk = False
        return okk

    def __log_warning(self, message):
        """ log a warning message """
        if self.log_queue is not None:
            self.log_queue.put((Global.LOG_LEVEL_WARNING, message))
        else:
            print(">>> warning: " + message)

    #def __log_info(self, message):
    #    """ log a info message """
    #    if self.log_queue is not None:
    #        self.log_queue.put((Global.LOG_LEVEL_INFO, message))
    #    else:
    #        print(">>> info: " + message)

    def __log_debug(self, message):
        """ log a info message """
        if self.log_queue is not None:
            self.log_queue.put((Global.LOG_LEVEL_DEBUG, message))
        else:
            print(">>> debug: " + message)
