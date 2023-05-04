
# io_config.py
"""
IocConfig- helper class that is used when passing io device config items from config json file

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

from global_constants import Global

from io_data import IoData
from compass_points import CompassPoints

class IoConfig:
    """ Data class for IO Config data """

    def __init__(self, config=None):
        self.config = config
        self.i2c_bus_number = None
        self.io_device_map = None
        self.io_port_map = None
        self.io_mux_map = None
        # self.__parse_io_configs()
        # self.__build_port_map()

    def report_inventory(self, node_name, sub_topics, pub_topics):
        """ generate metadata for response to an inventory request message """
        # print(">>> inv requested")

        metadata = {}
        device_list = []
        if self.io_device_map is not None:
            device_list = self.__flatten_device_map(self.io_device_map)
        # print(">>> inventory report")
        sensors = self.__build_sensors_metadata(
            device_list, node_name, sub_topics, pub_topics, stypes=[Global.SENSOR, Global.ENCODER])
        if sensors:
            metadata.update({Global.SENSOR: sensors})

        switches = self.__build_switches_metadata(
            device_list, node_name, sub_topics, pub_topics)
        if switches:
            metadata.update({Global.SWITCH: switches})

        locators = self.__build_locators_metadata(
            device_list, node_name, sub_topics, pub_topics)
        if locators:
            metadata.update({Global.LOCATOR: locators})

        blocks = self.__build_blocks_metadata(
            device_list, node_name, sub_topics, pub_topics)
        if blocks:
            metadata.update({Global.BLOCK: blocks})

        signals = self.__build_signals_metadata(
            device_list, node_name, sub_topics, pub_topics)
        if signals:
            metadata.update({Global.SIGNAL: signals})
        return metadata

    #
    # private functions
    #

    def parse_io_configs(self):
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

        # print(">>> devices: "+str(devices_config))
        if devices_config is not None:
            devices = self.__parse_devices_config(devices_config)
            # print(">>> devices 2: "+str(devices))
            if devices:
                self.io_device_map = devices

    def __parse_devices_config(self, devices_config):
        """ parse device config details  """
        devices = None
        if isinstance(devices_config, list):
            devices = {}
            for dev_config in devices_config:
                # print(">>> io config: "+str(dev_config))
                new_dev = self.__parse_one_dev_config(dev_config)
                if new_dev is not None:
                    if new_dev.io_device_key not in devices:
                        devices[new_dev.io_device_key] = new_dev
                    else:
                        print("Configuration error: Duplicate device address: " +
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
        io_metadata = dev_config.get(Global.IO_METADATA, None)
        io_port_id = dev_config.get(Global.PORT_ID, None)
        if io_port_id is not None:
            # make sure port id is a string
            io_port_id = str(io_port_id)
        io_block_id = dev_config.get(Global.BLOCK_ID, None)
        if io_block_id is not None:
            io_block_id = str(io_block_id)
        io_direction = dev_config.get(Global.DIRECTION, None)
        okk = self.__check_config(io_device, io_device_type, io_address, io_port_id,
                                  io_sub_address, io_direction, dev_config)
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
            io_data.io_mux_address = \
                dev_config.get(Global.IO_MUX_ADDRESS, None)
            io_data.mqtt_message_root = dev_config.get(
                Global.MESSAGE + "-" + Global.ROOT, None)
            io_data.mqtt_port_id = dev_config.get(Global.PORT_ID, None)
            if io_data.mqtt_port_id is not None:
                # make sure port id is a string
                io_data.mqtt_port_id = str(io_data.mqtt_port_id)
            io_data.mqtt_block_id = \
                dev_config.get(Global.BLOCK_ID, None)
            io_data.mqtt_direction = \
                dev_config.get(Global.DIRECTION, None)
            # ">>>>>> : "+str(io_data.mqtt_port_id))
            io_data.mqtt_description = dev_config.get(Global.DESCRIPTION, None)
            io_data.mqtt_block_id = io_block_id
            io_data.mqtt_direction = io_direction
            io_data.mqtt_metadata = io_metadata
            send_sensor_message = \
                dev_config.get(Global.SEND + "-" +
                               Global.SENSOR + "-" + Global.MESSAGE, Global.NO)
            io_data.mqtt_send_sensor_message = bool(
                send_sensor_message in (Global.YES, Global.TRUE))
            io_data.io_metadata = dev_config.get(Global.IO_METADATA, None)
            io_sub_devices = dev_config.get(Global.IO_SUB_DEVICES, None)
            if isinstance(io_sub_devices, list):
                # print("[[" + str(type(io_sub_devices))+"]]")
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
                            Global.LOCATOR, Global.MULTIPLE, Global.GPIO,
                            Global.PORT_EXPANDER, Global.PORT_EXPANDER_RELAY,
                            Global.RAILCOM, Global.RFID, Global.SENSOR,
                            Global.SERVO, Global.SERVO_CONTROLLER,
                            Global.SIGNAL, Global.SWITCH,
                            Global.DISPLAY, Global.LOGGER,
                            Global.TURNTABLE)

    def build_port_map(self):
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
                print("Configuration error: duplicate item with same port: [" +
                      str(port_id)+"]")
            else:
                self.io_port_map[port_id] = key
                print("I2C Device: " + str(key) +
                      " : " + str(port_id))

    def __check_config(self, io_device, io_device_type, io_address, io_port_id,
                       io_sub_address, io_direction, dev_config):
        okk = True
        if io_address is None and io_sub_address is None:
            print(
                "Configuration error, io_address, io-sub-address missing: " +
                str(dev_config))
            okk = False
        if io_device is None:
            print("Configuration error, io-device missing: " +
                               str(dev_config))
            okk = False
        elif not self.__is_valid_io_device_type(io_device):
            print("Configuration error, io-device invalid: " +
                               str(dev_config))
            okk = False
        if io_device_type is None:
            print(
                "Configuration error, io-device-type missing: " +
                str(dev_config))
            okk = False
        elif not self.__is_valid_io_device_type(io_device_type):
            print(
                "Configuration error, io-device-type invalid: " +
                str(dev_config))
            okk = False
        if io_port_id is not None:
            if " " in str(io_port_id):
                print(
                    "Configuration error, port_id contain spaces: " +
                    str(dev_config))
                okk = False
        if io_direction is not None:
            if not CompassPoints.is_valid(io_direction):
                print(
                    "Configuration error, direction is not valid: " +
                    str(dev_config))
                okk = False
        return okk

    def __flatten_device_map(self, device_map):
        """ create a flat list of devices and sub devices """
        dev_list = []
        for (_key, device) in device_map.items():
            dev_list.append(device)
            if isinstance(device.io_sub_devices, dict):
                for (_key, sub_device) in device.io_sub_devices.items():
                    dev_list.append(sub_device)
        return dev_list

    def __build_blocks_metadata(self, device_list, node_name, sub_topics, pub_topics):
        """ format blocks data, sensors with meta type 'block' """
        return self.__build_sensors_metadata(
            device_list, node_name, sub_topics, pub_topics, stypes=[Global.BLOCK])

    def __build_locators_metadata(self, device_list, node_name, sub_topics, pub_topics):
        """ format locator data, sensors with meta type 'railcom' """
        return self.__build_sensors_metadata(
            device_list, node_name, sub_topics, pub_topics, stypes=[Global.RFID, Global.RAILCOM, Global.LOCATOR])

    def __build_sensors_metadata(self, device_list, node_name, _sub_topics, pub_topics, stypes=None):
        """ format sensor data """
        if stypes is None:
            stypes = []
        sensor_topic = pub_topics.get(Global.SENSOR, None)
        inventory_meta = []
        for dev in device_list:
            # print("\n\n>>> dev: "+str(dev))
            # print(">>> ... stypes: "+str(stypes))
            if dev.io_device_type == Global.SENSOR:
                if dev.io_device in stypes:
                    sensor = {}
                    sensor.update({Global.NODE_ID: node_name})
                    if dev.mqtt_port_id is not None:
                        sensor.update({Global.PORT_ID: dev.mqtt_port_id})
                    if dev.mqtt_block_id is not None:
                        sensor.update({Global.BLOCK_ID: dev.mqtt_block_id})
                    if dev.mqtt_direction is not None:
                        sensor.update({Global.DIRECTION: dev.mqtt_direction})
                    if dev.mqtt_reported is not None:
                        sensor.update({Global.REPORTED: dev.mqtt_reported})
                    if dev.mqtt_timestamp is not None:
                        sensor.update({Global.TIMESTAMP: dev.mqtt_timestamp})
                    if dev.mqtt_description is not None:
                        sensor.update(
                            {Global.DESCRIPTION: dev.mqtt_description})
                    if dev.mqtt_data_topic is not None:
                        sensor.update({
                            Global.DATA + "-" + Global.TOPIC:
                            dev.mqtt_data_topic
                        })
                    elif sensor_topic is not None:
                        sensor.update({
                            Global.DATA + "-" + Global.TOPIC:
                            sensor_topic + "/" + dev.mqtt_port_id
                        })
                    # print(">>> sensor: "+str(sensor))
                    inventory_meta.append(sensor)
        return inventory_meta

    def __build_switches_metadata(self, device_list, node_name, sub_topics, pub_topics):
        """ format inventory switch data for inventory reporting """
        inventory_meta = []
        sensor_topic = pub_topics.get(Global.SENSOR, None)
        switch_topic = sub_topics.get(Global.SWITCH, None)
        for dev in device_list:
            # print("\n\n\n>>> dev: "+str(key))
            if dev.io_device_type == Global.SWITCH:
                # print(">>> ... dev: "+str(dev))
                switch = {}
                switch.update({Global.NODE_ID: node_name})
                if dev.io_blocks is not None:
                    switch.update({Global.BLOCKS: dev.io_blocks})
                if dev.mqtt_port_id is not None:
                    switch.update({Global.PORT_ID: dev.mqtt_port_id})
                if dev.mqtt_block_id is not None:
                    switch.update({Global.BLOCK_ID: dev.mqtt_block_id})
                if dev.mqtt_direction is not None:
                    switch.update({Global.DIRECTION: dev.mqtt_direction})
                if dev.mqtt_description is not None:
                    switch.update({Global.DESCRIPTION: dev.mqtt_description})
                if dev.mqtt_data_topic is not None:
                    switch.update({
                        Global.DATA + "_" + Global.TOPIC:
                        dev.mqtt_data_topic
                    })
                elif sensor_topic is not None:
                    switch.update({
                        Global.DATA + "-" + Global.TOPIC:
                        sensor_topic + "/" + dev.mqtt_port_id
                    })
                if dev.mqtt_roster_topic is not None:
                    switch.update({
                        Global.ROSTER + "_" + Global.TOPIC:
                        dev.mqtt_roster_topic
                    })
                elif switch_topic is not None:
                    sw_topic = switch_topic.replace("/#", "")
                    switch.update({
                        Global.COMMAND + "-" + Global.TOPIC:
                        sw_topic + "/" + dev.mqtt_port_id + "/req"
                    })

                inventory_meta.append(switch)
        return inventory_meta

    def __build_signals_metadata(self, device_list, node_name, sub_topics, pub_topics):
        """ format inventory signal data for inventory reporting """
        # print(">>> sub topics: "+str(self.mqtt_config.subscribe_topics))
        sensor_topic = pub_topics.get(Global.SENSOR, None)
        roster_topic = pub_topics.get(Global.ROSTER, None)
        signal_topic = sub_topics.get(Global.SIGNAL, None)
        inventory_meta = []
        for dev in device_list:
            if dev.io_device_type == Global.SIGNAL:
                signal = {}
                signal.update({Global.NODE_ID: node_name})
                if dev.io_blocks is not None:
                    signal.update({Global.BLOCKS: dev.io_blocks})
                if dev.mqtt_port_id is not None:
                    signal.update({Global.PORT_ID: dev.mqtt_port_id})
                if dev.mqtt_block_id is not None:
                    signal.update({Global.BLOCK_ID: dev.mqtt_block_id})
                if dev.mqtt_direction is not None:
                    signal.update({Global.DIRECTION: dev.mqtt_direction})
                if dev.mqtt_description is not None:
                    signal.update({Global.DESCRIPTION: dev.mqtt_description})
                if dev.mqtt_data_topic is not None:
                    signal.update({
                        Global.DATA + "_" + Global.TOPIC:
                        dev.mqtt_data_topic
                    })
                elif sensor_topic is not None:
                    signal.update({
                        Global.DATA + "-" + Global.TOPIC:
                        sensor_topic + "/" + dev.mqtt_port_id
                    })
                if roster_topic is not None:
                    signal.update({
                        Global.ROSTER + "_" + Global.TOPIC:
                        roster_topic
                    })
                elif signal_topic is not None:
                    sig_topic = signal_topic.replace("/#", "")
                    signal.update({
                        Global.COMMAND + "-" + Global.TOPIC:
                        sig_topic + "/" + dev.mqtt_port_id + "/req"
                    })
                inventory_meta.append(signal)
        return inventory_meta
