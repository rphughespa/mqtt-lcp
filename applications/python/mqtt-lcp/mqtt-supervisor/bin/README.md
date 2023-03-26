#### MQTT-LCP Application

# MQTT-SUPERVISOR

This application should be run on any computer running other MQTT-LCP applications.

It performs serveral simple tasks:

* **PING**  Periodically the applcation publishes a PING message.  Other applications can monitor this message
to determine that this computer is up and running.

    The PING message from this application can contain
several measurments of the computer health: memory usage, cpu usage, cpu temperature (an important item with Rapsberry PIs). To provide this information the LANDSCAPE-SYSINFO command must be installed.

* **SHUTDOWN** The application subscribes to SHUTDOWN and REBOOT MQTT messages.  If either message is received, this
appliaction will wait a few seconds and then either SHUTDOWN or REBOOT the computer.

    This remote initiation of a SHUTDOWN insures a clean shutdown of the computers.  This is very helpful with computers booting from sdcards to prevent problems.

[Please see the WIKI for more information](https://github.com/rphughespa/mqtt-lcp/wiki)
