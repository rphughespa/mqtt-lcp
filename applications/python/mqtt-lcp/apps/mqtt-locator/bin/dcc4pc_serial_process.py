#!/usr/bin/python3
# dcc4pc_serial_process.py
"""

        dcc4pc_seriall_process - process class for dcc4pc serial message processings

        Monitors dcc4pc data bytes received through a serial port and interperts them.
        Specically look for railcom and block occpancy messages,  When received, data is forwarded
        to the application.

The MIT License (MIT)

Copyright 2023 richard p hughes

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
from processes.serial_process import SerialProcess
from utils.global_constants import Global


sys.path.append('../lib')


MAX_BUFFER = 120

DCC4PC_END_OF_MESSAGE = b'\xFF'
DCC4PC_ADDRESS_MESSAGE = b'\xFC'
DCC4PC_CV_MESSAGE = b'\xFE'
DCC4PC_SYSTEM_MESSAGE = b'\xFD'
DCC4PC_DIAGNOSTIC_MESSAGE = b'\xD1'
DCC4PC_SIGNOUT_MESSAGE = b'\xFA'

DCC4PC_INITIALIZE_ALL_COMMAND = b'\x20'
DCC4PC_QUERY_COMMAND = b'\x40'
DCC4PC_SEND_INFO_COMMAND = b'\x60'
DCC4PC_PROGRAM_DETECTOR_COMMAND = b'\x80'
DCC4PC_REQUEST_DIAG_COMMAND = b'\xA0'
DCC4PC_SWITCH_SCOPE_MODE_COMMAND = b'\xC0'
DCC4PC_TURN_OFF_TRAFFIC_COMMAND = b'\x21'

class BlockData(object):
    """ data about a block """

    def __init__(self):
        """ initialize """
        self.block_id = 0
        self.loco_id = 0
        self.loco_facing_normal = True
        self.occupied = False

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"


class Dcc4pcSerialProcess(SerialProcess):
    """ Process Some dcc4pc Messages from Serial Port"""

    def __init__(self, events=None, queues=None):
        self.queues = queues
        # we don't have a separate driver process
        # redirect driver messages to application process
        self.queues[Global.DRIVER] = queues[Global.APPLICATION]
        super().__init__(events=events, queues=queues)

        self.block_map = {}

        self.bytes_queue = []
        self.bytes_queue_length_desired = 0

        self.message_type = {}
        self.message_type[DCC4PC_ADDRESS_MESSAGE] = 5
        self.message_type[DCC4PC_CV_MESSAGE] = 4
        self.message_type[DCC4PC_SYSTEM_MESSAGE] = 6
        self.message_type[DCC4PC_DIAGNOSTIC_MESSAGE] = 12
        self.message_type[DCC4PC_SIGNOUT_MESSAGE] = 4


    def publish_input(self, serial_data):
        """ override method in parent class """
        # get input, one integer at a time
        print(">>> Dcc4Pc Serial Input: " + str(serial_data) + " ... " + str(hex(serial_data)))
        self.bytes_queue.append(serial_data)
        message_processing_done = False
        while not message_processing_done:
            if serial_data == DCC4PC_END_OF_MESSAGE:
                message_processing_done = True
            else:
                first_byte = self.bytes_queue[0]
                desired_message_length = self.message_type.get(
                    first_byte, None)
                if desired_message_length is None:
                    self.log_warning(
                        "Unrecognized message: " + str(first_byte))
                    # remove bad first bytes
                    self.bytes_queue = self.bytes_queue[1:]
                elif desired_message_length > len(self.bytes_queue):
                    # have not received enough bytes for this message
                    message_processing_done = True
                else:
                    message_bytes = self.bytes_queue[0:desired_message_length]
                    self.bytes_queue = self.bytes_queue[desired_message_length:]
                    self.__process_message_bytes(message_bytes)


    #
    # private functions
    #

    def __publish_dcc4pc_input(self, body):
        """ publish the interperted data"""
        self.app_queue.put(body)

    def __process_message_bytes(self, message_bytes):
        message_type = message_bytes[0]
        if message_type == DCC4PC_ADDRESS_MESSAGE:
            block_message = self.__decode_address_message(message_bytes)
            if _block_has_changed(block_message):
                self.log_info("Message received: Block, "+str(block_message))
                if _block_loco_changed(block_message):
                    _publish_locator_message(block_message)
                if _block_occupancy_changed(block_message):
                    publish_occuopied_message(block_message)
                _update_block_data(block_message)

                self.log_info("Message received: Block, "+str(block_message))
                input_message = (Global.DEVICE_INPUT_BLOCK_DATA, {
                    'data': message_map
                })
                self.__publish_dcc4pc_input(input_message)
            message_map = self.__decode_railcom_message(message_bytes)
            self.log_info("Message received: Railcom, " + str(message_map))
            input_message = (Global.DEVICE_INPUT_RAILCOM_DATA, {
                'data': message_map
            })

            self.__publish_dcc4pc_input(input_message)
        else:
            self.log_debug("Warning: Unknown Message Received: " +
                           str(hex(message_type)))

    def __decode_address_message(self, message_list):
        # decode dcc4pc address message
        block_id = int(message_list[1],2)
        facing_flag = message_list[2] & 0x80
        addr1 = message_list[2] & 0x7f
        loco_id = int(addr1,2) * 256 + int(message_list[3],2)
        block_data = BlockData()
        block_data.block_id = block_id
        block_data.loco_id = loco_id
        if facing_flag  != 0:
            block_loco_facing_normal = True
        if loco_id != 0:
            block_data.occupied = True
        return block_data

    def __decode_railcom_message(self, message_list):
        # byte 1 is a legth byte in the long message
        status_byte = message_list[2]
        block_byte = message_list[3]
        loco_high = message_list[4]
        loco_low = message_list[5]
        direction_byte = message_list[6]
        (block, status) = self.__translate_block_status_changed(
            block_byte, status_byte)
        loco_addr = self.__translate_loco_address(loco_high, loco_low)
        direction = self.__translate_loco_direction(direction_byte)

        return {
            "type": Global.RAILCOM,
            "state": status,
            "loco": loco_addr,
            "block": block,
            "facing": direction
        }

    def __translate_block_status_changed(self, block_byte, status_byte):
        # get right mode 4 bits, shit left seven bits
        high_block_byte = (status_byte & 0x0F) << 7
        low_block_byte = block_byte
        block_id = high_block_byte + low_block_byte + 1
        status_code = (status_byte & 0x60) >> 5
        status = Global.UNKNOWN
        if status_code == 1:
            status = Global.ENTERED
        elif status_code == 0:
            status = Global.EXITED
        return (block_id, status)

    def __translate_loco_address(self, loco_high_byte, loco_low_byte):
        #  get right most 7 bits, slide to left 7 bits
        high_addr = (loco_high_byte & 0x7F) << 7

        # get right mode 7 bits
        low_addr = loco_low_byte & 0x7F

        address = high_addr + low_addr
        return str(address)

    def __translate_loco_direction(self, direction_byte):
        # check bit 7
        direction_flag = direction_byte & 0x40
        direction = Global.REVERSED
        if direction_flag == 0:
            direction_flag = Global.NORMAL
        return direction

    def __find_start_of_next_command(self):
        """ find start of next dcc4pc command, value > 127 """
        start = None
        if self.bytes_queue:
            for i, val in enumerate(self.bytes_queue):
                if val > 127:  # bit 7 set
                    start = i
                    break
        return start

    # def __process_message_bytes(self, message_bytes):
    #    decoded_message  = self.decode_dcc4pc_message(message_bytes)
    #    if decoded_message is not None:
    #        self.__publish_dcc4pc_input(decoded_message)
