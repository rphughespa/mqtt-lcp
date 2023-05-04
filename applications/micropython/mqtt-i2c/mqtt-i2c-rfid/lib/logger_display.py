
# logger_display.py
"""

LoggerDisplay - class for log messages toi2c display.
    Messages are queued and then written out later when I2C bus is not busy.


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
import collections
from ssd1306 import SSD1306_I2C

from logger_console import LoggerConsole

SSD1306_128x64 = "ssd1306-128x64"
SSD1306_128x32 = "ssd1306-128x32"

class LoggerDisplay(LoggerConsole):
    """ a class for a console logger """

    def __init__(self, i2c_bus, io_address, display_type):
        """ initialize the logger """
        super().__init__()
        self.i2c_bus = i2c_bus
        self.io_addrerss = io_address
        self.display_type = display_type
        self.line_height = 8
        self.line_per_screen = 8
        self.screen_height = 64
        self.screen_width = 128
        self.line_buffer = []
        self.initialize_display()

    def initialize_display(self):
        """ initialze the display screen """
        if self.display_type == SSD1306_128x32:
            self.screen_height = 32
            self.screen_width = 128
        self.display = SSD1306_I2C(self.screen_width, self.screen_height, self.i2c_bus)
        self.lines_per_screen = int(self.screen_height / self.line_height)
        for _l in range(self.lines_per_screen):
            self.line_buffer.append("")

    def write_line_to_output(self, line):
        """ write line to output device """
        super().write_line_to_output(line)
        self.__add_line_to_buffer(line)
        self.__display_line_buffer()

    #
    # private functions
    #

    def __add_line_to_buffer(self, new_line):
        line = new_line
        line_2 = None
        if line is None:
            line = ""
        if len(new_line) > 16:
            line = new_line[:16]
            line_2 = new_line[16:]
        for l in range(len(self.line_buffer)-1):
            self.line_buffer[l] = self.line_buffer[l+1]
        self.line_buffer[len(self.line_buffer)-1] = line
        if line_2 is not None:
            for l in range(len(self.line_buffer)-1):
                self.line_buffer[l] = self.line_buffer[l+1]
            self.line_buffer[len(self.line_buffer)-1] = "  " + line_2

    def __display_line_buffer(self):
        self.display.fill(0)
        pos = 0
        for line in self.line_buffer:
            self.display.text(line, 0, pos)
            pos += self.line_height
        self.display.show()
