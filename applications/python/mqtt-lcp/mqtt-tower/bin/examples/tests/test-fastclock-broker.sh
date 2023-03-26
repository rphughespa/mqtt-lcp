#test.sh


echo "test fastclock"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/mqtt-registry/fastclock/req' \
 -m '{"fastclock": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"fastclock":"run"}}}}'

sleep 10

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/mqtt-registry/fastclock/req' \
 -m '{"fastclock": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"fastclock":"pause"}}}}'

sleep 10

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/mqtt-registry/fastclock/req' \
 -m '{"fastclock": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"fastclock":"reset"}}}}'

sleep 10

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/mqtt-registry/fastclock/req' \
 -m '{"fastclock": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"fastclock":"error???"}}}}'

sleep 10

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/mqtt-registry/fastclock/req' \
 -m '{"fastclock": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"fastclock":"run"}}}}'
