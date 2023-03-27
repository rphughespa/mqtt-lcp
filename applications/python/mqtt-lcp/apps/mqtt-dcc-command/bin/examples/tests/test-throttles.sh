#test.sh


echo "power on"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/track/mqtt-dcc-command/req' \
 -m '{"track": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle", "port-id": "track", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": {"power":"on"}}}}'

sleep 3


echo "connect A"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dcc-command/desktop-throttle-a/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle", "throttle-id": "ab23cd",  "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "connect"}}}'

sleep 3

echo "connect B"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "handheld-throttle",  "throttle-id": "45abcd", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "connect"}}}'

sleep 3

echo "disconnect A"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dcc-command/desktop-throttle-a/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle",  "throttle-id": "ab23cd", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "disconnect"}}}'

sleep 3

echo "disconnect B"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "handheld-throttle",  "throttle-id": "45abcd", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "disconnect"}}}'

sleep 6

echo "power off"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/track/mqtt-dcc-command/req' \
 -m '{"track": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle", "throttle-id": "ab23cd", "port-id": "track", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": {"power":"off"}}}}'

sleep 6

echo "test shutdown"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/node/mqtt-dcc-command/req' \
 -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle", "throttle-id": "ab23cd", "port-id": "track", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "shutdown"}}}'

