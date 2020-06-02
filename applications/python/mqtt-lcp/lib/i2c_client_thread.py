# i2c_client_thread.py

"""

i2c_client_thread.py - helper class to process i2c devices via a reader / writter thread

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
# platforms for esp32 = esp32, for lobo esp32 = esp32_LoBo, for pi = linux
if sys.platform.startswith("esp32_LoBo"):
    from threading_lobo import Thread
elif sys.platform.startswith("esp32"):
    from threading_esp32 import Thread
else:
    from threading import Thread

import time


from i2c_client import I2cClientReaderWriter


class I2cClientThread(Thread):
    """ Runs two separate I2C reader and writer threads"""

    def __init__(self, log_queue, devices, in_queue, out_queue, display_queue, thread_name, i2c_config):
        """ Initialize"""
        Thread.__init__(self)
        self.thread_name = thread_name
        self.i2c_in_queue = in_queue
        self.i2c_out_queue = out_queue
        self.i2c_config = i2c_config
        self.client_i2c = None
        self.i2c_readerwriter = None
        self.log_queue = log_queue
        self.display_queue = display_queue
        # print("start i2c client")
        self.i2c_reader_writer = I2cClientReaderWriter(self.log_queue, devices,
                self.i2c_in_queue, self.i2c_out_queue, self.display_queue)
        self.exit = False


    def run(self):
        """ Create separate reader and writer thraeds and start them"""
        # print("start i2c thread")
        self.i2c_reader_writer.start()
        # print("after start")
        time.sleep(0.5)
        self.log_queue.add_message("info", 'I2C Client Thread Started...')
        if sys.platform.startswith("esp32_LoBo"):
            pass
        else:
            while not self.exit:
                try:
                    time.sleep(0.1)
                    self.i2c_reader_writer.process_devices()
                except (KeyboardInterrupt, SystemExit):
                    raise

    def i2c_process_devices_loop(self):
        """ processing loop """
        # threading is different in lobo micropython
        if sys.platform.startswith("esp32_LoBo"):
            _thread.allowsuspend(True)
            while True:
                ntf = _thread.getnotification()
                if ntf:
                    # some notification received
                    if ntf == _thread.EXIT:
                        return
                self.i2c_reader_writer.process_devices()
                time.sleep(0.1)
        else:
            pass

    def check_msg(self):
        if sys.platform.startswith("esp32_LoBo"):
            self.button_reader.check_buttons()
            self.i2c_reader_writer.process_devices()
        else:
            pass


    def shutdown(self):
        """ Shutdown both reader and writer threads"""
        self.log_queue.add_message("info", "Exiting i2c Client")
        self.exit = True
        if sys.platform.startswith("esp32_LoBo"):
            if self.loop_thread_id is not None:
                _thread.stop(self.loop_thread_id)
                self.i2c_reader_writer.shutdown()
                self.i2c_reader_writer.exit()
        elif sys.platform.startswith("esp32"):
            self.i2c_reader_writer.shutdown()
            # self.console_thread.join()
            self.i2c_reader_writer.exit()
        else:
            self.i2c_reader_writer.shutdown()
            # self.console_thread.join()
            #self.i2c_reader_writer.join()
            self.join()

