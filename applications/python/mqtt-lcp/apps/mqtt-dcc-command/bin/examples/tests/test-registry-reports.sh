# export HNAME=$HOSTNAME
export HNAME=mqtt-dev-tower
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"sensors"}}}}'

sleep 3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"switches"}}}}'

sleep 3
