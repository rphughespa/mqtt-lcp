#!/usr/bin/python3
# serial_process.py
"""

        serial_process - process class for serial devices

    This process reveives data to send to the serial through it's "in_queue" message queue. These
    messesages are tagged as "SERIAL_DEVICE_SEND".  The process will also periodically poll the
    serial device for input. Data received is send to the "app queue" and tagged as "SERIAL_DEVICE_DATA"

    The process can also do synchronius type functions of sending data to the serial device and
    then waiting for a response.  This "send and respond" process if invoked via message
    type "SERIAL_DEVICE_SEND_AND_RESPOND" . THe response is returned tagged as "SERIAL_DEVICE_RESPONSE".

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
import sys

sys.path.append('../../lib')

import time
import serial
import serial.tools.list_ports

from utils.global_constants import Global
# from utils.bit_utils import BitUtils

from processes.base_process import BaseProcess

MAX_BUFFER = 120


class SerialProcess(BaseProcess):
    """ interface to serial device """
    def __init__(self, events=None, queues=None):
        super().__init__(name="serial",
                        events=events,
                        in_queue=queues[Global.DEVICE],
                        app_queue=queues[Global.APPLICATION],
                        log_queue=queues[Global.LOGGER])

        self.queues = queues
        self.driver_queue = queues[Global.DRIVER]
        self.delay = 0
        self.buffer = ""
        self.serial_mode = Global.TEXT
        self.serial_port = None
        self.serial_usb_vendor_id = None
        self.serial_usb_product_id = None
        self.serial_baudrate = None
        self.serial_port_id = None
        self.serial_configured = False
        self.error_count = 0
        self.data_queue = ""

        # print(">>> serial process starting !!!!!!!!")

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def initialize_process(self):
        """ iitialize this process """
        super().initialize_process()
        self.serial_port_id = None
        usb_vendor_key = Global.USB + "-" + Global.VENDOR + "-" + Global.ID
        usb_product_key = Global.USB + "-" + Global.PRODUCT + "-" + Global.ID
        if Global.CONFIG in self.config:
            if Global.IO in self.config[Global.CONFIG]:
                if Global.SERIAL in self.config[Global.CONFIG][Global.IO]:
                    self.serial_configured = True
                    if Global.SERIAL_MODE in self.config[Global.CONFIG][
                            Global.IO][Global.SERIAL]:
                        self.serial_mode = \
                            self.config[Global.CONFIG][Global.IO][Global.SERIAL][Global.SERIAL_MODE]
                    if usb_vendor_key in self.config[Global.CONFIG][Global.IO][
                            Global.SERIAL]:
                        self.serial_usb_vendor_id = \
                            self.config[Global.CONFIG][Global.IO][Global.SERIAL][usb_vendor_key]
                    if usb_product_key in self.config[Global.CONFIG][
                            Global.IO][Global.SERIAL]:
                        self.serial_usb_product_id = \
                            self.config[Global.CONFIG][Global.IO][Global.SERIAL][usb_product_key]
                    if Global.BAUDRATE in self.config[Global.CONFIG][
                            Global.IO][Global.SERIAL]:
                        self.serial_baudrate = \
                            self.config[Global.CONFIG][Global.IO][Global.SERIAL][Global.BAUDRATE]
                    if Global.PORT in self.config[Global.CONFIG][Global.IO][
                            Global.SERIAL]:
                        self.serial_port_id = \
                            self.config[Global.CONFIG][Global.IO][Global.SERIAL][Global.PORT]
        if self.serial_usb_vendor_id is not None and self.serial_usb_product_id is not None:
            self.serial_port_id = self.__find_usb_port(
                self.serial_usb_vendor_id, self.serial_usb_product_id)
        if self.serial_port_id is None:
            self.serial_configured = False
        if not self.serial_configured:
            self.log_warning(
                "Serial port not configured. Serial port not being used.")
        else:
            if self.serial_port_id is None:
                self.log_critical(\
                    "!!!! Configuration file error: serial port cannot be opened")
                time.sleep(2)  # allow time for log to be written
                self.events[Global.RESTART].set()
            else:
                if self.serial_baudrate is None:
                    self.serial_baudrate = "115200"
                self.log_info("Starting serial port: " +
                              str(self.serial_port_id) + " ..." +
                              str(self.serial_mode))
                try:
                    self.serial_port = serial.Serial(
                        port=self.serial_port_id,
                        baudrate=self.serial_baudrate,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_TWO,
                        bytesize=8,
                        timeout=1)
                except Exception as exc:
                    self.log_critical("exception opening serial port: " +
                                      str(exc))
                if self.serial_port.isOpen():
                    self.log_info(" ... Serial connection established.")
                else:
                    self.log_critical(
                        " ... Serial connection NOT OPEN, exiting")
                    time.sleep(2)  # allow time for log to be written
                    self.events[Global.RESTART].set()

    def shutdown_process(self):
        """ process shutdown is in progress """
        if self.serial_port is not None and self.serial_port.isOpen():
            self.serial_port.close()
        super().shutdown_process()

    def process_message(self, new_message=None):
        """ process messages from async message queue """
        print(">>> new serial process message 1: " + str(new_message))
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            # print(">>> new serial process message: " + str(new_message))
            (msg_type, msg_map) = new_message
            msg_text = msg_map
            if isinstance(msg_map, dict):
                msg_text = msg_map[Global.TEXT]
            response_queue = None
            encoded_msg_text = self.encode_message(msg_text)
            # self.log_warning("Send Serial: " + str(encoded_msg_text))
            if msg_type == Global.DEVICE_SEND:
                #print(">>> serial m: [" + str(new_message) + "] ... [" +
                #      str(msg_text) + "]")
                if self.serial_port is not None and self.serial_port.isOpen():
                    self.send_serial_message(encoded_msg_text)
                    msg_consummed = True
            elif msg_type == Global.DEVICE_SEND_AND_RESPOND:
                if self.serial_port is not None and self.serial_port.isOpen():
                    # print(">>> send/respond")
                    self.send_serial_message(encoded_msg_text)
                    message = self.__perform_async_io(0.1)
                    self.publish_response(message, msg_map[Global.RESPONSE_QUEUE])
                    msg_consummed = True
                else:
                    self.publish_response({Global.TEXT: Global.ERROR},
                                          response_queue)
        return msg_consummed

    def process_other(self):
        """ perform other than message queue tasks"""
        super().process_other()
        # perform  device other periodic processing
        message = self.__perform_async_io(0.01)
        if message is not None:
            # print(">>> serial other: " + str(message))
            if isinstance(message, list):
                for message_line in message:
                    self.publish_input(message_line)
            else:
                self.publish_input(message)

    def publish_input(self, serial_data):
        """ publish serial input """
        message = (Global.DEVICE_INPUT, serial_data)
        if self.driver_queue is not None:
            self.driver_queue.put(message)
        else:
            self.send_to_application(message)

    def publish_response(self, serial_data, response_queue):
        """ publish serial input """
        #print(">>> response to: " + str(response_queue) + " ... " + str(serial_data))
        message = (Global.DEVICE_RESPONSE, serial_data)
        resp_queue = self.queues.get(response_queue, None)
        if resp_queue is not None:
            resp_queue.put(message)

    def send_serial_message(self, message):
        """ send a message to serial device """
        if message is not None:
            self.log_info("Serial Send: [" + str(message) + "]")
            bytes_to_write = message
            if self.serial_mode == Global.TEXT:
                #print(">>> message: " + str(message))
                line = message + "\r\n"
                bytes_to_write = line.encode()
            self.log_debug("Send to serial: " + str(bytes_to_write))
            bytes_written = self.serial_port.write(bytes_to_write)
            if bytes_written != len(bytes_to_write):
                self.log_error("Serial write error on message: " + str(message))

    def encode_message(self, msg_body):
        """ translate data read from serial port """
        return msg_body

    def decode_message(self, msg_body):
        """ translate data read from serial port """
        return msg_body

    #
    # private functions
    #

    def __perform_async_io(self, timeout):
        """ perform async I/O: read from serial device without first sending data """
        # check for unsolicited input from serial device
        time_waited = 0
        rett = None
        while time_waited < timeout:
            bytes_avail = self.serial_port.in_waiting
            if bytes_avail > 0:
                if self.serial_mode == Global.TEXT:
                    rett = self.__read_serial_io_by_line()
                else:
                    rett = self.__read_serial_io_by_char()
                break
            time.sleep(0.02)
            time_waited += 0.02
        return rett

    def __read_serial_io_by_line(self):
        """ read a message from serial device """
        # print(">>> read serial...")
        rett = None
        try:
            # Get serial input if there is any
            bytes_avail = self.serial_port.in_waiting
            if bytes_avail > 0:
                bytes_read = self.serial_port.readline()
                self.error_count = 0
                message = bytes_read.decode(" ISO-8859-1")
                message_fixed = message.replace("\r\n",
                            "\n").replace("\r", "\n").replace("\n", "")
                rett = []
                decoded = self.decode_message(message_fixed)
                if isinstance(decoded, list):
                    for lmessage in decoded:
                        rett.append(lmessage)
                else:
                    rett.append(decoded)
        except IOError as exc:
            self.log_error('IOError error: {}' + str(exc))
            self.error_count += 1
            if self.error_count > 20:
                self.log_critical(
                    "Too mnay errors serial errors received, shutting down")
                self.events[Global.RESTART].set()
        if rett is not None:
            self.log_info("Serial Read: " + str(rett))
        return rett

    def __read_serial_io_by_char(self):
        """ read a message from serial device """
        # print(">>> read serial...")
        rett = None
        try:
            # Get serial input if there is any
            bytes_avail = self.serial_port.in_waiting
            if bytes_avail > 0:
                bytes_read = self.serial_port.read(bytes_avail)
                self.error_count = 0
                # message = bytes_read.decode(" ISO-8859-1")
                # convert bytes to lits of integers
                rett = list(bytes_read)
                # print(">>> Bytes Read: " + str(rett))
        except IOError as exc:
            self.log_error('IOError error: {}' + str(exc))
            self.error_count += 1
            if self.error_count > 20:
                self.log_critical(
                    "Too mnay errors serial errors received, shutting down")
                self.events[Global.RESTART].set()
        if rett is not None:
            self.log_debug("Serial Read:" + str(rett))
        return rett

#    def __log_text_string(self, message_text=None):
#        self.log_debug('Message Received from serial [' + str(message_text) +
#                       ']')
#        # print(">>> log debug: " + str(self.is_logging_debug))
#        if self.is_logging_debug:
#            hex_list = BitUtils.string_to_hex_list(str(message_text))
#            self.log_debug('... [' + str(hex_list) + ']')

    def __find_usb_port(self, vendor_id=None, product_id=None):
        """ find a serial port given a vendor and product id"""

        self.log_info("Finding USB, Looking for: " + str(vendor_id) + ", " +
                       str(product_id))
        usb_port = None
        devs = serial.tools.list_ports.comports()
        for dev in devs:
            self.log_info("Device: " + dev.device + ",  Name: " + dev.name + ",  Description: " + dev.description)
            if dev.vid is not None:
                self.log_info(" Vendor ID: " + str(dev.vid) + ", " +
                            hex(dev.vid) +
                            " Product ID: " + str(dev.pid) + ", " +
                            hex(dev.pid))
                # if dev.vid == vend_id_bin and dev.pid == prod_id_bin:
                if dev.vid == vendor_id and dev.pid == product_id:
                    self.log_info(" Found IT: " + dev.device)
                    usb_port = dev.device
        return usb_port
