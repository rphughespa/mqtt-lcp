# keyboard_client.py


"""

    keyboard_client.py - helper class to process keyboard input


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


import errno
import threading
from queue_py import Queue

BUFFER_LENGTH = 4096



class KeyboardReader(threading.Thread):
    """ Device class for processing keyboard input thread"""
    def __init__(self, log_queue, thread_name):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.key_in_queue = Queue(100)
        self.client_socket = None
        self.log_queue = log_queue
        self.exit = False

    def run(self):
        """Run the thread"""
        while not self.exit:
            try:
                # Now we want to loop over received messages
                # (there might be more than one) and print them
                message_text = input("> ")
                new_message = {'text': message_text}
                self.log_queue.add_message("debug", 'Received from keyboard [' + message_text + ']')
                self.key_in_queue.put(new_message)
            except (KeyboardInterrupt, SystemExit):
                raise
            except IOError as exc:
                # This is normal on non blocking connections -
                # when there are no incoming data error is going to be raised
                # Some operating systems will indicate that using AGAIN,
                # nd some using WOULDBLOCK error code
                # We are going to check for both - if one of them -
                # that's expected, means no incoming data, continue as normal
                # If we got different error code - something happened
                if exc.errno != errno.EAGAIN and exc.errno != errno.EWOULDBLOCK:
                    self.log_queue.add_message("debug", 'Reading error: {}' + str(exc))
                continue

            except Exception as exc:
                self.log_queue.add_message("debug", 'Reading error: ' + str(exc))
                continue

    def shutdown(self):
        """ Shutdown the thread"""
        self.exit = True
        self.join()


    def get_incomming_message_from_queue(self):
        """ Get keypoard input from queue"""
        message = None
        if not self.key_in_queue.empty():
            message = self.key_in_queue.get()
        return message
