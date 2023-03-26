#### MQTT-LCP Application

# MQTT-TURNTABLE

MQTT-TURNTABLE provides a method for controlling a turntable via MQTT messaging.

The turntable is logically considered to be a set of switches. One for each track the turntable is to be moved to.  However, instead of requesting the normal THROW or CLOSE, the switch message for a turntable requests HEAD or TAIL indicating the end of the turntable to be moved to the desired track.

This implementation is designed to be used with a Walther brand turntable controlled via a USB interface.


[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
