#test.sh

echo "test reports"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/mqtt-registry/report/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "report"},"metadata":{"type":"roster"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/mqtt-registry/report/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "report"},"metadata":{"type":"switches"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/mqtt-registry/report/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "report"},"metadata":{"type":"warrants"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/mqtt-registry/report/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "report"},"metadata":{"type":"signals"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/mqtt-registry/report/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "report"},"metadata":{"type":"layout"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/mqtt-registry/report/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "report"},"metadata":{"type":"dashboard"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/mqtt-registry/report/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "report"},"metadata":{"type":"state"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/report/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "report"},"metadata":{"type":"dashboard"}}}'

sleep 6

echo "test fastclock"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/mqtt-registry/fastclock/req' \
 -m '{"fastclock": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "run"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/mqtt-registry/fastclock/req' \
 -m '{"fastclock": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "pause"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/mqtt-registry/fastclock/req' \
 -m '{"fastclock": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "reset"}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/registry/mqtt-registry/fastclock/req' \
 -m '{"fastclock": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "res-topic": "cmd/trains/nodes/speed-test-requestor/res", "state": {"desired": "run"}}}'

sleep 3

echo  "test backup"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/mqtt-registry/req' \
 -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "rotary-1", "res-topic": "dt/trains/backup", "state": {"desired": "backup"}}}'


sleep 6

echo "test shutdown"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/trains/node/mqtt-registry/req' \
 -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "res-topic": "cmd/trains/throttle/throttle1/res", "state": {"desired": "shutdown"}}}'

