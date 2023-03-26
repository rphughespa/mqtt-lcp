#### MQTT-LCP Application

# MQTT-TOWER

MQTT-TOWER provides track side functions for other aplications. It collects information from applications and disseminates it to the layout.

* **INVENTORY** : MQTT-TOWER maintains a dynamic inventory of all the track side devices.

  It builds this list by querying other applications on the layout.

  The MQTT-TOWER subscribes to all "PING" messages published by applications on the layout.  When a new application is seen, or if an application has rejoined the layout, the MQTT-TOWER will publish an INVENTORY request message to the application.

  When an application receives an INVENTORY request it responds with a list of the trackside devices it controls. The MQTT-TOWER application adds this data into a consolidated INVENTORY.
adds

  This process is repeated for all applicaions.

  Within a few seconds of power up, The MQTT-TOWER's inventory contains information for all trackside devices.

  Applications, like throttles, need to know what trackside devices exist on the layout.  They send the MQTT-TOWER a request to report its inventory either in full or by category (SWICHES, SIGNALS, etc).

* **DASHBOARD** The application stores a summary of the pING messages it receives. Periodically, the application publish out a data BROARDCAST message list all application on the layout and whether thay have PING'd recently.

* **FASTCLOCK** : The application periodically publishes a FASTCLOCK message that contains both the current time and also the "fast time".



[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
