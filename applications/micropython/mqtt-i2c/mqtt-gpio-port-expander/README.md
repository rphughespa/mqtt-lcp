
#### MQTT-LCP Applications

# MQTT-GPIO-PORT-EXPANDER

This micropython application uses 16 GPIO pins on the RP2040 PICO W board to control low voltage, low current signals and inpout.:

These GPIO pins operate at 3.3v.  They can be individually configured for simple input or output. The application set them to "active-low".

Groups of consecutive pins can be configured  to operate as a single device.

The output operation supported on both boards are:

* **Signals**

    * **single**: one pin on/off or blink

    * **color**: 'three pins for a color' signal heads

    * **position**: four pins for a 'positional'signal heads

    * **rgb**: three pins to drive an rpg led used as a searchlight signal/

    * **toggle**: two pins, "on" turn on one pin, turn off the other. "off" reverses the lights.

    * **flasher**: Two pins are alternate on/off at a set blink rate.

    * **pulse**: The "single" or "toggle" types can be engerized for a short period then quickly deengerized. This is intended to simulate a push button press/release


[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
