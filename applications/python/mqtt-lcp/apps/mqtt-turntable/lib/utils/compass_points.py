#!/usr/bin/python3
# compass_points.py
"""


   CompassPoints - functions that help deal wirth compass points, North, South, etc

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



import time
import sys

sys.path.append('../../lib')

from utils.global_constants import Global

class CompassPoints(object):
    """ helper class compass points functions """

    def __init__(self):
        pass

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    @classmethod
    def is_valid(cls, point):
        """ calc now seconds """
        rett = point in [Global.NORTH, Global.EAST, Global.SOUTH, Global.WEST]
        return rett
    @classmethod
    def reverse_direction(cls, point):
        """ return the opposite compass point """
        rett = point
        if point == Global.NORTH:
            rett = Global.SOUTH
        elif point == Global.EAST:
            rett = Global.WEST
        elif point == Global.SOUTH:
            rett = Global.NORTH
        elif point == Global.WEST:
            rett = Global.EAST
        return rett
