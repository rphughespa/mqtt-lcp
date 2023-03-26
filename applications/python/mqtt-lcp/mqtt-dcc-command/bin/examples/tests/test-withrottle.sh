#!/bin/bash
#test.sh


echo "power on"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc-command/power/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "power", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "on"}}}'

sleep 6


echo "connect A"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-a/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle", "throttle-id": "12abcd",  "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "connect"}}}'

sleep 4


echo "acquite loco for cab-1"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle",  "throttle-id": "12abcd",  "cab-id": "cab-a", "loco-id": 5887, "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "acquire"}}}'


sleep 4

echo "set direction for cab-1"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle",  "throttle-id": "12abcd",  "cab-id": "cab-a", "loco-id": 5887, "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": {"direction":"forward"}}}}'

sleep 4

echo "move loco for cab-1"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle",  "throttle-id": "12abcd",  "cab-id": "cab-a", "loco-id": 5887, "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": {"speed":10}}}}'

#sleep 4

echo "stop loco for cab-1"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle",  "throttle-id": "12abcd",  "cab-id": "cab-a", "loco-id": 5887, "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": {"speed":0}}}}'

sleep 4

echo "set direction for cab-1"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle",  "throttle-id": "12abcd",  "cab-id": "cab-a", "loco-id": 5887, "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": {"direction":"reverse"}}}}'

sleep 4

echo "move loco for cab-1"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle",  "throttle-id": "12abcd",  "cab-id": "cab-a", "loco-id": 5887, "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": {"speed":10}}}}'

#sleep 4

echo "stop loco for cab-1"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle",  "throttle-id": "12abcd",  "cab-id": "cab-a", "loco-id": 5887, "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": {"speed":0}}}}'

sleep 4


echo "bell on loco for cab-1"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle",  "throttle-id": "12abcd",  "cab-id": "cab-a", "loco-id": 5887, "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": {"function":1, "state":"on"}}}}'

sleep 4

echo "bell of loco for cab-1"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle",  "throttle-id": "12abcd",  "cab-id": "cab-a", "loco-id": 5887, "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": {"function":1, "state":"off"}}}}'

sleep 4

echo "release loco for cab-1"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-b/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle", "throttle-id": "12abcd",   "cab-id": "cab-a", "loco-id": 5887, "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "release"}}}'

#sleep 4

echo "disconnect A"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/'$HOSTNAME'-dcc-command/desktop-throttle-a/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle", "throttle-id": "12abcd",   "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "disconnect"}}}'


sleep 6

echo "power off"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc-command/power/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1","throttle-id": "56abcd",   "port-id": "power", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "off"}}}'

sleep 6

echo "test shutdown"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-dcc-command/req' \
 -m '{"node": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "desktop-throttle","throttle-id": "12abcd",   "port-id": "track", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "shutdown"}}}'

