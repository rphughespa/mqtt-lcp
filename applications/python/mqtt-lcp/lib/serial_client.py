# serial_client.py


"""

    serial_client.py - helper class to process client serial connections

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
import serial
import serial.tools.list_ports
from queue_py import Queue


BUFFER_LENGTH = 4096



class SerialClientReader(threading.Thread):
    """ Read serial data  """

    def __init__(self, log_queue, thread_name,
                port=None, vendor_id=None, product_id=None,
                baudrate=115200, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_TWO, bytesize=8):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.serial_in_queue = Queue(100)
        self.log_queue = log_queue
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.exit = False
        self.serial = None
        self.port = port
        if self.port is None:
            self.port = SerialClientReader.find_usb_port(vendor_id, product_id, self.log_queue)
        if self.port is None:
            raise Exception("ERROR, USB Device not found: ["+str(vendor_id)+"], ["+str(product_id)+"]")

    def receive_message(self, _client_port):
        """ Get serial message"""
        try:
            message_text = self.serial.readline()
            return message_text
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as exc:
            # If we are here, client closed connection violently, f
            # or example by pressing ctrl+c on his script
            # or just lost his connection
            # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR)
            # what sends information about closing the socket (shutdown read/write)
            # and that's also a cause when we receive an empty message
            self.log_queue.add_message(("error", "Exception in receive_message: " + str(exc)))
            return False

    def run(self):
        """ Run thread"""
        self.serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize,
            timeout=1
        )
        if self.serial.isOpen():
            self.log_queue.add_message("info", "Serial connection established.")
        else:
            self.log_queue.add_message("info", "Serial connection NOT OPEN.")
        while not self.exit:
            time.sleep(0.1)
            try:
                # Now we want to loop over received messages (there might be more than one) and print them
                if self.serial.in_waiting > 0:
                    message = self.receive_message(self.serial)
                    if len(message) > 0:
                        self.log_queue.add_message("debug", 'Message Received from serial [' + str(message) + ']')
                        message_text = message.decode("utf8").rstrip()
                        if len(message_text) > 0:
                            new_message = {'text': message_text}
                            self.log_queue.add_message("debug", 'Text Received from serial [' + message_text + ']')
                            self.log_queue.add_message("debug", ' ... ['+message_text.encode('utf-8').hex()+']')
                            self.serial_in_queue.put(new_message)
            except (KeyboardInterrupt, SystemExit):
                raise
            except IOError as exc:
                self.log_queue.add_message("error", 'IOError error: {}' + str(exc))
                continue

            except Exception as exc:
                self.log_queue.add_message("error", 'Reading error: ' + str(exc))
                continue

    def shutdown(self):
        """ Shutdown thread"""
        self.serial.close()
        self.exit = True
        #self.join()

    def get_serial(self):
        """ Get serial object"""
        return self.serial

    def get_incomming_message_from_queue(self):
        """ Get queues input data"""
        message = None
        if not self.serial_in_queue.empty():
            message = self.serial_in_queue.get()
        return message

    def clear_incomming_queue(self):
        """ empty input queue"""
        while not self.serial_in_queue.empty():
            self.serial_in_queue.get()

# class level functions
    @classmethod
    def find_usb_port(cls, vendor_id, product_id, log_queue=None):
        """ find a serial port given a vendor and product id"""
        if log_queue is not None:
            log_queue.add_message("debug", "Finding USB, Looking for: "+str(vendor_id)+", "+str(product_id))
        usb_port = None
        devs = serial.tools.list_ports.comports()
        for dev in devs:
            if log_queue is not None:
                log_queue.add_message("debug", "Device: "+ dev.device)
                log_queue.add_message("debug", "  Name: "+ dev.name)
                log_queue.add_message("debug", "  Description: "+ dev.description)
            if dev.vid is not None:
                if log_queue is not None:
                    log_queue.add_message("debug", "  Vendor ID: "+ str(dev.vid) + ", "+hex(dev.vid))
                    log_queue.add_message("debug", "  Product ID: "+ str(dev.pid) + ", "+hex(dev.pid))
                #if dev.vid == vend_id_bin and dev.pid == prod_id_bin:
                if dev.vid == vendor_id and dev.pid == product_id:
                    if log_queue is not None:
                        log_queue.add_message("debug", "  Found IT: "+dev.device)
                    usb_port = dev.device
        return usb_port

class SerialClientWriter(threading.Thread):
    """ Write data to serial port"""

    def __init__(self, log_queue, thread_name):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.serial_out_queue = Queue(40)
        self.serial = None
        self.log_queue = log_queue
        self.exit = False

    def run(self):
        """ run the thread"""
        while not self.exit:
            time.sleep(0.1)
            while not self.serial_out_queue.empty():
                message = self.serial_out_queue.get()
                message_text = message['text']
                self.log_queue.add_message("debug", 'Sending to Serial: [' + message_text + ']')
                try:
                    rcode = self.serial.write(message_text.encode())
                    self.log_queue.add_message("debug", " .. serial bytes written : " + str(rcode))
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as exc:
                    self.log_queue.add_message("error", 'Sending error '+str(exc))

    def shutdown(self):
        """ shutdown the thread"""
        self.serial.close()
        self.exit = True
        #self.join()

    def set_serial(self, new_serial):
        """ set serial port to use"""
        self.serial = new_serial

    def add_outgoing_message_to_queue(self, message):
        """ add a message to outgoing queue"""
        self.serial_out_queue.put(message)
