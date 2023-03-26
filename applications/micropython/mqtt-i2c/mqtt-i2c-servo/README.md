
#### MQTT-LCP Applications

# MQTT-I2C-SERVO

This micropython application connects via I2C to a servo controller board with a PCA9685 chip (Zio 16 Servo Controller - Qwiic)

Each board support 16 servos.

The application accepts SWITCH messages to throw / close the sevos.

The cofiguration entry for each servo specifies what DEGREE (0-90) that is considerd as "throw", and which DEGREE represents "close".


[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
