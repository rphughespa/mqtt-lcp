
#### MQTT-LCP Applications

# MQTT-I2C-PORT-EXPANDER

This micropython application connects via I2C to two different types of port expander devices:

## MCP23017

The MCP23017 board has 16 IO pins which be set for either input or output.  These pins can operate at either 3.3v of 5v depending on the voltage of the input I2C wiring.  When pluged into either an RP2040 or an ESP32 board, 3.3v is the default voltage.  To use the device at 5v, you need to pass the 3.4v I2C signal thru an I2C bi-direction logic level converter.

Please note that is a limit to how much current can pass thru this device.  You can connect 16 LEDs to the device, but they can't all be ON at the same time as the current draw may exceed the limits of the device.

## 12v Relay Board

The 12v Relay Board has no similar limits of the voltage or current that pass through it pins.  Each "pin" is actually a SPDT relay.

A convient way to interface the relay board to I2C is via a  PCA9685 chip (Iowa Scaled Engineering I2C-RELAY16-QWIIC interface board).

The MCP23017 is an IO device where the 12v Relay board is output only.

The output operation supported on both boards are:

* **Signals**

    * **single**: one pin on/off or blink

    * **color**: 'three pins for a color' signal heads

    * **position**: four pins for a 'positional'signal heads

    * **rgb**: three pins to drive an rpg led used as a searchlight signal/

    * **toggle**: two pins, "on" turn on one pin, turn off the other. "off" reverses the lights.

    * **flasher**: Two pins are alternate on/off at a set blink rate.

    * **pulse**: The "single" or "toggle" types can be engerized for a short period then quickly deengerized. This is intended to simulate a push button press/release



* **Switches**:

    * **single**: Simple on/off (throw/close)

    * **toggle**: Two pins. When one pin is engerized on on, the other pin engerized on off

    * **pulse**: Either of the above switch types default to steady state, simulating a togole switch.  Each of the above can also be configured to PULSE, quick ON then OFF. This simulates a puch button.


[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
