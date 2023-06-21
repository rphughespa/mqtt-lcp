#test.sh

export HNAME=mqtt-tower
echo "test fastclock"

echo "fastclock run"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/fastclock/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-tower", "port-id": "fastclock", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "run"}}}'

sleep 10
echo "fastclock pause"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/fastclock/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-tower", "port-id": "fastclock", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "pause"}}}'

sleep 10
echo "fastclock reset"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/fastclock/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-tower", "port-id": "fastclock", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "reset"}}}'

sleep 10

echo "fastclock error"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/fastclock/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-tower", "port-id": "fastclock", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "error???"}}}'

sleep 10

echo "fastclock run"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/fastclock/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-tower", "port-id": "fastclock", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "run"}}}'
