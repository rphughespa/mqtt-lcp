# ic2_display

"""

i2c_display.py - helper class to process i2c display devices
        It support two SSD type I2C connected displays:
            ssd1306 : 128x64
            ssd1327 : 128x128

    supports ssd1306 oled displays

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
from i2c_device import I2cDevice

if sys.platform.startswith("esp32"):
    from display_ssd1306_esp32 import Display
else:
    from display_ssd1306_py import Display

from global_constants import Global

class I2cDisplay(I2cDevice):
    """ Class for an I2C connected display device """
    def __init__(self, log_queue, i2c_address,
                    display_type=None, display_size=None,
                    i2c_bus_number=1, i2c_mux=None, i2c_sub_address=None, log_level="info"):
        super().__init__(log_queue, i2c_address,
                         i2c_device_type="display", i2c_bus_number=i2c_bus_number,
                         i2c_sub_address=i2c_sub_address)
        self.mode = "output"
        self.log_level = self.set_log_level(log_level)
        self.i2c_bus_number = i2c_bus_number
        self.i2c_address = i2c_address
        self.display_type = display_type
        # display size should be  a string like: "128x32" or "128x64"
        self.display_size = display_size
        self.display = None
        # print("Display: "+str(self.display_type)+", "+str(self.i2c_address))
        if self.display_type == "ssd1306":
            self.display = Display(self.i2c_bus_number, self.i2c_address, self.display_size)
        elif self.display_type == "ssd1327":
            self.display = Display(self.i2c_bus_number, self.i2c_address, self.display_size)
        # print("display: "+str(self.i2c_bus_number)+", "+str(self.i2c_address))
        self.display.clear()
        self.display.splash(title="Ready")

    def set_log_level(self, level):
        """ set log level """
        level = level.upper()
        log_level = Global.LOG_LEVEL_DEBUG
        if level == "DEBUG":
            log_level = Global.LOG_LEVEL_DEBUG
        elif level == "INFO":
            log_level = Global.LOG_LEVEL_INFO
        elif level in ("WARN", "WARNING"):
            log_level = Global.LOG_LEVEL_WARNING
        elif level == "ERROR":
            log_level = Global.LOG_LEVEL_ERROR
        elif level == "CRITICAL":
            log_level = Global.LOG_LEVEL_CRITICAL
        elif level == "CONSOLE":
            log_level = Global.LOG_LEVEL_CONSOLE
        return log_level

    def write_message(self, message):
        """ write messages """
        self.display.scroll_message(message)

    def write_log_message(self, level, message):
        """ write log message """
        # print("Display Log: ...  "+str(self.log_level)+".."+level+" : "+message)
        if level >= self.log_level:
            self.display.scroll_message(message)

    def write_one_log_messages(self, display_queue):
        """ write a single log message to output """
        if self.display is not None:
            # print("display type: "+type(self.display))
            level, message = display_queue.get()
            if message is not None:
                self.write_log_message(level, message)

    def write_log_messages(self, display_queue):
        """ write multiple log messages to output """
        #print("display...")
        if self.display is not None:
            # print("display type: "+type(self.display))
            level, message = display_queue.get()
            while message is not None:
                self.write_log_message(level, message)
                level, message = display_queue.get()
