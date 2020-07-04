# serial_client_thread.py

"""

    SerialClient Thread : class to manage serial io

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


import threading
import time

from serial_client import SerialClientReader
from serial_client import SerialClientWriter


BUFFER_LENGTH = 4096

class SerialClientThread(threading.Thread):
    """ lass to manage serial IO via threads"""

    def __init__(self, log_queue, thread_name, port=None, baudrate=115200, vendor_id=None, product_id=None):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.port = port
        self.baudrate = baudrate
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.client_serial = None
        self.serial_reader = None
        self.serial_writer = None
        self.log_queue = log_queue
        self.exit = False


    def run(self):
        """ Run the threads"""
        self.serial_reader = SerialClientReader(self.log_queue, "SerialReader",
                port=self.port, baudrate=self.baudrate, vendor_id=self.vendor_id, product_id=self.product_id)
        self.serial_reader.start()

        time.sleep(0.5)

        self.serial_writer = SerialClientWriter(self.log_queue, "SerialWriter")
        self.client_serial = self.serial_reader.get_serial()
        self.serial_writer.set_serial(self.client_serial)
        self.serial_writer.start()

        self.log_queue.add_message("info", 'Serial Client Started...')
        while not self.exit:
            time.sleep(0.5)

    def shutdown(self):
        """ Shutdown the threads"""
        self.log_queue.add_message("info", "Exiting Serial Client")
        self.exit = True
        self.serial_reader.shutdown()
        self.serial_writer.shutdown()
        # self.console_thread.join()
        #self.serial_reader.join()
        #self.serial_writer.join()
        self.join()

    def set_serial(self, serial):
        """ set the serial device"""
        self.client_serial = serial

    def add_outgoing_message_to_queue(self, message):
        """ add message to outgoing queue"""
        if self.serial_writer is not None:
            self.serial_writer.add_outgoing_message_to_queue(message)

    def get_incomming_message_from_queue(self):
        """ get a message from incomming queue"""
        return self.serial_reader.get_incomming_message_from_queue()

    def clear_incomming_queue(self):
        """ empty the incomming queue"""
        if self.serial_reader is not None:
            self.serial_reader.clear_incomming_queue()

    def send_immediate(self, out_message, timeout=5):
        """ send message to serial device and wait for response"""
        self.log_queue.add_message("debug", "Serial Send Immediate Send: "+str(out_message))
        self.clear_incomming_queue()
        self.add_outgoing_message_to_queue(out_message)
        in_message = None
        timeout_seconds = time.mktime(time.localtime()) + timeout
        while in_message is None and timeout_seconds > time.mktime(time.localtime()):
            time.sleep(0.2)
            self.log_queue.add_message("debug", "Serial Send Immediate, Waiting...")
            in_message = self.get_incomming_message_from_queue()
        self.log_queue.add_message("debug", "Serial Send Immediate Received: "+str(in_message))
        return in_message
