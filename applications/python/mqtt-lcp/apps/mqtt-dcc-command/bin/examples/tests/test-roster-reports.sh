# export HNAME=$HOSTNAME
export HNAME=mqtt-dcc-command
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/roster/'$HNAME'/req' \
 -m '{"roster": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'-dcc-command", "port-id":"roster", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "report"}}}'

sleep 3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/roster/'$HNAME'-dcc-command/req' \
 -m '{"roster": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'-dcc-command", "port-id":"rfid", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "report"}}}'

sleep 3
