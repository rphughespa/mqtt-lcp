# ic2rfid

"""

i2c_rfid.py - helper class to process i2c rfid devices

    supports sparkfun qwiic rfid reader

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
    from smbus2_go_lobo import SMBus
elif sys.platform.startswith("esp32"):
    from smbus2_esp32 import SMBus
else:
    from smbus2 import SMBus

# import time

from i2c_io_data import I2cIoData
from i2c_device import I2cDevice

class I2cRfid(I2cDevice):
    """ Class for an I2C connected RFID device"""

    def __init__(self, log_queue, input_queue, i2c_address, mqtt_port=None, mqtt_type=None,
                    itype="rfid", i2c_bus_number=1,
                    i2c_mux=None, i2c_sub_address=None):
        """ Initialize """
        super().__init__(log_queue, i2c_address, input_queue=input_queue,
                         i2c_device_type=itype, i2c_bus_number=i2c_bus_number,
                         i2c_mux=i2c_mux, i2c_sub_address=i2c_sub_address)
        self.mode = "input"
        self.mqtt_port = mqtt_port
        self.mqtt_type = mqtt_type
        self.sub_address = i2c_sub_address

    def read_input(self):
        """ Read input from RFID device"""
        #read rfid tag from reader
        #self.log_queue.add_message("info", 'Read rfid from: ' + str(self.i2c_address))
        if self.i2c_mux is not None:
            #print("Enable MUX: "_str(self.i2c_mux_port))
            self.i2c_mux.enable_mux_port(self.sub_address)
        tag = self.read_i2c_rfid_tag()
        if tag is not None:
            return_data = I2cIoData()
            return_data.i2c_type = "rfid"
            return_data.mqtt_type = "rfid"
            return_data.mqtt_port = self.mqtt_port
            return_data.reported = tag
            self.log_queue.add_message("debug", 'Received from rfid [' + str(return_data.reported) + ']')
            self.input_queue.put(return_data)
        if self.i2c_mux is not None:
            self.i2c_mux.disable_mux_port(self.sub_address)

    def read_i2c_rfid_tag(self):
        """ Read a tag"""
        tag_id = None
        tag = None
        self.log_queue.add_message("debug", "Read i2c: "+str(self.i2c_address))
        try:
            with SMBus(self.i2c_bus_number) as bus:
                if sys.platform.startswith("esp32_LoBo"):
                    tag = bus.readfrom_mem(self.i2c_address, 0x00, 10, False)
                elif sys.platform.startswith("esp32"):
                    tag = bus.readfrom_mem(self.i2c_address, 0, 10)
                else:
                    tag = bus.read_i2c_block_data(self.i2c_address, 0, 10)
                # print(" ... rfid tag: "+str(tag))
        except Exception as exc:
            self.log_queue.add_message("error", "Exception during rfid read: " +str(self.i2c_address)+ ", "+str(exc))
        # self.log_queue.add_message("info", "RFID Tag Read: "+str(tag))
        # convert to hex characters
        tag_complete = ""
        if tag is not None:
            for i in tag:
                char_hex = str(hex(i))
                if len(char_hex) > 2:
                    char_hex = char_hex[2:]
                if len(char_hex) < 2:
                    char_hex = "0"+char_hex
                # print(char_hex)
                tag_complete += char_hex
                #0x00x00x00x00x00x00
                #x00x00x00x86
            # self.log_queue.add_message("debug", "RFID Tag Read concat: "+str(tag_complete))
            # the first 6 hex bytes is the tag number, remove hex 'x' and ignore rest
            tag_id = tag_complete[:12]
            self.log_queue.add_message("debug", "RFID Tag Read stripped: "+str(tag_id))
            # randon get "8" set.  Remove them
            tag_id = tag_id.replace("8","0")
            # a tag of all zeros means no tag read
            if ((tag_id == "000000000000") or
                    (tag_id == "7fffffffffff")):  # no tag read
                tag_id = None
        return tag_id
