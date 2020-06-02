# node_base_i2c.py - base class for mqtt nodes
"""

    node_base_i2c - Base class for nodes that use i2c.  Derived from node_base_mqtt.

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
import sys
if sys.platform.startswith("esp32_LoBo"):
    from smbus2_go_lobo import SMBus
    from queue_esp32 import Queue
elif sys.platform.startswith("esp32"):
    from smbus2_esp32 import SMBus
    from queue_esp32 import Queue
else:
    from smbus2 import SMBus
    from queue_py import Queue

import time

from node_base_mqtt import NodeBaseMqtt
from i2c_client_thread import I2cClientThread
from i2c_io_data import I2cIoData
from i2c_mux import I2cMux
from i2c_rfid import I2cRfid
from i2c_rotary import I2cRotary
from i2c_servo import I2cServo
from i2c_servo_hat import I2cServoHat
from global_constants import Global


class NodeBaseI2c(NodeBaseMqtt):
    """
        Base class for node programs usig I2c IO
        Manages IO via threads
    """

    def __init__(self):
        super().__init__()
        self.i2c_client = None
        self.i2c_devices = []
        self.i2c_in_queue = Queue(100)
        self.i2c_out_queue = Queue(100)
        self.i2c_display_imported = False


    def start_i2c(self):
        """Start I2C IO"""
        self.log_queue.add_message("info", 'start i2c client thread')
        #if sys.platform.startswith('esp32'):
         #   with SMBus(1) as i2cbus:
          #      print("I2C Scan: "+str(i2cbus.scan()))
        if Global.CONFIG in self.config:
            if Global.IO in self.config[Global.CONFIG]:
                if Global.I2C in self.config[Global.CONFIG][Global.IO]:
                    self.parse_config_data(self.config[Global.CONFIG][Global.IO][Global.I2C])
                    self.i2c_client = I2cClientThread(self.log_queue, self.i2c_devices, self.i2c_in_queue, self.i2c_out_queue,
                        self.display_queue, "I2cClient", self.config[Global.CONFIG][Global.IO][Global.I2C])
                    self.i2c_client.start()
                    time.sleep(1)

    def received_from_i2c(self, i2c_io_data):
        """ call back to process received subsctibed messages. override in derived class"""
        pass

    def get_incomming_message_from_queue(self):
        """ retrieve a receieved message from the queue """
        message = None
        if not self.i2c_in_queue.empty():
            message = self.i2c_in_queue.get()
        return message

    def process_input(self):
        """ cprocess input from all source input queues"""
        # process all input of a given type in order of importance: keyboard, serial, mqtt
        self.write_log_messages()
        if self.i2c_client is not None:
            self.i2c_client.check_msg()
            i2c_input = self.get_incomming_i2c_message_from_queue()
            if i2c_input is not None:
                self.received_from_i2c(i2c_input)
        super().process_input()

    def send_to_i2c(self, message):
        """ send message to an I2C device"""
        if self.i2c_client is not None:
            self.i2c_out_queue.put(message)

    def get_incomming_i2c_message_from_queue(self):
        """ retrieve a receieved message from the queue """
        message = None
        if not self.i2c_in_queue.empty():
            message = self.i2c_in_queue.get()
        return message

    def initialize_threads(self, alt_mqtt_client_name=None):
        """ initialize all IO threads"""
        # load config file
        # do not enable keyboard for apps meant to be run in background
        super().initialize_threads(alt_mqtt_client_name)
        if Global.CONFIG in self.config:
            if Global.IO in self.config[Global.CONFIG]:
                io_config = self.config[Global.CONFIG][Global.IO]
                if Global.I2C in io_config:
                    self.start_i2c()

    def loop(self):
        """ loop through IO.  override in dericed class"""
        while not self.shutdown_app:
            try:
                time.sleep(0.01)
                self.write_log_messages()
                self.process_input()
            except KeyboardInterrupt:
                self.shutdown_app = True

    def shutdown_threads(self):
        """ shutdown all IO threads"""

        if self.i2c_client is not None:
            # print("shutdown serial")
            self.i2c_client.shutdown()
        super().shutdown_threads()

    def parse_config_data(self, config_data):
        """ Parse out I2C items from config json file"""
        self.log_queue.add_message("debug", "parse i2c config")
        for i2c_node in config_data:
            self.parse_device_config(i2c_node, i2c_bus=1)

    def parse_device_config(self, i2c_node, i2c_bus=None, i2c_mux_device=None):
        """ parse configuration """
        i2c_type = None
        i2c_device = None
        address = None
        if Global.BUS in i2c_node:
            i2c_bus = i2c_node[Global.BUS]
        if Global.ADDRESS in i2c_node:
            address = i2c_node[Global.ADDRESS]
        if isinstance(address, str):
            # assume hex format "0x77"
            address = int(address, 16)
        # self.log_queue.add_message("info", "I2C Device config: "+str(address))
        if Global.DEVICE_TYPE in i2c_node:
            # a block of i2c device, either mux or gpio or unitary (single device per address)
            i2c_type = i2c_node[Global.DEVICE_TYPE]
            if i2c_type == "mux":
                mux_device = I2cMux(self.log_queue, address)
                if not self.is_device_connected(i2c_bus, address):
                    self.i2c_device_not_connected_error(i2c_bus, address, i2c_type)
                ports = i2c_node[Global.PORTS]
                for port in ports:
                    self.parse_device_config(port, i2c_bus=i2c_bus, i2c_mux_device=mux_device)
            elif i2c_type == "servo-hat":
                i2c_mux_port = None
                servos = {}
                items = i2c_node[Global.PORTS]
                for item in items:
                    device_type = None
                    i2c_io_data = I2cIoData()
                    sub_address = -1
                    center_degrees = 45  # defaults for 90 degree servo
                    throw_degrees = 90
                    close_degrees = 0
                    mqtt_port = None
                    mqtt_type = None
                    device_type = None
                    if Global.MQTT+"-"+Global.PORT in item:
                        mqtt_port = item[Global.MQTT+"-"+Global.PORT]
                    if Global.MQTT+"-"+Global.TYPE in item:
                        mqtt_type = item[Global.MQTT+"-"+Global.TYPE]
                    if Global.SUB_ADDRESS in item:
                        sub_address = int(item[Global.SUB_ADDRESS])
                    if Global.DEVICE_TYPE in item:
                        device_type = item[Global.DEVICE_TYPE]
                    i2c_io_data.mqtt_type = mqtt_type
                    i2c_io_data.mqtt_port = mqtt_port
                    i2c_io_data.sub_address = sub_address
                    i2c_io_data.device_type = device_type
                    servos[mqtt_port] = i2c_io_data
                    # print("Servo: "+str(i2c_io_data.mqtt_name))
                i2c_device = I2cServoHat(self.log_queue, self.i2c_in_queue, self.i2c_out_queue,
                            address,
                            #port=port,
                            # type=mtype,
                            i2c_bus_number=i2c_bus,
                            i2c_servos=servos)
            else:
                i2c_sub_address = None
                i2c_mux_port = None
                if i2c_mux_device is not None:
                    if Global.SUB_ADDRESS in i2c_node:
                        i2c_sub_address = i2c_node[Global.SUB_ADDRESS]
                if i2c_type == Global.RFID:
                    mqtt_port = None
                    mqtt_type = None
                    device_type = None
                    if Global.MQTT+"-"+Global.PORT in i2c_node:
                        mqtt_port = i2c_node[Global.MQTT+"-"+Global.PORT]
                    if Global.MQTT+"-"+Global.TYPE in i2c_node:
                        mqtt_type = i2c_node[Global.MQTT+"-"+Global.TYPE]
                    if Global.DEVICE_TYPE in i2c_node:
                        device_type = i2c_node[Global.DEVICE_TYPE]
                    self.log_queue.add_message("info", "I2C Device config: "+str(address)+"..."+str(i2c_type)+
                            "..."+str (mqtt_port)+"..."+str(mqtt_type))
                    i2c_device = I2cRfid(self.log_queue, self.i2c_in_queue, address,
                            mqtt_port=mqtt_port,
                            mqtt_type=mqtt_type,
                            itype=device_type,
                            i2c_bus_number=i2c_bus,
                            i2c_mux=i2c_mux_device,
                            i2c_sub_address=i2c_sub_address)
                elif i2c_type == Global.ROTARY:
                    mqtt_port = None
                    mqtt_type = None
                    device_type = None
                    if Global.MQTT+"-"+Global.PORT in i2c_node:
                        mqtt_port = i2c_node[Global.MQTT+"-"+Global.PORT]
                    if Global.MQTT+"-"+Global.TYPE in i2c_node:
                        mqtt_type = i2c_node[Global.MQTT+"-"+Global.TYPE]
                    if Global.DEVICE_TYPE in i2c_node:
                        device_type = i2c_node[Global.DEVICE_TYPE]
                    self.log_queue.add_message("info", "I2C Device config: "+str(address)+"..."+str(i2c_type)+
                            "..."+str (mqtt_port)+"..."+str(mqtt_type))
                    i2c_device = I2cRotary(self.log_queue, self.i2c_in_queue, address,
                            mqtt_port=mqtt_port,
                            mqtt_type=mqtt_type,
                            itype=device_type,
                            i2c_bus_number=i2c_bus,
                            i2c_mux=i2c_mux_device,
                            i2c_sub_address=i2c_sub_address)
                elif i2c_type == Global.DISPLAY:
                    display_size = None
                    display_type = None
                    if Global.DISPLAY+"-"+Global.SIZE in i2c_node:
                        display_size = i2c_node[Global.DISPLAY+"-"+Global.SIZE]
                    if Global.DISPLAY+"-"+Global.TYPE in i2c_node:
                        display_type = i2c_node[Global.DISPLAY+"-"+Global.TYPE]
                        # not everyone needs disply, import only if needed
                    if not self.i2c_display_imported:
                        from i2c_display import I2cDisplay
                        self.i2c_display_imported = True
                    self.log_queue.add_message("info", "I2C Device config: "+str(address)+"..."+i2c_type)
                    i2c_device = I2cDisplay(self.log_queue, address,
                            display_size=display_size,
                            display_type=display_type,
                            i2c_bus_number=i2c_bus,
                            i2c_mux=i2c_mux_device,
                            i2c_sub_address=i2c_sub_address)
                elif i2c_type == Global.GPIO:
                    pass
        if i2c_type is not None and i2c_device is not None:
            if not self.is_device_connected(i2c_device.i2c_bus_number, i2c_device.i2c_address):
                self.i2c_device_not_connected_error(i2c_device.i2c_bus_number, i2c_device.i2c_address,
                        i2c_device.i2c_device_type)
            self.i2c_devices.append({'type': i2c_type, 'dev': i2c_device})

    def i2c_device_not_connected_error(self, bus, address, dtype):
        """ raise Exception(Global.MSG_I2C_NOT_CONNECTED+" "+Global.DEVICE_TYPE+": "+str(type)+", "+
            Global.BUS+": "+str(bus)+", "+Global.ADDRESS+": "+str(address)) """
        self.log_queue.add_message("error", Global.MSG_I2C_NOT_CONNECTED+" "+Global.DEVICE_TYPE+
              ": "+str(dtype)+", "+
              Global.BUS+": "+str(bus)+", "+Global.ADDRESS+": "+str(address))

#   modified routine from sparkfun qwiic_i2c
    def is_device_connected(self, smbus, address):
        device_connected = False
        with SMBus(smbus) as bus:
            try:
                # Try to write a byte to the device, command 0x0
                # If it throws an I/O error - the device isn't connected
                bus.write_byte(address, 0x0)
                device_connected = True
            except Exception as ee:
                print("Error connecting to Device: %X, %s" % (address, ee))
                pass
        return device_connected
