#### MQTT-LCP Application

# MQTT-DCC-COMMAND

MQTT-DCC-COMMAND is the "command station" in the MQTT-LCP system.  This application subscribes to
MQTT messages that are published by the throttles.  The MQTT messages are translated into actions that passed to the hardware comand stations to control the locos.

This application is coded to communicate with two differnt hardware "back-ends" that actually put the DCC messages on the track:

* **DCC++** - MQTT-DCC-COMMAND can connect directly to an Arduiono running the DCC++ (or DCC++Ex) via
        a serial USB connection.

        Note: Tested with DCC-EX V-4.1.2. The preamble size was changed from 16 to 64 to better accomodate Railcom.

* **WITHROTTLE** - MQTT-DCC-COMMAND can connect to a Withrottle server to drive locos via that server.

        Note: Tested with Digitrax LNW1 and JMRI Withrottle servers.

MQTT-DCC-COMMAND also distributes the ROSTER to the throttles. Optionally, this aplication will peridoically
connect to a JMRI REST server and download the ROSTER maintained in DecoderPro and merge it into the MQTT-LCP ROSTER.

[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
