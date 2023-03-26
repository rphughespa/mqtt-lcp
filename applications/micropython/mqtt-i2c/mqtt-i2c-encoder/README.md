
#### MQTT-LCP Applications

# MQTT-I2C-ENCODER

This micropython application connects via I2C to a RGB rotary encoder(SparkFun Qwiic Twist)
Rotating the shaft of the device will generate MQTT-LCP sensor MQTT messages. Values from 0-100 are transmitted.

In addition to sending out sensor messages the application will also change the color of the shaft from OFF at zero, to GREEN at 1 thru to RED at 100.


[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
