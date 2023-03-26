#!/usr/bin/python3
# bit_utils.py
"""


   BitUtils.py - utility bit oriented functionx

The MIT License (MIT)

Copyright 2021 richard p hughes

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

import binascii


class BitUtils(object):
    """ help class for bit operations """
    def __init__(self):
        pass

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    @classmethod
    def set_a_bit(cls, int_num, offset):
        """ Set a bit in an integer"""
        # offset is 0-7
        mask = 1 << offset
        rett = int_num | mask
        #if int_num != 0:
        #    print(">>> set: "+str(int_num) + " ... " + str(offset) + " ... "+str(rett))
        return rett

    @classmethod
    def clear_a_bit(cls, int_num, offset):
        """ Clear a bit in an integer"""
        # offset is 0-7
        mask = ~(1 << offset)
        rett = int_num & mask
        #if int_num != 0:
        #    print(">>> clear: "+str(int_num) + " ... " + str(offset) +" ... "+str(rett))
        return rett

    @classmethod
    def is_bit_set(cls, int_num, offset):
        """ Is the sepcified bit set """
        temp = int_num >> offset
        return (temp & 1) == 1

    @classmethod
    def bits_different(cls, int_one, int_two):
        """ Compare two bytes, return int of changed bits """
        int_diff = int_one ^ int_two
        return int_diff

    @classmethod
    def string_to_hex_list(cls, in_string):
        """ convert a string into a list of hex values """
        hex_list = []
        for c in list(in_string):
            bytes_str = bytes(c, 'utf-8')
            hex_nums = binascii.hexlify(bytes_str)
            hex_fix = str(hex_nums).replace("b\'", "0x").replace("\'", "")
            hex_list.append(hex_fix)
        return hex_list
