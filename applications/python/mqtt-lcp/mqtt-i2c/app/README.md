#### MQTT-LCP Application

# MQTT-I2C

This application provides an MQTT interface for I2C based devices.  The application
translates SWITCH and SIGNAL MQTT requests and manipulates the attached I2C device accordingly.

In addition to changing I2C devices, the application can also read I2C devices and transmit SENSOR
messages:

The currently supported I2C devices are:

* **MCP23017 Port Expander** : 16 port 3v-5v input/output (led signals, simple on/off sensors, etc)
* **I2C RELAY BOARD** : output, uses and I2C 16 port relay interface board (solenoid, slow motion switches, etc)
* **RFID Tag Reader** : input
* **ROTARY ENCODER** : input
* **Multiplexor** : 8 port input / output
* **Servo Board** : 16 port servo controller for servo switches

[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
