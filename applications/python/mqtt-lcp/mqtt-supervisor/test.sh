#test.sh

echo "test inventory"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/mqtt-supervisor/inventory/req' \
 -m '{"register": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "report"}, "metadata": {"type": "inventory"}}}'

sleep 3

test "backup"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/mqtt-supevisor/req' \
 -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "rotary-1", "res-topic": "dt/trains/backup", "state": {"desired": "backup"}}}'

sleep 3

# either run reboot or shutdown, they are mutally exclusive

# echo "test reboot"
#mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
# -t 'cmd/trains/node/mqtt-supervisor/req' \
# -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "rotary-1", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "reboot"}}}'

echo "test shutdown"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/mqtt-supervisor/req' \
 -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "rotary-1", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "shutdown"}}}'
