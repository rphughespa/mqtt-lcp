# node_base_serial.py - base class for mqtt nodes
"""


 node_base_serial - base class for nodes that use usb serial i/o.  Derived from node_base_mqtt.

the MIT License (MIT)

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

import time

from global_constants import Global

from node_base_mqtt import NodeBaseMqtt
from keyboard_client_thread import KeyboardClientThread
from serial_client_thread import SerialClientThread


class NodeBaseSerial(NodeBaseMqtt):
    """
        Base class for node programs that use Serial IO, MQTT, and keyboard
        Manages IO via threads
    """

    def __init__(self):
        super().__init__()
        self.serial_client = None
        self.serial_usb_vendor_id = None
        self.serial_usb_product_id = None
        self.serial_port_id = None
        self.serial_baudrate = None
        self.keyboard_client = None

    def start_keyboard(self):
        """ Start keyboard IO"""
        self.keyboard_client = KeyboardClientThread(self.log_queue, 'keyboard_reader',
                prompt=self.node_name+">")
        self.keyboard_client.start()

    def start_serial(self):
        """Start Serial IO"""
        self.log_queue.add_message("info", 'start serial client thread')
        usb_vendor_key = Global.USB+"-"+Global.VENDOR+"-"+Global.ID
        usb_product_key = Global.USB+"-"+Global.PRODUCT+"-"+Global.ID
        if Global.IO in self.config[Global.CONFIG]:
            if Global.SERIAL in self.config[Global.CONFIG][Global.IO]:
                if usb_vendor_key in self.config[Global.CONFIG][Global.IO][Global.SERIAL]:
                    self.serial_usb_vendor_id = self.config[Global.CONFIG][Global.IO][Global.SERIAL][usb_vendor_key]
                if usb_product_key in self.config[Global.CONFIG][Global.IO][Global.SERIAL]:
                    self.serial_usb_product_id = self.config[Global.CONFIG][Global.IO][Global.SERIAL][usb_product_key]
                if Global.BAUDRATE in self.config[Global.CONFIG][Global.IO][Global.SERIAL]:
                    self.serial_baudrate = self.config[Global.CONFIG][Global.IO][Global.SERIAL][Global.BAUDRATE]
                if Global.PORT in self.config[Global.CONFIG][Global.IO][Global.SERIAL]:
                    self.serial_port_id = self.config[Global.CONFIG][Global.IO][Global.SERIAL][Global.PORT]
                self.serial_client = SerialClientThread(self.log_queue, "SerialClient",
                        port=self.serial_port_id,
                        baudrate=self.serial_baudrate,
                        vendor_id=self.serial_usb_vendor_id,
                        product_id=self.serial_usb_product_id)
                self.serial_client.start()
                time.sleep(1)



    def received_from_keyboard(self, key_input):
        """ call back to process received mqtt input. override in derived class"""
        pass

    def received_from_serial(self, serial_input):
        """ call back to process received serial input. override in derived class"""
        pass


    def process_input(self):
        """ process input from all source input queues"""
        # process all input of a given type in order of importance: keyboard, serial, mqtt
        self.write_log_messages()
        if self.keyboard_client is not None:
            key_input = self.keyboard_client.get_incomming_message_from_queue()
            if key_input is not None:
                key_in = key_input['text']
                self.received_from_keyboard(key_in)
        if self.serial_client is not None:
            serial_input = self.serial_client.get_incomming_message_from_queue()
            if serial_input is not None:
                serial_in = serial_input['text']
                self.received_from_serial(serial_in)
        super().process_input()

    def send_to_serial_and_wait(self, message):
        """ send message to seial and wait for response"""
        response = None
        new_message = {'text' : message+'\n'}
        if self.serial_client is not None:
            response = self.serial_client.send_immediate(new_message)
        return response

    def send_to_serial(self, message):
        """ send message to serial, do not wait for response"""
        new_message = {'text' : message+'\n'}
        if self.serial_client is not None:
            self.serial_client.add_outgoing_message_to_queue(new_message)

    def initialize_threads(self):
        """ initialize all IO threads"""
        # load config file
        super().initialize_threads()
        # do not enable keyboard for apps meant to be run in background
        if Global.IO in self.config[Global.CONFIG]:
            io_config = self.config[Global.CONFIG][Global.IO]
            if Global.KEYBOARD in io_config:
                opt = io_config[Global.KEYBOARD]
                if opt == "true":
                    self.start_keyboard()
            if Global.SERIAL in io_config:
                self.start_serial()

    def loop(self):
        """ loop through IO.  override in dericed class"""
        while not self.shutdown_app:
            try:
                time.sleep(0.01)
                self.write_log_messages()
                self.process_input()
            except KeyboardInterrupt:
                self.shutdown_app = True

    def shutdown_theads(self):
        """ shutdown all IO threads"""
        if self.serial_client is not None:
            # print("shutdown serial")
            self.serial_client.shutdown()
        super().shutdown_threads()
