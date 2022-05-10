#!/usr/bin/python3
# socker_server_process.py
"""

        socker_server_process - process class for a socker server
            open a socket port and waits for incomming connections


The MIT License (MIT)

Copyright 2021 richard p hughes

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
import socket
import select

from zeroconf import IPVersion, ServiceInfo, Zeroconf

from utils.global_constants import Global

from processes.base_process import BaseProcess

BUFFER_LENGTH = 4096


class SocketServerProcess(BaseProcess):
    """ Allow incomming socket connections """
    def __init__(self, events=None, queues=None):
        super().__init__(name="socket",
                         events=events,
                         in_queue=queues[Global.DEVICE],
                         app_queue=queues[Global.APPLICATION],
                         log_queue=queues[Global.LOGGER])
        self.delay = 0
        self.buffer = ""
        self.socket_mode = "text"
        self.socket_ip_address = None
        self.socket_host = None
        self.socket_port_id = None
        self.server_socket = None
        self.sockets_list = None
        self.service_name = None
        self.service_description = None
        self.service_info = None
        self.service_zeroconf = None

        # print(">>> socket process starting !!!!!!!!")

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def initialize_process(self):
        """ iitialize this process """
        super().initialize_process()
        self.log_info("Init socket server")
        if Global.CONFIG in self.config:
            if Global.IO in self.config[Global.CONFIG]:
                if Global.NETWORK in self.config[Global.CONFIG][Global.IO]:
                    network_config = self.config[Global.CONFIG][Global.IO][
                        Global.NETWORK]
                    if Global.SELF in network_config:
                        if Global.HOST in network_config[Global.SELF]:
                            self.socket_host = \
                            host = network_config[Global.SELF][Global.HOST]
                            self.socket_host = \
                                    host.replace("**" + Global.HOST + "**", self.host_name)
                        if Global.PORT in network_config[Global.SELF]:
                            self.socket_port_id = \
                                network_config[Global.SELF][Global.PORT]
                        if Global.SERVICE in network_config[Global.SELF]:
                            self.service_name = \
                                network_config[Global.SELF][Global.SERVICE]
                        if Global.DESCRIPTION in network_config[Global.SELF]:
                            self.service_description = \
                                network_config[Global.SELF][Global.DESCRIPTION]

        if self.socket_host is None:
            self.log_critical("Error: Configuration error: "+\
                    "Missing io/network/self/host")
        else:
            try:
                #print(">>> host: " +str(self.socket_host))
                self.socket_ip_address = socket.gethostbyname(self.socket_host)
                #print(">>> ip: " + str(self.socket_ip_address))
            except Exception as exc:
                self.log_critical("Error: Configuration error: "+\
                    "Invalid io/network/self/host: {"+str(self.socket_host)+"}\n ... "+str(exc))

        if self.socket_port_id is None:
            self.log_critical("Error: Configuration error: "+\
                    "Missing io/network/self/port")

        if self.socket_ip_address is None:
            self.log_critical(
                "Error: Configuration error: IP address not defined")
        elif self.socket_port_id is None:
            self.log_critical(
                "Error: Configuration error: port number not defined")
        else:
            self.log_info("Open socket: " + str(self.socket_ip_address) +
                          " ... " + str(self.socket_port_id))
            self.server_socket = socket.socket(socket.AF_INET,
                                               socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET,
                                          socket.SO_REUSEADDR, 1)
            self.server_socket.setsockopt(socket.SOL_SOCKET,
                                          socket.SO_REUSEPORT, 1)
            self.server_socket.bind(
                (self.socket_ip_address, self.socket_port_id))
            # This makes server listen to new connections
            self.server_socket.listen()
            # List of sockets for select.select()
            self.sockets_list = [self.server_socket]
            if self.service_name is not None:
                self.__register_service()

    def shutdown_process(self):
        """ process shutdown is in progress """
        if self.server_socket is not None:
            #print(">>> close server socket ")
            self.server_socket.close()
            self.server_socket = None
            if self.service_zeroconf is not None:
                self.__unregister_service()
        super().shutdown_process()

    def process_message(self, new_message=None):
        """ process messages from async message queue """
        (operation, socket_message) = new_message
        self.log_info("New Message " + str(operation) + " ... " +
                      str(socket_message))

    def process_other(self):
        """ perform other than message queue tasks"""
        if self.server_socket is not None:
            self.__check_for_socket_connections()


#
# private functions
#

    def __check_for_socket_connections(self):
        """ chec for new connection, if new connections found, accept them """

        read_sockets, _, exception_sockets = \
                select.select(self.sockets_list, [], self.sockets_list, 0.1)
        # Iterate over notified sockets

        for notified_socket in read_sockets:
            # If notified socket is a server socket - new connection, accept it
            if notified_socket == self.server_socket:
                # Accept new connection
                # That gives us new socket - client socket,
                # connected to this given client only, it's unique for that client
                # The other returned object is ip/port set
                client_socket, client_address = self.server_socket.accept()
                self.__accept_client_connection(client_socket, client_address)
            # Else existing socket is sending a message
            else:
                # Receive message
                message_bin = self.__receive_message(notified_socket)
                # If False, client disconnected, cleanup
                if message_bin is False:
                    self.__close_client_connection(notified_socket)
                    continue

                # Get user by notified socket, so we will know who sent the message
                message = message_bin.decode("utf8")
                message_source = notified_socket
                message_hex = binascii.hexlify(message_bin)
                new_message = {"source": message_source, "text": message}
                self.log_info("<<< Client <<< [" \
                     + message + "] ...["+ str(message_hex) + "]")
                self.log_info(" ... " + str(new_message))
                # self.socket_in_queue.put(new_message)
                # It's not really necessary to have this,
                # but will handle some socket exceptions just in case
        for notified_socket in exception_sockets:
            self.__close_client_connection(notified_socket)

    def __accept_client_connection(self, client_socket, client_address):
        """ accept a new incomming client connection"""
        self.log_info("New Socket Client Connection: " + str(client_address))
        msg_body = {
            Global.SOCKET: client_socket,
            Global.ADDRESS: client_address
        }
        self.send_to_application((Global.DEVICE_CONNECT, msg_body))

    def __receive_message(self, client_socket):
        """ Handle received messages"""
        try:
            return_bytes = ""
            return_bytes = client_socket.recv(BUFFER_LENGTH)
            if not return_bytes:
                return_bytes = False
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

    def __close_client_connection(self, client_socket):
        """ Close a client connection"""
        #if self.client_thread is not None:
        #    self.client_thread.shutdown()
        #    del self.client_thread
        self.log_info('Closed connection from: ' + str(client_socket))
        self.sockets_list.remove(client_socket)

    def __register_service(self):
        "register a service name for this socker server"
        desc = {
            'path': '/~paulsm/'
        }  # no idea what this does, it was in the example
        print("Registration of a service:  ")
        print(" ... {" + str(self.service_name) + "}")
        print(" ... {" + str(self.service_description) + "}")
        print(" ... {" + str(self.socket_host) + "}")
        print(" ... {" + str(self.socket_ip_address) + "}")
        print(" ... {" + str(self.socket_port_id) + "}")
        self.service_zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        self.service_info = ServiceInfo(
            self.service_name,
            self.service_description + "." + self.service_name,
            addresses=[socket.inet_aton(str(self.socket_ip_address))],
            port=self.socket_port_id,
            properties=desc,
            server=self.socket_host + ".",
        )
        self.service_zeroconf.register_service(self.service_info)

    def __unregister_service(self):
        print("Unregistering...")
        self.service_zeroconf.unregister_service(self.service_info)
        self.service_zeroconf.close()
