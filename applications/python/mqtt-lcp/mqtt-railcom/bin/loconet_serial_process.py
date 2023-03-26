#!/usr/bin/python3
# loconet_serial_process.py
"""

        loconet_seriall_process - process class for loconet serial message processings

        Monitors loconet data bytes received through a serial port and interperts them.
        Specically look for railcom and block occpancy messages,  Whne received, data is forwarded
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

LNET_FORCE_IDLE_MESSAGE = 13  # 0x85
LNET_POWER_ON_MESSAGE = 131  # 0x83
LNET_POWER_OFF_MESSAGE = 130  # 0x82
LNET_MASTER_BUSY_MESSAGE = 129  # 0x81
LNET_SET_SLOT_DIR_MESSAGE = 161  # 0xA1
LNET_SET_SLOT_SOUND_MESSAGE = 162  # 0xA2
LNET_REQ_SWITCH_MESSAGE = 176  # 0xB0
LNET_TURNOUT_SENSOR_INPUT_MESSAGE = 177  # 0xB1
LNET_GENERAL_SENSOR_INPUT_MESSAGE = 178  # 0xB2
LNET_LONG_ACK_MESSAGE = 180  # 0xB4
LNET_WRITE_SLOT_MESSAGE = 181  # 0xB5
LNET_SET_FUNC_MESSAGE = 182  # 0xB6
LNET_UNLINK_SLOTs_MESSAGE = 184  # 0xB8
LNET_LINK_SLOTs_MESSAGE = 185  # 0xB9
LNET_MOVE_SLOTS_MESSAGE = 186  # 0xBA
LNET_REQUEST_SLOT_DATA_MESSAGE = 187  # 0xBB
LNET_SWITCH_STATE_MESSAGE = 188  # 0xBC
LNET_SWITCH_ACK_MESSAGE = 189  # 0xBD
LNET_TRANSPONDER_MESSAGE = 208  # D0
LNET_RAILCOM_SENSOR_MESSAGE = 224  # 0xE0
LNET_DATA_MOVE_MESSAGE = 229  # 0xE5
LNET_SLOT_DATA_MESSAGE = 231  # 0xE7
LNET_SEND_PACKET_MESSAGE = 237  # 0xED
LNET_WRITE_SLOT_MESSAGE = 238  # 0xEF


class LoconetSerialProcess(SerialProcess):
    """ Process Some Loconet Messages from Serial Port"""

    def __init__(self, events=None, queues=None):
        self.queues = queues
        # we don't have a separate driver process
        # redirect driver messages to application process
        self.queues[Global.DRIVER] = queues[Global.APPLICATION]
        super().__init__(events=events, queues=queues)

        self.bytes_queue = []
        self.bytes_queue_length_desired = 0
        self.message_type = {}
        self.message_type[LNET_FORCE_IDLE_MESSAGE] = 2
        self.message_type[LNET_POWER_ON_MESSAGE] = 2
        self.message_type[LNET_POWER_OFF_MESSAGE] = 2
        self.message_type[LNET_MASTER_BUSY_MESSAGE] = 2
        self.message_type[LNET_SET_SLOT_DIR_MESSAGE] = 4
        self.message_type[LNET_SET_SLOT_SOUND_MESSAGE] = 4
        self.message_type[LNET_REQ_SWITCH_MESSAGE] = 4
        self.message_type[LNET_TURNOUT_SENSOR_INPUT_MESSAGE] = 4
        self.message_type[LNET_GENERAL_SENSOR_INPUT_MESSAGE] = 4
        self.message_type[LNET_LONG_ACK_MESSAGE] = 4
        self.message_type[LNET_WRITE_SLOT_MESSAGE] = 4
        self.message_type[LNET_SET_FUNC_MESSAGE] = 4
        self.message_type[LNET_UNLINK_SLOTs_MESSAGE] = 4
        self.message_type[LNET_LINK_SLOTs_MESSAGE] = 4
        self.message_type[LNET_MOVE_SLOTS_MESSAGE] = 4
        self.message_type[LNET_REQUEST_SLOT_DATA_MESSAGE] = 4
        self.message_type[LNET_SWITCH_STATE_MESSAGE] = 4
        self.message_type[LNET_SWITCH_ACK_MESSAGE] = 4
        self.message_type[LNET_TRANSPONDER_MESSAGE] = 6
        self.message_type[LNET_RAILCOM_SENSOR_MESSAGE] = 9
        self.message_type[LNET_DATA_MOVE_MESSAGE] = 16
        self.message_type[LNET_SLOT_DATA_MESSAGE] = 10
        self.message_type[LNET_SEND_PACKET_MESSAGE] = -1
        self.message_type[LNET_WRITE_SLOT_MESSAGE] = 10

    def publish_input(self, serial_data):
        """ override method in parent class """
        # get input, one integer at a time
        # print(">>> Lnet Serial Input: " + str(serial_data) + " ... " + str(hex(serial_data)))
        self.bytes_queue.append(serial_data)
        message_processing_done = False
        while not message_processing_done:
            start_of_command = self.__find_start_of_next_command()
            if start_of_command is None:
                message_processing_done = True
            else:
                if start_of_command != 0:
                    # oops, partial message in queue, log it and purge it
                    sub_list = self.bytes_queue[0:start_of_command]
                    self.log_warning(
                        "Partial LNet message, purged: " + str(sub_list))
                    self.bytes_queue = self.bytes_queue[start_of_command:]
                    start_of_command = 0
                first_byte = self.bytes_queue[start_of_command]
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

    def publish_input_2(self, serial_data):
        """ override method in parent class """
        # get input, one integer at a time
        # print(">>> Lnet Int: " + str(hex(serial_data)))
        desired_message_length = self.message_type.get(serial_data, None)
        if desired_message_length is not None:
            if self.bytes_queue is not None:
                self.log_warning(
                    "Warning: incomplete message being dropperd: " +
                    str(hex(self.bytes_queue[0])))
            self.bytes_queue = []
            self.bytes_queue_length_desired = desired_message_length
        if self.bytes_queue is not None:
            self.bytes_queue.append(serial_data)
            if len(self.bytes_queue) == self.bytes_queue_length_desired:
                # hit max bytes for this message type
                self.__process_message_bytes(self.bytes_queue)
                self.bytes_queue = None
                self.bytes_queue_length_desired = 0

    #
    # private functions
    #

    def __publish_lnet_input(self, body):
        """ publish the interperted data"""
        self.app_queue.put(body)

    def __process_message_bytes(self, message_bytes):
        message_type = message_bytes[0]
        if message_type == LNET_GENERAL_SENSOR_INPUT_MESSAGE:
            message_map = self.__decode_block_message(message_bytes)
            self.log_info("Message received: Block, "+str(message_map))
            input_message = (Global.DEVICE_INPUT_BLOCK_DATA, {
                'data': message_map
            })
            self.__publish_lnet_input(input_message)
        elif message_type == LNET_RAILCOM_SENSOR_MESSAGE:
            message_map = self.__decode_railcom_message(message_bytes)
            self.log_info("Message received: Railcom, " + str(message_map))
            input_message = (Global.DEVICE_INPUT_RAILCOM_DATA, {
                'data': message_map
            })

            self.__publish_lnet_input(input_message)
        else:
            self.log_debug("Warning: Unknown Message Received: " +
                           str(hex(message_type)))

    def __decode_block_message(self, message_list):
        # int contactNum = ((SENSOR_ADR(in1, in2) - 1) * 2 + ((in2 & LnConstants.OPC_INPUT_REP_SW) != 0 ? 2 : 1));
        # (((a2 & 0x0f) * 128) + (a1 & 0x7f)) + 1;

        # get right mode 4 bits, shit left seven bits
        high_addr_byte = (message_list[2] & 0x0F) << 7

        # get the right most 7 bits
        low_addr_byte = message_list[1] & 0x7F

        # IO.inspect(low_addr_byte)
        addr = (high_addr_byte + low_addr_byte) * 2 + 1

        # get bit 5, slide to right
        l_code = (message_list[2] & 0x10) >> 4

        # get bit 6 , slide to right
        i_code = (message_list[2] & 0x20) >> 5

        device_type = None
        address = None
        state = None
        if i_code == 1:
            # switch
            address = addr + 1
            device_type = Global.SWITCH
            if l_code == 0:
                state = Global.OFF
            else:
                state = Global.ON
        elif i_code == 0:
            address = addr
            device_type = Global.SENSOR
            if l_code == 0:
                state = Global.OFF
            elif l_code == 1:
                state = Global.ON

        return {"type": device_type, "block": address, "state": state}

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
        """ find start of next lnet command, value > 127 """
        start = None
        if self.bytes_queue:
            for i, val in enumerate(self.bytes_queue):
                if val > 127:  # bit 7 set
                    start = i
                    break
        return start

    # def __process_message_bytes(self, message_bytes):
    #    decoded_message  = self.decode_lnet_message(message_bytes)
    #    if decoded_message is not None:
    #        self.__publish_lnet_input(decoded_message)
