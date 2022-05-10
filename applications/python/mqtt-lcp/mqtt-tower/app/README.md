#### MQTT-LCP Application

# MQTT-TOWER

This application provides track side functions for other aplications.


* **Inventory** : the application maintains a dynamic list of all the track side devices.
When applications come on-line, MQTT-TOWER asks the application to report it "inventory" of
of the devices it controls.  The MQTT-TOWER collects this information into a consolidated
list of track side devices on the layout and which computer controls them.  This data is made
available to other computer via the "report" function.

* **FASTCLOCK** : The application periodically publishes a FASTCLOCK message that
  contains both the current time but also the "fast time".

* **Reports** : The tower can be requested to procuce several "report" type messages:
    * **INVENTORY** : A list of all track side devices (switches, signals, sensors) on the layout


[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
