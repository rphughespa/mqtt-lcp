#!/usr/bin/python3
# ic2_rfid_attiny64.py
"""

I2cRfidAttiny64 - low level hardware driver fot a rdif reader connected to i2c using the attiny64 circuit device


    supports sparkfun qwiic rfid reader

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

sys.path.append('../../../lib')

# from global_constants import Global

from i2c.devices.i2c_base_device import I2cBaseDevice


class I2cRfidAttiny64(I2cBaseDevice):
    """ Class for an I2C connected RFID device"""
    def __init__(self, i2c_address=None, i2c_bus=None, log_queue=None):
        """ Initialize """
        super().__init__(name="i2c_rfid_atting64",
                         i2c_address=i2c_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)
        self.__initialize_device()

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def read_input(self):
        """ Read input from RFID device"""
        #read rfid tag from reader
        return_data = []
        tag = self.__read_i2c_rfid_tag()
        while tag is not None:
            return_data.append(tag)
            tag = self.__read_i2c_rfid_tag()
        return return_data

    def __read_i2c_rfid_tag(self):
        """ Read a tag"""
        tag_id = None
        tag = None
        # self.log_debug("Read i2c: "+str(io_address))
        try:
            tag = self.i2c_bus.read_i2c_block_data(self.i2c_address, 0, 10)
            # print(" ... rfid tag: "+str(tag))
        except Exception as exc:
            if "[Errno 121]" not in str(exc):
                self.log_debug("Exception during rfid read: " +
                               str(self.i2c_address) + ", " + str(exc))
        # self.log_debug("RFID Tag Read: "+str(tag))
        # convert to hex characters
        tag_complete = ""
        if tag is not None:
            for i in tag:
                char_hex = str(hex(i))
                if len(char_hex) > 2:
                    char_hex = char_hex[2:]
                if len(char_hex) < 2:
                    char_hex = "0" + char_hex
                # print(char_hex)
                tag_complete += char_hex
                #0x00x00x00x00x00x00
                #x00x00x00x86
            # self.log_debug("RFID Tag Read concat: "+str(tag_complete))
            # the first 6 hex bytes is the tag number, remove hex 'x' and ignore rest
            tag_id = tag_complete[:12]
            #if tag_id != "000000000000":
            #    print(tag_id)
            #    self.log_debug("RFID Tag Read stripped: "+str(tag_id)))
            if not self.__tag_is_ok(tag_id):
                tag_id = None
            else:
                self.log_debug("RFID Tag Read stripped: " + str(tag_id))
        return tag_id

    def __tag_is_ok(self, tag_id):
        tag_ok = False
        # randon get "8" set.  Remove them
        tag_checked = tag_id.replace("7", "")
        tag_checked = tag_checked.replace("8", "")
        tag_checked = tag_checked.replace("0", "")
        tag_checked = tag_checked.replace("F", "")
        tag_checked = tag_checked.replace("f", "")
        if tag_checked:
            # print(">>> "+str(tag_checked))
            tag_ok = True
        return tag_ok

    def __initialize_device(self):
        """ initialize the device """
        pass
