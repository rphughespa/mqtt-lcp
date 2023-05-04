
# board_qt_esp32_pico.py
"""

BoardQtEsp32Pico - a class for the Aadafruit Qt ESP32 Pico micro controller board


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
#from neopixel import NeoPixel
from machine import Pin, I2C



class BoardQtEsp32Pico():
    """ a class for the Adafruit Qt ESP32 Pico micro controller board """

    def __init__(self):
        self.i2c_bus = I2C(1, sda=Pin(22), scl=Pin(19), freq=100000)
        print("I2c Devices: "+str(self.i2c_bus.scan()))
        #self.power_pin = Pin(8, Pin.OUT)  # NeoPixel power is on pin 8
        #self.power_pin.on()  # Enable the NeoPixel Power
        #self.pin = Pin(5, Pin.OUT)  # Onboard NeoPixel is on pin 5
        #self.np = NeoPixel(self.pin, 1)

    def led_on(self):
        #self.np.fill((0, 128, 0))  # Set the NeoPixel green
        #self.np.write()
        pass

    def led_off(self):
        #self.np.fill((0, 0, 0))  # Turn the NeoPixel off
        #self.np.write()
        pass
