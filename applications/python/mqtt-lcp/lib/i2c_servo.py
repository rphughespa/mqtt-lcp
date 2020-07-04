# i2c_servo.py

"""

i2c_servo_hat.py - helper class to process i2c connected servo devices

    Supports the SparkFun pi hat servo board, Some code in this module has been copied from
    the SparkFun python modules:

        PiServoHat.py, Qwiic_PCA9685_Py

    Please check theses modules for SparkFun code license.

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
else:
    from queue_py import Queue
from global_constants import Global

from io_data import IoData
from i2c_device import I2cDevice

class I2cServo(I2cDevice):
    """ Class for an I2C connected servo device"""

    def __init__(self, log_queue, i2c_address, mqtt_port=None, mqtt_type=None, input_queue=None,
                    i2c_device_type=Global.SERVO, i2c_bus_number=1, mqtt_send_sensor_msg=False,
                    i2c_mux=None, i2c_sub_address=None):
        """ initialize """
        super().__init__(log_queue, i2c_address, input_queue=input_queue,
                         i2c_device_type=i2c_device_type, i2c_bus_number=i2c_bus_number,
                         mqtt_port=mqtt_port, mqtt_type=mqtt_type, mqtt_send_sensor_msg=mqtt_send_sensor_msg,
                         i2c_mux=i2c_mux, i2c_sub_address=i2c_sub_address)
        self.mode = "input"
        self.last_value = 0
        self.init_device()
        self.center_degrees = 45
        self.throw_degrees = 89
        self.close_degrees = 0


    def read_input(self):
        """ Read input from servo device"""
        pass

    def write_output(self, message):
        """ process servo movement message """
        pass

    def add_to_out_queue(self, io_data):
        if self.i2c_mux is not None:
            self.i2c_mux.write_output(self, io_data)
