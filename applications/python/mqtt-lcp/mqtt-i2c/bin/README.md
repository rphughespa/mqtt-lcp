#### MQTT-LCP Application

# MQTT-I2C

The MQTT-I2C application provides an MQTT-LCP interface for I2C based devices. These devices in turn provide trackside functionality

The currently supported I2C devices are:

* **PORT-EXPANDERS**: This micropython application connects via I2C to two different types of port expander devices:

    * **MCP23017** The MCP23017 board has 16 IO pins which be set for either input or output.  These pins can operate at either 3.3v of 5v depending on the voltage of the input I2C wiring.  When pluged into either an RP2040 or an ESP32 board, 3.3v is the default voltage.  To use the device at 5v, you need to pass the 3.4v I2C signal thru an I2C bi-direction logic level converter.

        *  Please note that is a limit to how much current can pass thru this device.  You can connect 16 LEDs to the device, but they can't all be ON at the same time as the current draw may exceed the limits of the device.

    * **12v Relay Board** The 12v Relay Board has no similar limits of the voltage or current that pass through it pins.  Each "pin" is actually a SPDT relay.

        * A convient way to interface the relay board to I2C is via a  PCA9685 chip (Iowa Scaled Engineering I2C-RELAY16-QWIIC interface board).

    The MCP23017 is an IO device where the 12v Relay board is output only.

    * The output operation supported on both boards are:

        * **Signals**
            * **single lamps**: on/off or blink
                * **3 lamps**: 'color' signal heads
            * **4 lamps**: 'positional'signal heads
        * **Switches**:
            * **Single**: Simple on/off (throw/close)
            * **Toggle**: Two pins. When one pin is engerized on on, the other pin engerized on off
            * **Pulse**: Either of the above switch types default to steady state, simulating a togole switch.  Each of the above can also be configured to PULSE, quick ON then OFF. This simulates a puch button.

* **RFID Tag Reader** : This application can connect via I2C to a RFIDF tag reader (SparkFun RFID Qwiic Reader)

    The application publishes a LOCATOR message when an RFID tag is read.

    If the systems ROSTER has RFID tag information for the locos in the ROSTER, the LOCATOR message will include the loco DCC-ID of the loco that matches the RFID tag id read.

* **ROTARY ENCODER** : This application can connect via I2C to a RGB rotary encoder(SparkFun Qwiic Twist)
Rotating the shaft of the device will generate MQTT-LCP sensor MQTT messages. Values from 0-100 are transmitted.

    In addition to sending out sensor messages the application will also change the color of the shaft from OFF at zero, to GREEN at 1 thru to RED at 100.


* **Multiplexor** : 8 port input / output
* **Servo Board** : This application can connect via I2C to a servo controller board with a PCA9685 chip (Zio 16 Servo Controller - Qwiic)

    Each board support 16 servos.

    The application accepts SWITCH messages to throw / close the sevos.

    The cofiguration entry for each servo specifies what DEGREE (0-90) that is considerd as "throw", and which DEGREE represents "close".


## I2C Bus Devices

An I2C bus can contain, in theory, 127 different devices.  Each device on the bus must have its own unique I2C address.

The possible addresses for any given board varies widely.  Many boards support 8 address choices, other support 16 different addresses, a few only one ot two choices.

For exampole, a server board driven by the PCA9685 chip may offer 16 different address choices.  The means you could, in theory, operate 16 servo boards connected to the same I2C bus.  This would translate into one computer controlling  256 servos.

In reality there are two major factors that limit how many devices can be usefully operated over an I2C bus.

The first is electrical.  In many situations, the length of the physical I2C wiring should not exceed about 12 inches

The second limit is on what computing device controls the I2C bus.  On a microcontroller, having one or two device on the bus is useful.  On a larger computer, like a Raspberry PI, many more devices can be controlled.


[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
