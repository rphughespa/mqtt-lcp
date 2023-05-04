# netservices.py
"""
 Netservices - helper class for various network related functions

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
import time
import machine
import network
import ntptime


from global_constants import Global

global rtc
rtc = None

class NetServices:
    """ network services """
    def __init__(self, config):
        """ initialize """
        self.config = config
        self.mdns = None
        self.ip_address = None
        self.net_connected = False
        self.static_ip = None
        self.ssid = None
        self.password = None
        self.hostname = None

    def set_static_ip(self, ip_config):
        """ set up a static ip """
        #ip_config is a tupple (ip, mask, gateway, dns)
        self.static_ip = ip_config

    def do_connect(self):
        """ connect to wifi """

        print("Net Config: "+str(self.config[Global.CONFIG][Global.IO][Global.NETWORK]))
        
        wifi_hostname = self.config[Global.CONFIG][Global.IO][Global.NETWORK][Global.WIFI][Global.HOSTNAME]
        #print("Hostname: "+str(wifi_hostname) + " : " + str(network.hostname()))
        #network.hostname(wifi_hostname+".local")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True) 
        wifi_ssid = self.config[Global.CONFIG][Global.IO][Global.NETWORK][Global.WIFI][Global.SSID]
        wifi_password = self.config[Global.CONFIG][Global.IO][Global.NETWORK][Global.WIFI][Global.PASSWORD]
        if not wlan.isconnected():
            print("Connecting to network... "  + str(wifi_ssid) + " : "+str(wifi_hostname))
            wlan.connect(wifi_ssid, wifi_password)
            while not wlan.isconnected():
                print(".", end =" ")
                time.sleep(1)
        print(' ... network config:', wlan.ifconfig())
        (self.ip_address, _mask, _gateway, _dns) = wlan.ifconfig()
        self.net_connected = True


    def start_net_time(self):
        """ start up network time"""
        #if needed, overwrite default time server
        ntptime.host = "1.europe.pool.ntp.org"

        try:
            print("Local time before synchronization：%s" %str(time.localtime()))
            #make sure to have internet connection
            ntptime.settime()
        except:
            print("Error syncing time")


    def get_ip_address(self):
        """ get ip address"""
        return self.ip_address

    def is_connected(self):
        """ is device connected to network """
        return self.net_connected
