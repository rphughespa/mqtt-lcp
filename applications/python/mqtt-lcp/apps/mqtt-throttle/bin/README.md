#### MQTT-LCP Application

# MQTT-PI-THROTTLE

This application presents an GUI interface to control locos.

Each instance of the program presents two independant CABS which allows for the operation of two locos(or consists).

Multiple instances of the program can be run
simultaneously on one computer or across multiple computers to control more locos.

Functionality is provided via different screens:

* **CAB** This screen controls the actual locos. There are two CAB screens, A or B.  This allows for two locos(or consists) to be controlled

    * **THROTTLE** This screen provides the basic loco functionality:

        * **SPEED** The speed of a loco can be changed via a slider ot via two arrow buttons.  The speed reported back from the MQTT-DCC-COMMAND is displayed in a speedometer.

        * **DIRECTION** The loco direction can be set to move forward, reverse or stopped.

        * **STATUS** Two boxes display the loco dcc id and its image, if available, and it reported block location, if available.

        * **CAB SIGNAL** If available, the current cab signal for the loco is displayed as a graphic, either three color or positional

        * **Bell / HORN** The BELL function and the HORN function of the loco can be activated.
    * **FUNCTIONS** The functions of the loco can be trun ed on/off.
    * **LOCOS** This screen is for the maintainance of the current loco used in this CAB

        * **ACQUIRED** - Displays the loco currently acquired by this cab.  The locos can be released from this screen.

        * **ROSTER** - This screen allows locos to be acquired from the list of locos in the ROSTER.

        * **KEYPAD** Acuire a loco by entering it dcc id.

* **TOWER** - Aloows for control of tracksode devices.

    * **Switches** Displays the available switches on the layout in list form.  A request to change the state of a switch can be requested via clicking its list entry.

    * **Routes** Displays the available soutes on the layout in list form.  A request to change the state of a route can be requested via clicking its list entry.

    * **System** Several system-wide setting can be managed:

        * **Track Power** Turn track power on/off

        * **Shutdown** Transmit the SHUTDOWN message to all MQTT-LCP applications.  When received, the programs wwill do a clean" shutdown.  In addition, the MQTT-SUPERVISOR application will execute a shutdown the computers on which they are running.

The MQTT-THROTTLE application is designed to operate on the PI 7" touch screen but should run well on other screens that is at least 800x400 resolutions.

[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
