
# board_rp2040_pico_w.py
"""

BoardRp2040PicoW - a class for the Raspberry RP2040 Pic micro controller board


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
from machine import I2C, Pin




class BoardRp2040PicoW():
    """ a class for the Raspberry RP2040 Pico W micro controller board"""

    def __init__(self):
        """ initialize """
        self.i2c_bus = I2C(0, sda=Pin(16), scl=Pin(17), freq=100000)
        print("I2c Devices: "+str(self.i2c_bus.scan()))
        self.led = Pin("LED", Pin.OUT)

    def led_on(self):
        """ set board led on """
        self.led.on()

    def led_off(self):
        """ turn board led off """
        self.led.off()
