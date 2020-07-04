#test.sh

echo "power off"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/track/mqtt-dcc-bridge/req' \
 -m '{"track": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "track", "res-topic": "cmd/trains/node/throttle1/res", "state": {"desired": {"power" : "off"}}}}'

sleep 3

echo "power on"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/track/mqtt-dcc-bridge/req' \
 -m '{"track": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "track", "res-topic": "cmd/trains/node/throttle1/res", "state": {"desired": {"power":"on"}}}}'

sleep 3

echo "power report"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/track/mqtt-dcc-bridge/req' \
 -m '{"track": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "track", "res-topic": "cmd/trains/node/throttle1/res", "state": {"desired": {"report":"power"}}}}'

sleep 3

echo "connect"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/throttle/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "throttle", "res-topic": "cmd/trains/node/throttle1/res", "state": {"desired": "connect"}}}'

sleep 3

meta1='"metadata":{"dcc-id":"2096", "name":"prr-gg1-green-9678",'
meta2=' "consist":[{"dcc-id":"2096", "name":"prr-gg1-green-9678","direction":"forward", "functions":"true"},'
meta3='{"dcc-id":"603", "name":"prr-k4s-2865", "direction":"forward", "functions":"true"}]}'
meta=$meta1$meta2$meta3
echo $meta

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2=' "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle1/res",'
body3=' "state": {"desired": "acquire"},'
body4=$meta
body5='}}'
body=$body1$body2$body3$body4$body5
echo $body

echo "acquire"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/2096/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle1/res", "state": {"desired": "acquire"}}}'

sleep 3


echo "function on"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/2096/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle-1/res", "state": {"desired": {"function":0, "action":"on"}}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/2096/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle-1/res", "state": {"desired": {"function":1, "action":"on"}}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/2096/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle-1/res", "state": {"desired": {"function":5, "action":"on"}}}}'

sleep 6

echo "move loco forward"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/2096/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle-1/res", "state": {"desired": {"speed":12, "direction":"forward"}}}}'


sleep 3

echo "stop loco"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/2096/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle-1/res", "state": {"desired": {"speed":0, "direction":"forward"}}}}'


sleep 3

echo "move loco reverse"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/2096/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle-1/res", "state": {"desired": {"speed":12, "direction":"reverse"}}}}'

sleep 3





echo "function off"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/2096/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle-1/res", "state": {"desired": {"function":5, "action":"off"}}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/2096/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle-1/res", "state": {"desired": {"function":1, "action":"off"}}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/2096/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle-1/res", "state": {"desired": {"function":0, "action":"off"}}}}'

sleep 3


echo "test throw switch east"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/switch/mqtt-dcc-bridge/siding-east/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-east", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 8

echo "test close switch east"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/trains/switch/mqtt-dcc-bridge/siding-east/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-east", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 8

echo "release"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/2096/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "2096", "res-topic": "cmd/trains/node/throttle1/res", "state": {"desired": "release"}}}'

sleep 3

echo "disconnect"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/cab/mqtt-dcc-bridge/throttle/req' \
 -m '{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "throttle", "res-topic": "cmd/trains/node/throttle1/res", "state": {"desired": "disconnect"}}}'

sleep 6

echo "power off"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/track/mqtt-dcc-bridge/req' \
 -m '{"track": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "track", "res-topic": "cmd/trains/node/throttle1/res", "state": {"desired": {"power":"off"}}}}'

sleep 6

echo "test shutdown"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/mqtt-dcc-bridge/req' \
 -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "track", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "shutdown"}}}'

