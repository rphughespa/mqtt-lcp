#test.sh

echo "test north-east"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/switch/harris-1/siding-north-east/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-north-east", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 4

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/trains/switch/harris-1/siding-north-east/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-north-east", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 4

echo "test north-west"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/switch/harris-1/siding-north-west/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-north-west", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 4

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/trains/switch/harris-1/siding-north-west/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-north-west", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 4

echo "test south-east"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/switch/harris-1/siding-south-east/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-south-east", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 4

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/trains/switch/harris-1/siding-south-east/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-south-east", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 4

echo "test south-west"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/switch/harris-1/siding-south-west/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-south-west", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 4

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/trains/switch/harris-1/siding-south-west/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "siding-south-west", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "close"}}}'

echo "test report"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/sensor/harris-1/siding-south-west/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "track-5", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "report"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/sensor/harris-1/siding-north-east/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "rotary-1", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "report"}}}'

sleep 3

test "test inventory"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/harris-1/inventory/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": {"report":"inventory"}}}}'

sleep 3

echo "test backup"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/harris-1/req' \
 -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "rotary-1", "res-topic": "dt/trains/backup", "state": {"desired": "backup"}}}'


sleep 6

echo "test shutdown"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/harris-1/req' \
 -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "rotary-1", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "shutdown"}}}'
