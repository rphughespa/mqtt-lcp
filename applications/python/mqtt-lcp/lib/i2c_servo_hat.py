# ic2_servo_hat

"""

i2c_servo_hat.py - helper class to process i2c connected servo devices

    Manages a servro hat with multiple serve ports.

    The code is a bit complicated.

        a.  Multiple requests to move any giving servo are queued (FIFO) and executed serially.

        b.  Since the servo hat port supports multiple servos they are moved in parallel
            because we want slow motion in each movement. Waiting for one servo movement to complete befor
            starting the movement of another would be be too slow a process.

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
if sys.platform.startswith("esp32_LoBo"):
    from queue_esp32 import Queue
    import ujson
    from smbus2_go_lobo  import SMBus
elif sys.platform.startswith("esp32"):
    from queue_esp32 import Queue
    import ujson
    from smbus2_esp32 import SMBus
else:
    from queue_py import Queue
    import json
    from smbus2 import SMBus

import time

from global_constants import Global
from global_synonyms import Synonyms
from io_data import IoData
from i2c_device import I2cDevice
from i2c_servo import I2cServo
from i2c_servo_data import I2cServoData
from sparkfun_qwiic_servo_hat import QwiicServoHat

MAX_SERVO_PORTS = 16


class I2cServoHat(I2cDevice):
    """ Class for an I2C connected servo hat device"""
    def __init__(self, log_queue, i2c_address, mux_type=None, input_queue=None,
                mqtt_port=None, mqtt_type="switch+sensor", output_queue=None,
                mqtt_state='thrown', meta_type='turnout', i2c_bus_number=1,
                i2c_mux=None, i2c_sub_address=None):
        super().__init__(log_queue, i2c_address, input_queue=input_queue,
                         i2c_device_type=Global.SERVO+"-"+Global.BUS, i2c_bus_number=i2c_bus_number,
                         i2c_mux=i2c_mux, i2c_sub_address=i2c_sub_address, mux_type=mux_type)
        self.mode = "i/o"
        self.i2c_servos = {}
        self.servo_alignment = None
        self.alignment_dict = {}
        self.servo_out_dict = {}
        self.servo_out_dict_index = 0
        self.process_dict = {}
        self.state_dict = {}
        self.pi_servo_hat = QwiicServoHat(address=self.i2c_address, smbus=self.i2c_bus_number)
        self.pi_servo_hat.restart()
        #self.pi_servo_hat_restart()
        self.pi_servo_hat_reset_servos(0)
        self.pi_servo_hat_reset_servos(1)
        self.pi_servo_hat_reset_servos(2)
        self.pi_servo_hat_reset_servos(3)
        self.configure()

    def configure(self):
        """ configure """
        with open('servos.json') as json_file:
            if sys.platform.startswith("esp32"):
                self.servo_alignment = ujson.load(json_file)
            else:
                self.servo_alignment = json.load(json_file)
        if self.servo_alignment is None:
            print("! Configure ERROR !")
        assert (self.servo_alignment is not None), "Error: servo.json was not found!"
        if Global.CONFIG in self.servo_alignment:
            if Global.SERVO in self.servo_alignment[Global.CONFIG]:
                if Global.PORTS in self.servo_alignment[Global.CONFIG][Global.SERVO]:
                    ports = self.servo_alignment[Global.CONFIG][Global.SERVO][Global.PORTS]
                    for port in ports:
                        if Global.PORT in port:
                            self.alignment_dict[port[Global.PORT]] = port

    def setup_new_servo_to_move(self, servo_io):
        """ setup a new servo """
        # remove a switch request and place in process queue
        # only one request in process queue per switch
        servo = servo_io["servo"]
        port = servo.i2c_sub_address
        io_data = servo_io["io_data"]
        servo_data = I2cServoData()
        # print("Degrees: "+str(servo.close_degrees)+".."+str(servo.throw_degrees))
        servo_data.desired_degrees = servo.close_degrees
        if Synonyms.is_synonym_throw(io_data.mqtt_desired):
            servo_data.desired_degrees = servo.throw_degrees
        servo_data.current_degrees = int(self.pi_servo_hat.get_servo_position(port, 90)+0.5)
        # print("current: "+str(servo_data.current_degrees))
        servo_data.move_degrees = 1
        servo_data.max_moves = abs(servo_data.desired_degrees - servo_data.current_degrees)
        # set direction of move
        if servo_data.desired_degrees < servo_data.current_degrees:
            servo_data.move_degrees = -1
        self.log_queue.add_message("info", "Servo Move: "+str(port)+" from "+str(servo_data.current_degrees)
          +" to "+str(servo_data.desired_degrees)+" by "+str(servo_data.move_degrees))
        return {"data": servo_data, "servo": servo, "io_data": io_data}

    def read_input(self):
        """ Read input from servo device"""
        # print("read servohat inputs")
        for key in list(self.servo_out_dict):
            out_servo_io = self.servo_out_dict[key]
            port = out_servo_io["servo"].i2c_sub_address
            if port not in self.process_dict:
                self.process_dict[port] = self.setup_new_servo_to_move(out_servo_io)
                del self.servo_out_dict[key]
        for key in list(self.process_dict):
            servo_io = self.process_dict[key]
            servo_data = servo_io["data"]
            port = servo_io["servo"].i2c_sub_address
            if servo_data.max_moves > 0:
                servo_data.max_moves -= 1
                servo_data.current_degrees += servo_data.move_degrees
                # print("Move to: "+str(port)+", "+str(servo_data.current_degrees))
                self.pi_servo_hat.move_servo_position(port, servo_data.current_degrees)
            else:  # done moves?
                io_data = servo_io["io_data"]
                pos = int(self.pi_servo_hat.get_servo_position(port, 90)+0.5)
                if pos == servo_data.desired_degrees:
                    io_data.mqtt_reported = Synonyms.desired_to_reported(io_data.mqtt_desired)
                else:
                    io_data.mqtt_metadata = {Global.MESSAGE:Global.ERROR+": "+Global.MSG_ERROR_SERVO_MOVE + str(pos)}
                    io_data.mqtt_reported = Global.ERROR
                self.input_queue.put(io_data)
                del self.process_dict[key]

    def write_output(self, servo, io_data):
        """ process servo movement message """
        # servo-out_queues - switch requests waiting to be processed
        # there may be more than one request queued per switch
        # print("process: "+ io_data.desired)
        # print("process: "+ io_data.mqtt_port)
        if io_data.mqtt_port not in self.i2c_servos:
            self.i2c_servos[io_data.mqtt_port] = servo
        if ((io_data.mqtt_desired != Global.CLOSE) and
                (io_data.mqtt_desired != Global.THROW)):
            io_data.mqtt_reported = Global.ERROR
            io_data.mqtt_metadata = {Global.MESSAGE:Global.ERROR+": "+Global.MSG_ERROR_BAD_STATE + " "+io_data.mqtt_desired}
            self.input_queue.put(io_data)
        else: # name and state desired OK
            io_data.io_sub_address = self.i2c_servos[io_data.mqtt_port].i2c_sub_address
            self.log_queue.add_message("info", "move: "+str(io_data.io_sub_address)+", "+io_data.mqtt_desired)
            self.servo_out_dict_index += 1
            if self.servo_out_dict_index > 1000:
                self.servo_out_dict_index = 0
            out_servo_io = {"index": self.servo_out_dict_index, "servo": servo, "io_data":io_data}
            self.servo_out_dict[out_servo_io["index"]] = out_servo_io

###  functions that interact with pi servo hat

    def pi_servo_hat_restart(self):
        """ restart servo hat """
        with SMBus(self.i2c_bus_number) as bus:
            bus.write_byte_data(self.i2c_address, 0, 0x20) # enables word writes
            time.sleep(.25)
            # enable Prescale change as noted in the datasheet
            bus.write_byte_data(self.i2c_address, 0, 0x10)
            time.sleep(.25) # delay for register
             #changes the Prescale register value for 50 Hz, using the equation in the datasheet.
            bus.write_byte_data(self.i2c_address, 0xfe, 0x88)
            bus.write_byte_data(self.i2c_address, 0, 0x20) # enables word writes
            time.sleep(.25)

    def pi_servo_hat_move_servo(self, channel, degree):
        """move servo """
        with SMBus(self.i2c_bus_number) as bus:
            # for 90 degree arc...
            #   start at 250 degrees, = 0 deg
            #   end at 440 degrees = 90 deg
            #   increment by 2.1 = 1 deg
            bus.write_word_data(self.i2c_address, 0x06, channel) # chl 0 start time = 0us
            angle = int((degree*2.1)+250)
            # print(degree)
            bus.write_word_data(self.i2c_address, 0x08, angle)

    def pi_servo_hat_reset_servos(self, channel):
        """ test servo """
        #for position in range(40, 50):
        #    self.pi_servo_hat.move_servo_position(channel, position)
        #    new_pos = int(self.pi_servo_hat.get_servo_position(channel, 90)+0.5)
        #    print("Port: "+str(channel)+", Desired: "+str(position)+", Reported: "+str(new_pos))
        #    time.sleep(0.05)
        #for position in range(50, 40, -1):
        #    self.pi_servo_hat.move_servo_position(channel, position)
        #    new_pos = int(self.pi_servo_hat.get_servo_position(channel, 90)+0.5)
        #    print("Port: "+str(channel)+", Desired: "+str(position)+", Reported: "+str(new_pos))
        #    time.sleep(0.05)
        self.pi_servo_hat.move_servo_position(channel, 45)  # mid way point of server range
