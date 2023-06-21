#!/usr/bin/python3
# withrottle_const.py
"""

	withrottle_const.py - helper class with const vales used in withrottle messaging.


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
OUT OFSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""


class WithrottleConst(object):
    """ data struct for decodec withrottle message """
    CLOSED = 2
    THROWN = 4
    UNKNOWN = 1
    INCONSISTENT = 0
    ACTIVE = 2
    INACTIVE = 4
    FORWARD = 1
    REVERSE = 0
    MAJOR_SEP = "]\\["
    MINOR_SEP = "}|{"
    SUB_SEP = "<;>"
    PORT_SEP = ":"
    ACTIVATED = "Activated"
    DEACTIVATED = "Deactivated"
