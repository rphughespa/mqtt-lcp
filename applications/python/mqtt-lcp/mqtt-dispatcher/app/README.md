#### MQTT-LCP Application

# MQTT-DISPATCHER

MQTT-DISPATCHER is the "command station" in the MQTT-LCP system.  This application subscribes to
MQTT messages that are published by the throttles.  THe MQTT messages are translated into actions
that contorl the locos.

This application is coded to use two diffeent "back-ends" that actually put the DCC messages on the track:

    DCC++ - MQTT-DISPATCHER can connect to an Arduiono running the DCC++ (or DCC++Ex) via
        a serial USB connection.

    Withrottle - MQTT-DISPATCHER can connect to a Withrottle server to drive locos via that server.
        Tested with Digitrax LNW1 and JMRI Withrottle servers.

MQTT-DISPATCHER also distributes the roster to the throttles. Optionally, the aplication will peridoically
connect to a JMRI REST server and download the roster maintained in DecoderPro.

[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
