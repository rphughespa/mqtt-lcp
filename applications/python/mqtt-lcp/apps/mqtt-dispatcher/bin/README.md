#### MQTT-LCP Application

# MQTT-PI-DISPATCHER

This application presents an GUI interface to control trackside devices.

Several functions are provided via different screens:

* **Panels** Display the layout graphically as a set of panels.  Each panel can be configure to show different sections of the layout.  Track, turnout and signals can be displayed.  The turnouts and signals images can be clicked to request changes to their state.  Track occupancy is reflected via color coded track images.  If location servies are active, the loco id detected can be shown next to its matching track segment.

* **Switches** Displays the available switches on the layout in list form.  A request to change the state of a switch can be requested via clicking its list entry.

* **Routes** Displays the available routes on the layout in list form.  A request to change the state of a route can be requested via clicking its list entry.

* **Signals** Displays the available signals on the layout in list form.  A request to change the state of a signal can be requested via clicking its list entry.

* **Dashboard** Displays the status the all the MQTT-LCP applications.

* **System** Sereral system-wide setting can be managed:

    * **FastclocK** Stop/Start/Reset the system fastclock.

    * **Track Power** Turn track power on/off

    * **Shutdown** Transmit the SHUTDOWN message to all MQTT-LCP applications.  When received, the programs wwill do a clean" shutdown.  In addition, the MQTT-SUPERVISOR application will execute a shutdown the computers on which they are running.


    * **Automatic Signals** Future, not current enabled

    * **Central Traffic Control** Provides the ability to limit which applications can be used to manage switches.

        * **Disabled** All throttle and the MQTT-Dispatcher application can each request changes to the  state of switches

        * **ENABLED** Onlythe MQTT-Dispatcher application can each request changes to the  state of switches.  Throttles cannot.

The MQTT-DISPATCHER application is designed to operate on the PI 7" touch screen but should run well on other screens that is at least 800x400 resolutions.

[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
