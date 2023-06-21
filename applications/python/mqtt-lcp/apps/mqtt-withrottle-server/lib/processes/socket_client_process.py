#!/usr/bin/python3
# socker_server_process.py
"""

        socker_server_process - process class for a socker server
            open a socket port and waits for incomming connections

            Assumes message traffic is text based and delimited by "\n"


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
import sys

sys.path.append('../../lib')

import binascii
import time
import socket
import select
from queue import Queue

from utils.global_constants import Global

from processes.base_process import BaseProcess

BUFFER_LENGTH = 4096


class SocketClientProcess(BaseProcess):
    """
        connects to socket and passes info to application
        either accepts a establihes connection
        or it create a new connection to a host/port
    """
    def __init__(self,
                 identity=None,
                 mode=None,
                 connection=None,
                 address=None,
                 events=None,
                 queues=None,
                 host=None,
                 port=None,
                 socket_mode="text"):
        super().__init__(name=mode + ":" + identity,
                        events=events,
                        in_queue=queues[Global.DEVICE],
                        app_queue=queues[Global.APPLICATION],
                        log_queue=queues[Global.LOGGER])
        self.identity = identity
        self.mode = mode
        self.queues = queues
        self.driver_queue = queues[Global.DRIVER]
        self.client_socket = connection
        self.address = address
        self.client_host = host
        self.client_ip_address = None
        self.client_port = port
        self.socket_mode = socket_mode
        self.clients_list = []
        self.data_queue = ""
        self.output_queue = Queue(100)

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def initialize_process(self):
        """ iitialize this process """
        super().initialize_process()
        self.log_info("Init socket client")
        if self.client_socket is None:
            if self.client_host is None:
                (self.client_host, self.client_port, self.socket_mode) = \
                    self.__parse_config(self.config, self.host_name)
            if self.client_host is None:
                self.log_critical("Error: Configuration error: "+\
                        "Missing io/network/server/host")
            else:
                try:
                    self.client_ip_address = socket.gethostbyname(
                        self.client_host)
                except Exception as exc:
                    self.log_critical("Error: Configuration error: "+\
                        "Invalid io/network/server/host: {"+\
                            str(self.client_host)+"}\n ... "+str(exc))

            if self.client_ip_address is None:
                self.log_critical(
                    "Error: Configuration error: IP address not defined")
            elif self.client_port is None:
                self.log_critical(
                    "Error: Configuration error: port number not defined")
            else:
                self.log_info("Open socket: " + str(self.client_host) + \
                            " ... " + str(self.client_port) + \
                            " ... Text Mode: " + str(self.socket_mode))
                self.client_socket = socket.socket(socket.AF_INET,
                                                   socket.SOCK_STREAM)
                self.client_socket.connect(
                    (self.client_host, self.client_port))
        if self.client_socket is None:
            self.log_error("Error: client socket not established")
        else:
            self.client_socket.setblocking(False)
            self.clients_list = [self.client_socket]

    def process_message(self, new_message=None):
        """ Process received message """
        #print(">>> send message: "+str(new_message))
        msg_consummed = super().process_message(new_message)
        if not msg_consummed:
            # self.log_info("Socket Send: " + str(new_message))
            (msg_type, msg_map) = new_message
            msg_text = msg_map
            if isinstance(msg_map, dict):
                msg_text = msg_map[Global.TEXT]
            encoded_msg_text = self.encode_message(msg_text)
            if msg_type == Global.DEVICE_SEND:
                if self.client_socket is not None:
                    self.__send_message(encoded_msg_text)
                    msg_consummed = True
            elif msg_type == Global.DEVICE_SEND_AND_RESPOND:
                if self.client_socket is not None:
                    self.__send_message(encoded_msg_text)
                    # print(">>> wait for response...")
                    message = self.__perform_async_io(0.1)
                    # print(">>> ... response..." + str(message))
                    self.publish_response(message,msg_map[Global.RESPONSE_QUEUE])
                    msg_consummed = True
        return msg_consummed

    def process_other(self):
        """ perform other none message relared tasks """
        super().process_other()
        if self.client_socket is not None:
            message = self.__perform_async_io(0.01)
            if message is not None:
                #print(">>> socket other: " + str(message))
                if isinstance(message, list):
                    for message_line in message:
                        self.publish_input(message_line)
                else:
                    self.publish_input(message)

    def publish_input(self, serial_data):
        """ publish serial input """
        message = (Global.DEVICE_INPUT, serial_data)
        if self.driver_queue is not None:
            self.driver_queue.put(message)
        else:
            self.send_to_application(message)

    def publish_response(self, serial_data, response_queue):
        """ publish serial input """
        message = (Global.DEVICE_RESPONSE, serial_data)
        resp_queue = self.queues.get(response_queue, None)
        # print(">>> socket response: " + str(response_queue) + " ... " + str(resp_queue))
        if resp_queue is not None:
            resp_queue.put(message)

    def shutdown_process(self):
        """ close client socket"""
        # print(">>> closing socket_client_process")
        self.__close_client_connection()
        super().shutdown_process()

    def encode_message(self, msg_body):
        """ translate data read from serial port """
        return msg_body

    def decode_message(self, msg_body):
        """ translate data read from serial port """
        return msg_body

    #
    # private functions
    #
    def __perform_async_io(self, timeout):
        """ perform async I/O: read from serial device without first sending data """
        # check for unsolicited input from serial device
        time_waited = 0
        rett = None
        while time_waited < timeout:
            if self.socket_mode == Global.TEXT:
                rett = self.__read_socket_io_by_line()
            else:
                rett = self.__read_socket_io_by_char()
            if rett is not None:
                break
            time.sleep(0.02)
            time_waited += 0.02
        return rett

    def __read_socket_io_by_line(self):
        """ read a message from serial device """
        # print(">>> read serial by line...")
        rett = None
        bytes_read = self.__perform_socket_read()
        if bytes_read is not None:
            #print(">>> bytes: " + str(bytes_read))
            message_fixed = bytes_read.replace("\r\n",
                        "\n").replace("\r", "\n")
            self.data_queue += message_fixed
            message_lines = self.data_queue.split("\n")
            #print(">>> lines: " + str(message_lines))
            # check to see is last line ended with \n
            if self.data_queue.endswith("\n"):
                # last line is OK
                self.data_queue = ""
            else:
                # last line is a partial, leave it in data_queue
                self.data_queue = message_lines[-1]
                message_lines = message_lines[:-1]
            rett = []
            for line in message_lines:
                #print(">>> line..." + str(line))
                if line != '':
                    decoded = self.decode_message(line)
                    #print(">>> ... decoded..." + str(decoded))
                    if isinstance(decoded, list):
                        # a single lnet message can generate multiple decoded messages
                        for lmessage in decoded:
                            rett.append(lmessage)
                    else:
                        rett.append(decoded)
        if rett is not None:
            self.log_debug("Socket Read . :" + str(rett))
        return rett

    def __read_socket_io_by_char(self):
        """ read a message from serial device """
        # print(">>> read serial by char...")
        rett = None
        bytes_read = self.__perform_socket_read()
        if bytes_read is not None:
            rett = list(bytes_read)
        if rett is not None:
            self.log_debug("Socket Read .. :" + str(rett))
        return rett

    def __perform_socket_read(self):
        read_sockets, write_sockets, exception_sockets = \
                select.select(self.clients_list, self.clients_list, self.clients_list, 0)
        # Iterate over notified sockets
        rett = None
        for notified_socket in read_sockets:
            message_bin = self.__receive_message(notified_socket)
            #print(">>> socket io: " + str(message_bin))
            # If False, client disconnected, cleanup
            if message_bin is False:
                self.log_info("Connection closed by client")
                self.send_to_application((Global.DEVICE_CLOSE, self.identity))
                self.__close_client_connection()
            else:
                # Get user by notified socket, so we will know who sent the message
                message_hex = binascii.hexlify(message_bin)
                self.log_debug("socket message received: " + str(message_hex))
                # message = message_bin.decode("utf8")
                rett = message_bin.decode(" ISO-8859-1")

        for notified_socket in write_sockets:
            if not self.output_queue.empty():
                message = self.output_queue.get(timeout=1)
                self.log_debug("Socket Device Send: " + str(message))
                self.__write_message_to_socket(message)

        for notified_socket in exception_sockets:
            self.__close_client_connection()
            self.log_warning("Warning: socket return exception: " +
                             str(self.identity))
            self.send_to_application((Global.DEVICE_ERROR, None))
        #if rett is not None:
        #    print(">>> bytes returned: " + str(rett))
        return rett

    def __receive_message(self, client_socket):
        """ Handle received messages"""
        try:
            return_bytes = ""
            return_bytes = client_socket.recv(BUFFER_LENGTH)
            if not return_bytes:
                return_bytes = False
            # print(">>> bytes in: "+str(return_bytes))
            return return_bytes
        except (KeyboardInterrupt, SystemExit):
            self.log_debug("keyboard or system exit")
            raise
        except Exception as _exc:
            # If we are here, client closed connection violently,
            # for example by pressing ctrl+c on his script
            # or just lost his connection
            # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR)
            # what sends information about closing the socket (shutdown read/write)
            # and that's also a cause when we receive an empty message
            return False

    def __close_client_connection(self):
        """ Close a client connection"""
        self.log_info('Closed connection from: ' + str(self.identity))
        if self.client_socket is not None:
            self.client_socket.close()
            self.client_socket = None

    def __send_message(self, message):
        """ enque message to be sent to device"""
        # print(">>> socket send: " + str(message))
        self.output_queue.put(message)

    def __write_message_to_socket(self, message):
        out_text = message
        if self.socket_mode == Global.TEXT:
            out_text = message + "\r\n"
        out_text_bin = out_text.encode('utf-8')
        try:
            # print(">>> socket write: " + str(out_text))
            self.client_socket.send(out_text_bin)
        except (KeyboardInterrupt, SystemExit):
            self.log_warning("keyboard or system interrupt")
            raise
        except Exception as exc:
            self.log_error("Error: excption writeing to socket: " + str(exc))

    def __parse_config(self, config, host_name):
        """ parse parameters from config data """
        socket_host = None
        socket_port = None
        socket_mode = Global.TEXT
        # print(">>> config: " + str(config))
        if Global.CONFIG in config:
            if Global.IO in config[Global.CONFIG]:
                if Global.NETWORK in config[Global.CONFIG][Global.IO]:
                    network_config = config[Global.CONFIG][Global.IO][
                        Global.NETWORK]
                    print(">>> net conf:" + str(network_config))
                    if Global.SERVER in network_config:
                        if Global.HOST in network_config[Global.SERVER]:
                            host = network_config[Global.SERVER][Global.HOST]
                            socket_host = \
                                    host.replace("**" + Global.HOST + "**", host_name)
                        if Global.PORT in network_config[Global.SERVER]:
                            socket_port = \
                                network_config[Global.SERVER][Global.PORT]
                        if Global.MODE in network_config[Global.SERVER]:
                            mode = network_config[Global.SERVER][Global.MODE]
                            if mode != Global.TEXT:
                                socket_mode = Global.CHAR
                            else:
                                socket_mode = Global.TEXT
        return (socket_host, socket_port, socket_mode)
