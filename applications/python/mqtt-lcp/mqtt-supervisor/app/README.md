#### MQTT-LCP Application

# MQTT-SUPERVISOR

This application is intended to run on any computer running other MQTT-LCP applications.

It performs serveral simple tasks:

** Periodically publishes a PING message.  Other application can monitor this message
to determine that this computer is up and running.  The PING message from this application contains
several measurments of the computer health: memory usage, cpu usage, cpu temperature (an
important item with Rapsberry PIs).

** The applicarion subscribes to SHUTDOWN and REBOOT MQTT messages.  If either message is received, this
appliaction will wait a few seconds and then either SHUTDOWN or REBOOT the computer.

This remote initiation of a SHUTDOWN insures clean shutdown of the computers.  This is very helpful with
computers booting from sdcards

[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
