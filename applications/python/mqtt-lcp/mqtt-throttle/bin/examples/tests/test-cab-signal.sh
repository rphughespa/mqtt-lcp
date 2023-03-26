#! /bin/bash

# test passing cab signals messages to mqtt-pi-throttle
# in mqtt-pi-throttle acquire loco 1234 then change to controls tab
# then run this script and the cab signal display should change

echo "cab signal for 1234: off"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/mqtt-tower' \
 -m '{"signal": {"node-id": "mqtt-tower", "loco-id": 1234, "state": {"reported": "off"}, "version": "1,0", "timestamp": 1647964569059}}'

sleep 3
echo "cab signal for 1234: clear"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/mqtt-tower' \
 -m '{"signal": {"node-id": "mqtt-tower", "loco-id": 1234, "state": {"reported": "clear"}, "version": "1,0", "timestamp": 1647964569059}}'

sleep 3

echo "cab signal for 1234: approach"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/mqtt-tower' \
 -m '{"signal": {"node-id": "mqtt-tower", "loco-id": 1234, "state": {"reported": "approach"}, "version": "1,0", "timestamp": 1647964569059}}'

sleep 3

echo "cab signal for 1234: stop"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/mqtt-tower' \
 -m '{"signal": {"node-id": "mqtt-tower", "loco-id": 1234, "state": {"reported": "stop"}, "version": "1,0", "timestamp": 1647964569059}}'

sleep 3

echo "cab signal for 1234: off"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/mqtt-tower' \
 -m '{"signal": {"node-id": "mqtt-tower", "loco-id": 1234, "state": {"reported": "off"}, "version": "1,0", "timestamp": 1647964569059}}'

sleep 3