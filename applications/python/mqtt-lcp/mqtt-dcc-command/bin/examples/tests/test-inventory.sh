mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/mqtt-broker-tower/report/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HOSTNAME'-tower", "port-id":"reports", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"inventory"}}}}'
