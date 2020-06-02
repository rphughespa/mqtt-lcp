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
from i2c_io_data import I2cIoData
from i2c_device import I2cDevice
from i2c_servo import I2cServo
from sparkfun_qwiic_servo_hat import QwiicServoHat

MAX_SERVO_PORTS = 16


class I2cServoHat(I2cDevice):
    """ Class for an I2C connected servo hat device"""
    def __init__(self, log_queue, input_queue, output_queue, i2c_address,
                mqtt_port=None, mqtt_type="sensor",
                mqtt_state='thrown', meta_type='turnout', i2c_bus_number=1,
                i2c_mux=None, i2c_sub_address=None, i2c_servos=None):
        super().__init__(log_queue, i2c_address, input_queue=input_queue, output_queue=output_queue,
                         i2c_device_type="servo-hat", i2c_bus_number=i2c_bus_number,
                         i2c_mux=i2c_mux, i2c_sub_address=i2c_sub_address)
        self.mode = "i/o"
        self.i2c_servos = i2c_servos
        self.servo_alignment = None
        self.servo_out_queues = {}
        self.process_dict = {}
        self.alignment_dict = {}
        self.state_dict = {}
        self.pi_servo_hat = QwiicServoHat(address=self.i2c_address, smbus=self.i2c_bus_number)
        for port in range(MAX_SERVO_PORTS):  # 0..15
            self.servo_out_queues[port] = Queue(20)
            self.process_dict[port] = None
            self.alignment_dict[port] = None
            self.state_dict[port] = Global.UNKNOWN
        self.pi_servo_hat.restart()
        #self.pi_servo_hat_restart()
        self.pi_servo_hat_test_servos(0)
        self.pi_servo_hat_test_servos(1)
        self.pi_servo_hat_test_servos(2)
        self.pi_servo_hat_test_servos(3)
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

    def setup_new_servo_to_move(self, port):
        """ setup a new servo """
        servo = None
        # print("process: "+str(port))
        if not self.servo_out_queues[port].empty():
            servo = I2cServo(self.servo_out_queues[port].get())
            align = self.alignment_dict[port]
            if servo.i2c_io_data.desired == Global.THROW:
                servo.desired_degrees = align[Global.THROW]
            elif servo.i2c_io_data.desired == Global.CLOSE:
                servo.desired_degrees = align[Global.CLOSE]
            if self.state_dict[port] == Global.UNKNOWN:
                position = int(self.pi_servo_hat.get_servo_position(port, 90)+0.5)
                if abs(align[Global.THROW] - position) < 2:
                    self.state_dict[port] = Global.THROW
                elif abs(align[Global.CLOSE] - position) < 2:
                    self.state_dict[port] = Global.CLOSE
            servo.move_degrees = 1
            servo.current_position = servo.desired_degrees
            if self.state_dict[port] == Global.CLOSE:
                servo.current_position = align[Global.CLOSE]
            if self.state_dict[port] == Global.THROW:
                servo.current_position = align[Global.THROW]
            servo.max_moves = abs(servo.desired_degrees - servo.current_position)
            if servo.desired_degrees < servo.current_position:
                servo.move_degrees = -1
            # print("Servo Move: "+str(port)+" from "+str(servo.current_position)
            #   +" to "+str(servo.desired_degrees)+" by "+str(servo.move_degrees))
        return servo

    def read_input(self):
        """ Read input from servo device"""
        # print("read inputs")
        for port in range(MAX_SERVO_PORTS):
            if self.process_dict[port] is None:
                self.process_dict[port] = self.setup_new_servo_to_move(port)
            else:
                servo = self.process_dict[port]
                if servo.max_moves > 0:
                    servo.max_moves -= 1
                    servo.current_position += servo.move_degrees
                    # print("Move to: "+str(port)+", "+str(servo.current_position))
                    self.pi_servo_hat.move_servo_position(port, servo.current_position)
                else:  # done moves?
                    pos = int(self.pi_servo_hat.get_servo_position(port, 90)+0.5)
                    i2c_io_data = servo.i2c_io_data
                    if pos == servo.desired_degrees:
                        if i2c_io_data.desired == Global.THROW:
                            i2c_io_data.reported = Global.THROWN
                            self.state_dict[port] = Global.THROW
                        elif i2c_io_data.desired == Global.CLOSE:
                            i2c_io_data.reported = Global.CLOSED
                            self.state_dict[port] = Global.CLOSE
                    else:
                        i2c_io_data.meta_type = Global.ERROR
                        i2c_io_data.meta_data = Global.MSG_ERROR_SERVO_MOVE + str(pos)
                        i2c_io_data.reported = Global.ERROR
                    self.input_queue.put(i2c_io_data)
                    self.process_dict[port] = None

    def write_output(self, message):
        """ process servo movement message """
        i2c_io_data = message['message']
        # print("process: "+ i2c_io_data.desired)
        if ((i2c_io_data.desired != Global.CLOSE) and
                (i2c_io_data.desired != Global.THROW)):
            i2c_io_data.reported = Global.ERROR
            i2c_io_data.meta_data = Global.MSG_ERROR_BAD_STATE + i2c_io_data.desired
            i2c_io_data.meta_type = Global.ERROR
            self.input_queue.put(i2c_io_data)
        elif i2c_io_data.mqtt_port not in self.i2c_servos:
            i2c_io_data.reported = Global.ERROR
            i2c_io_data.meta_data = Global.MSG_ERROR_SERVO_NOT_KNOWN + i2c_io_data.mqtt_port
            i2c_io_data.meta_type = Global.ERROR
            self.input_queue.put(i2c_io_data)
        else: # name and state desired OK
            i2c_io_data.sub_address = self.i2c_servos[i2c_io_data.mqtt_port].sub_address
            self.log_queue.add_message("info", "move: "+str(i2c_io_data.sub_address)+", "+i2c_io_data.desired)
            self.servo_out_queues[i2c_io_data.sub_address].put(i2c_io_data)

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
            print(degree)
            bus.write_word_data(self.i2c_address, 0x08, angle)

    def pi_servo_hat_test_servos(self, channel):
        """ test servo """
        for position in range(0, 90):
            self.pi_servo_hat.move_servo_position(channel, position)
            new_pos = int(self.pi_servo_hat.get_servo_position(channel, 90)+0.5)
            print("Port: "+str(channel)+", Desired: "+str(position)+", Reported: "+str(new_pos))
        for position in range(90, 0, -1):
            self.pi_servo_hat.move_servo_position(channel, position)
            new_pos = int(self.pi_servo_hat.get_servo_position(channel, 90)+0.5)
            print("Port: "+str(channel)+", Desired: "+str(position)+", Reported: "+str(new_pos))
