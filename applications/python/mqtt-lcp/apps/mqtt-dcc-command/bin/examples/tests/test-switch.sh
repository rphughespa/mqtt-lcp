#test.sh

echo "power off"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc_command/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "power", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "off"}}}'

sleep 3

echo "power on"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc_command/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "power", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "on"}}}'

sleep 3

echo "power report"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc_command/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "power", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "report"}}}'

sleep 3

echo "test inventory report request"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-dcc_command/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": {"report" : "inventory"}}}}'

sleep 3

echo "test throw switch east"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc_command/siding-east/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-north-east", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 3

echo "test close switch east"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc_command/siding-east/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-north-east", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 3

echo "test throw unknown switch east"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc_command/siding-east/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-unknown", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 3

echo "test inventory report request"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-dcc_command/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": {"report" : "inventory"}}}}'

sleep 3

echo "power off"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc_command/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "power", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "off"}}}'

sleep 6

echo "test shutdown"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-dcc_command/req' \
 -m '{"node": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "shutdown"}}}'

