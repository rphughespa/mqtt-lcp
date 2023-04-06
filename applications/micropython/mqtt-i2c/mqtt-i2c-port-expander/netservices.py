import machine, network, ntptime, time

from global_constants import Global

global rtc
rtc = None

class NetServices:

    def __init__(self, config):
        self.config = config
        self.mdns = None
        self.ip_address = None
        self.net_connected = False
        self.static_ip = None
        self.ssid = None
        self.password = None
        self.hostname = None

    def set_static_ip(self, ip_config):
        #ip_config is a tupple (ip, mask, gateway, dns)
        self.static_ip = ip_config

    def do_connect(self):
        import network
        print("Net Config: "+str(self.config[Global.CONFIG][Global.IO][Global.NETWORK]))
        wlan = network.WLAN(network.STA_IF)
        print("WLAN Active:",wlan.active(True)) 
        # wlan.active(True)
        wifi_ssid = self.config[Global.CONFIG][Global.IO][Global.NETWORK][Global.WIFI][Global.SSID]
        wifi_password = self.config[Global.CONFIG][Global.IO][Global.NETWORK][Global.WIFI][Global.PASSWORD]
        if not wlan.isconnected():
            print("Connecting to network... "  + str(wifi_ssid))
            wlan.connect(wifi_ssid, wifi_password)
            while not wlan.isconnected():
                print(".", end =" ")
                time.sleep(1)
        print(' ... network config:', wlan.ifconfig())
        (self.ip_address, _mask, _gateway, _dns) = wlan.ifconfig()
        self.net_connected = True


    def start_net_time(self):
        #if needed, overwrite default time server
        ntptime.host = "1.europe.pool.ntp.org"

        try:
          print("Local time before synchronization：%s" %str(time.localtime()))
          #make sure to have internet connection
          ntptime.settime()          
        except:
          print("Error syncing time")
  


    def get_ip_address(self):
        return self.ip_address

    def is_connected(self):
        return self.net_connected

