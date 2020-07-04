# i2c_device.py

"""

    I2cDevice - base class for I2C devices


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
if sys.platform.startswith('esp32'):
    from queue_esp32 import Queue
else:
    from queue_py import Queue

class I2cDevice():
    """ Base class for I2C device classes"""

    def __init__(self, log_queue, i2c_address, input_queue=None, output_queue=None,
                 mqtt_port=None, mqtt_type=None, mux_type=None, mqtt_send_sensor_msg=False,
                 i2c_mux=None, i2c_sub_address=None,
                 i2c_bus_number=None, i2c_device_type=None):
        self.log_queue = log_queue
        self.input_queue = input_queue
        self.output_queue = output_queue
        if isinstance(i2c_address, str):
            # presumes string is in hex formar, 0x5A etc
            self.i2c_address = int(i2c_address, 16)
        else:
            self.i2c_address = i2c_address
        self.mode = None
        self.mqtt_port = mqtt_port
        self.mqtt_type = mqtt_type
        self.mqtt_send_sensor_msg = mqtt_send_sensor_msg  # send sensor message along with response for a switch
        self.i2c_bus_number = i2c_bus_number
        self.i2c_device_type = i2c_device_type
        self.i2c_mux = i2c_mux
        self.mux_type = mux_type
        self.input_queue = input_queue
        self.output_queue = Queue(50)
        self.i2c_sub_address = i2c_sub_address
        self.log_queue.add_message("info", "I2C Device: "+self.i2c_device_type+". "+str(self.i2c_address))

    def init_device(self):
        """ Initialize the device"""
        pass

    def read_input(self):
        """ read input from device"""
        pass

    def add_to_out_queue(self, io_data):
        """ override in derived class"""
        pass
