
#test.sh

echo "power off"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc-command/power/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "power", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "off"}}}'

sleep 3

echo "power on"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc-command/power/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "power", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "on"}}}'

sleep 3

echo "power report"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc-command/power/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "power", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "report"}}}'

sleep 3


echo "power off"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc-command/power/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "power", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "off"}}}'

sleep 6

echo "test shutdown"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-dcc-command/req' \
 -m '{"node": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "track", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "shutdown"}}}'

