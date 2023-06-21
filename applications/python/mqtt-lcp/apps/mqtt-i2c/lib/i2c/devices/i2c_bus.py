#!/usr/bin/python3
# # ic2_bus.py
"""

I2cBus - thin wrapper around smbus2 adding retries on block read and write


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

sys.path.append('../../lib')

import time


from smbus2 import SMBus
from utils.global_constants import Global


class I2cBus(SMBus):
    """ Class for an I2C connected mux device"""

    def __init__(self, bus_number, log_queue):
        """ Initialize """
        super().__init__(bus_number)
        self.log_queue = log_queue

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def write_i2c_byte_data(self, i2c_addr, register, data):
        """ write a byte to i2c bus """
        tries = 3
        io_ok = False
        while tries > 0 and not io_ok:
            tries +=1
            (io_ok,exc) = \
                    self.__write_byte_catch_exception(i2c_addr, register, data)
            if not io_ok:
                # oops, we got an exception, wait a bit and retry
                time.sleep(0.2)
        if not io_ok:
            # give up, pass along exception
            self.log_queue.put(
                (Global.LOG_LEVEL_ERROR, "Exception during i2c_write: " + str(exc) +
                    " ... " + str(i2c_addr)))

    def write_i2c_block_data(self, i2c_addr, register, data, force=None):
        """ wrute a block of data """
        tries = 3
        io_ok = False
        while tries > 0 and not io_ok:
            tries +=1
            (io_ok,exc) = \
                    self.__write_block_catch_exception(\
                            i2c_addr, register, data, force)
            if not io_ok:
                # oops, we got an exception, wait a bit and retry
                time.sleep(0.2)
        if not io_ok:
            # give up, pass along exception
            self.log_queue.put(
                (Global.LOG_LEVEL_ERROR, "Exception during i2c_write: " + str(exc) +
                    " ... " + str(i2c_addr)))

    def read_i2c_byte_data(self, i2c_addr, register, length):
        """ read a block of data"""
        rett = None
        tries = 3
        io_ok = False
        while tries > 0 and not io_ok:
            tries -= 1
            (io_ok, exc,rett) \
                    = self.__read_byte_catch_exception(\
                        i2c_addr, register, length)
            if not io_ok:
                # oops, we got an exception, wait a bit and retry
                time.sleep(0.2)
        if not io_ok:
            # give up, pass along exception
            self.log_queue.put(
                (Global.LOG_LEVEL_WARNING, "Exception during i2c_read: " + str(exc) +
                    " ... " + str(i2c_addr)))
            # raise exc
        return rett

    def read_i2c_block_data(self, i2c_addr, register, length, force=None):
        """ read a block of data"""
        rett = None
        tries = 3
        io_ok = False
        while tries > 0 and not io_ok:
            tries -= 1
            (io_ok, exc,rett) \
                    = self.__read_block_catch_exception(\
                        i2c_addr, register, length, force)
            if not io_ok:
                # oops, we got an exception, wait a bit and retry
                time.sleep(0.2)
        if not io_ok:
            # give up, pass along exception
            self.log_queue.put(
                (Global.LOG_LEVEL_WARNING, "Exception during i2c_read: " + str(exc) +
                    " ... " + str(i2c_addr)))
            # raise exc
        return rett

    #def scan(self):
    #    """ scna the i2c bus, report device found """
    #    found = []
    #    for device in range(128):
    #        try:
    #            super().read_byte_data(device, 0, 1)
    #            found.append(device)
    #        except: # exception if read_byte fails
    #            pass
    #    return found

#
#   private functions
#

    def __write_byte_catch_exception(self, i2c_addr, register, data):
        io_ok = True
        exc = None
        try:
            super().write_byte_data(i2c_addr, register, data)
        except OSError as excp:
            io_ok = False
            exc = excp
            self.log_queue.put((Global.LOG_LEVEL_DEBUG,
                                "Exception during i2c_write: " + str(exc)))
        return(io_ok, exc)

    def __write_block_catch_exception(self, i2c_addr, register, data, force):
        io_ok = True
        exc = None
        try:
            super().write_i2c_block_data(i2c_addr, register, data, force)
        except OSError as excp:
            io_ok = False
            exc = excp
            self.log_queue.put((Global.LOG_LEVEL_DEBUG,
                                "Exception during i2c_write: " + str(exc)))

        return (io_ok, exc)

    def __read_byte_catch_exception(self, i2c_addr, register, length):
        io_ok = True
        exc = None
        rett = None
        # print(">>> I2C read from: "+str(i2c_addr) + " ... "+str(register))
        try:
            rett = super().read_byte_data(\
                    i2c_addr, register, length)
        except OSError as excp:
            io_ok = False
            exc = excp
            self.log_queue.put((Global.LOG_LEVEL_DEBUG,
                                "Exception during i2c_read: " + str(exc)))
        return (io_ok, exc, rett)

    def __read_block_catch_exception(self, i2c_addr, register, length, force):
        io_ok = True
        exc = None
        rett = None
        # print(">>> I2C read from: "+str(i2c_addr) + " ... "+str(register))
        try:
            rett = super().read_i2c_block_data(i2c_addr, register, length,
                                               force)
        except OSError as excp:
            io_ok = False
            exc = excp
            self.log_queue.put((Global.LOG_LEVEL_DEBUG,
                                "Exception during i2c_read: " + str(exc)))
        return (io_ok, exc, rett)
