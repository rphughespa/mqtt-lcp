# display_ssd1306_py - manage display on i2c bus
"""

    display_ssd1306_py.py - display info on a ssd1306 atteached to i2c bus on full python platform
        based on luma oled terminal example

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
sys.path[1] = '../lib'

import os
import time
from PIL import ImageFont
from luma.core.virtual import terminal
from luma.core import cmdline, error, __version__

LEVEL_CRITICAL = 50
LEVEL_ERROR = 40
LEVEL_WARNING = 30
LEVEL_INFO = 20
LEVEL_DEBUG = 10
LEVEL_NOTSET = 0

class Display:
    """ Control SSD1306 display """

    def __init__(self, bus, addr, _size):
        """ Initialize """
        self.log_level = LEVEL_NOTSET
        self.term = None
        self.bus = bus
        self.addr = addr
        self.line = 4
        self.width = 128
        self.height = 64
        self.oled = None
        self.msg_list = []
        self.max_msg_lines = 10
        self.display_lines_array = []
        self.font = self.make_font("ProggyTiny.ttf", 18)
        #self.font = self.make_font("tiny.ttf", 16)
        self.device = self.get_device(['--display', 'ssd1306', '--width',
            str(self.width), '--height', str(self.height), '--i2c-port',
            str(self.bus), '--i2c-address', str(self.addr)])
        self.term = terminal(self.device, self.font, animate=False)

    def make_font(self, name, size):
        """ set font """
        font_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../lib/fonts', name))
        return ImageFont.truetype(font_path, size)

    def clear(self):
        """ clear screen """
        self.term.clear()

    def splash(self, title="MQTT NODE"):
        """ display splash screen """
        self.term.println("")
        self.term.println(title.upper())
        self.term.println("")

    def scroll_message(self, message):
        """ scrool a message """
        # print("<<< "+message+" >>>")
        self.term.println(message)

    def scroll_error_message(self, message):
        """ scroll error message """
        self.term.println(message)

    def _display_footer(self, message):
        """ display a footer message """
        self.term.println(message)

    def footer_message(self, message):
        """ display a footer message """
        self.term.println(message)

    def footer_error_message(self, message):
        """ format an error message """
        self.term.println(message)



# logging
#logging.basicConfig(
#    level=logging.DEBUG,
#    format='%(asctime)-15s - %(message)s'
#)
# ignore PIL debug messages
#logging.getLogger('PIL').setLevel(logging.ERROR)


    def display_settings(self, args):
        """ Display a short summary of the settings. :rtype: str """
        iface = ''
        display_types = cmdline.get_display_types()
        if args.display not in display_types['emulator']:
            iface = 'Interface: {}\n'.format(args.interface)

        lib_name = cmdline.get_library_for_display_type(args.display)
        if lib_name is not None:
            lib_version = cmdline.get_library_version(lib_name)
        else:
            lib_name = lib_version = 'unknown'


        version = 'luma.{} {} (luma.core {})'.format(
            lib_name, lib_version, __version__)

        return 'Version: {}\nDisplay: {}\n{}Dimensions: {} x {}\n{}'.format(
            version, args.display, iface, args.width, args.height, '-' * 60)


    def get_device(self, actual_args=None):
        """
        Create device from command-line arguments and return it.
        """

        if actual_args is None:
            actual_args = sys.argv[1:]
            # actual_args = ['--display', 'ssd1306', '--width', '128',
            #   '--height', '64', '--i2c-port', '1', '--i2c-address', '0x3c']
        parser = cmdline.create_parser(description='luma.examples arguments')
        args = parser.parse_args(actual_args)

        if args.config:
            # load config from file
            config = cmdline.load_config(args.config)
            args = parser.parse_args(config + actual_args)

        print(self.display_settings(args))


        # create device
        # display ssd1306  --width 128 --height 64 --i2c-port 1 --i2c-address 0x3c
        try:
            device = cmdline.create_device(args)
        except error.Error as e:
            parser.error(e)

        return device
