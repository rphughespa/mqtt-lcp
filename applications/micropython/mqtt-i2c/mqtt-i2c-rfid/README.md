
#### MQTT-LCP Applications

# MQTT-I2C-RFID

This micropython application connects via I2C to a RFIDF tag reader (SparkFun RFID Qwiic Reader)

The application publishes a LOCATOR message when an RFID tag is read.

If the systems ROSTER has RFID tag information for the locos in the ROSTER, the LOCATOR message will include the loco DCC-ID of the loco that matches the RFID tag id read.

[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
