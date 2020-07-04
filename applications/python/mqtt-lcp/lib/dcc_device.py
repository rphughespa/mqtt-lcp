# dcc_device.py

"""

    DccDevice - base class for DCC decoder devices


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

from queue_py import Queue

class DccDevice():
    """ Base class for DCC device classes"""

    def __init__(self, log_queue, dcc_address,
                 mqtt_port=None, mqtt_type=None, mqtt_send_sensor_msg=False,
                 dcc_sub_address=None,
                 dcc_device_type=None):
        self.log_queue = log_queue
        self.dcc_address = dcc_address
        self.dcc_sub_address = dcc_sub_address
        self.mode = None
        self.mqtt_port = mqtt_port
        self.mqtt_type = mqtt_type
        self.mqtt_send_sensor_msg = mqtt_send_sensor_msg  # send sensor message along with response for switch
        self.dcc_device_type = dcc_device_type
        self.log_queue.add_message("info", "I2C Device: "+self.dcc_device_type+". "+str(self.dcc_address))

    def init_device(self):
        """ Initialize the device"""
        pass

    def read_input(self):
        """ read input from device"""
        pass

    def add_to_out_queue(self, io_data):
        """ override in derived class"""
        pass
