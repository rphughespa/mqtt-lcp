#### MQTT-LCP Applications

# MQTT-I2C

These micropython applications provid an MQTT-LCP interface for I2C based devices.

Some of application translat SWITCH and SIGNAL MQTT requests and manipulates the attached I2C device accordingly.

Other applications read from I2C devices and transmit SENSOR messages.

These application are designed to run on microcontrollers.  They were primarily designed and tested on a Raspberry RP2040 Pico W board.  They were also tested on an ESP32 board, the Adafruit QT Py ESP32 Pico.

Each applicarion only supports a specific type of I2C device:

* **MQTT-I2C-RFID** : Supports reading RFID tag via an I2C bus connected RFID reader.

* **MQTT-I2c-SERVO** Supports a servo control board.

* **MQTT-I2C-PORT-EXPANDER** : Supports two different I2C connected port expoanders for controlling signals, switches, sensors.

    * **MCP23017 Port Expander Board**
    * **12v Relay Board** controlled vai a I2C connected PCA9685 (Iowa Scaled Enginering interface board)

## I2C Bus Devices

An I2C bus can contain, in theory, 127 different devices.  Each device on the bus must have its own unique I2C address.

The possible addresses for any given board varies widely.  Many boards support 8 address choices, other support 16 different addresses, a few only one ot two choices.

For exampole, a server board driven by the PCA9685 chip may offer 16 different address choices.  The means you could, in theory, operate 16 servo boards connected to the same I2C bus.  This would translate into one computer controlling  256 servos.

In reality there are two major factors that limit how many devices can be usefully operated over an I2C bus.

The first is electrical.  In many situations, the length of the physical I2C wiring should not exceed about 12 inches

The second limit is on what computing device controls the I2C bus.  On a microcontroller, having one or two device on the bus is useful.  On a larger computer, like a Raspberry PI, many more devices can be controlled.




[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
