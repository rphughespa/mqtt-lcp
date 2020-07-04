#test.sh

echo "test report"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/sensor/mqtt-sensor/track-0/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "track-0", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "report"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/sensor/mqtt-sensor/rotary-1/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "rotary-1", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "report"}}}'

sleep 3

echo "test inventory"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/mqtt-sensor/inventory/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": {"report":"inventory"}}}}'

sleep 3

echo "test backup"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/mqtt-sensor/req' \
 -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "rotary-1", "res-topic": "dt/trains/backup", "state": {"desired": "backup"}}}'


sleep 6

echo "test shutdown"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/mqtt-sensor/req' \
 -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "rotary-1", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "shutdown"}}}'



