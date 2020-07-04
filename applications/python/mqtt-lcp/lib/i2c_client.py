# i2c_client.py


"""

    i2c_client.py - helper class to process i2c devices
    serializes access to i2c buss so only one device at a time uses bus

The MIT License (MIT)

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
import sys
# platforms for esp32 = esp32, for lobo esp32 = esp32_LoBo, for pi = linux
if sys.platform.startswith("esp32"):
    from queue_esp32 import Queue
    from smbus2_esp32 import SMBus
else:
    from queue_py import Queue
    from smbus2 import SMBus

import time


from io_data import IoData
from i2c_mux import I2cMux
from i2c_rfid import I2cRfid
from i2c_rotary import I2cRotary
from i2c_servo import I2cServo
from i2c_servo_hat import I2cServoHat

from global_constants import Global



class I2cClientReaderWriter():
    """ Class foor reading and writing to I2C devices"""

    def __init__(self, log_queue, devices, mqtt_devices, in_queue, out_queue, display_queue):
        # print("i2c client init")
        self.i2c_in_queue = in_queue
        self.i2c_out_queue = out_queue
        self.log_queue = log_queue
        self.display_queue = display_queue
        self.devices = devices
        self.mqtt_devices = mqtt_devices
        self.exit = False
        # print("i2c client init done")


    def start(self):
        """ initialize devices """
        # print("i2c client run")
        for device in self.devices:
            i2c_device = device['dev']
            if i2c_device is not None:
                i2c_device.init_device()
        # loop through inputs, then loop through out queue


    def shutdown(self):
        """ Shutdown this thread"""
        self.exit = True

    def process_devices(self):
        """ process the devices """
        try:
            for device in self.devices:
                self.log_queue.add_message("debug", "Read Input from: "+str(device['dev'].i2c_address))
                if device['type'] == Global.RFID:
                    device['dev'].read_input()
                if device['type'] == Global.ROTARY:
                    device['dev'].read_input()
                if device['type'] == Global.MUX:
                    mux_type = device['dev'].mux_type
                    # print("mux type: "+str(mux_type))
                    if mux_type == Global.SERVO_HAT:
                        device['dev'].read_input()
                if device['type'] == Global.DISPLAY:
                    # i2c display can slow down i2c bus.
                    if self.display_queue is not None:
                        device['dev'].write_one_log_messages(self.display_queue)
                while not self.i2c_out_queue.empty():
                    message = self.i2c_out_queue.get()
                    if message is not None:
                        dmessage = message['message']
                        mqtt_key = dmessage.mqtt_port+":"+dmessage.mqtt_type
                        if mqtt_key in self.mqtt_devices:
                            # print(">>> message/device")
                            device = self.mqtt_devices[mqtt_key]
                            device.add_to_out_queue(dmessage)
        except (KeyboardInterrupt, SystemExit):
            raise
        #except Exception as exc:
        #    self.log_queue.add_message("error", 'I2c Client error: ' + str(exc))

    def get_incomming_message_from_queue(self):
        """ Place incomming messages into a queue, get next log entry"""
        message = None
        if not self.i2c_in_queue.empty():
            message = self.i2c_in_queue.get()
        return message

    def add_outgoing_message_to_queue(self, message):
        """ Add outgoing message to Queue"""
        # self.queue.append ...
        pass
