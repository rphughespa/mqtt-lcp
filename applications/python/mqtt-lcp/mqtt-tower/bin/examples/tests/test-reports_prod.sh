#test.sh


echo "test reports"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HOSTNAME'-registry", "port-id":"reports", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report": "panels"}}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HOSTNAME'-registry", "port-id":"reports", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"roster"}}}}'

sleep 3

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HOSTNAME'-registry", "port-id":"reports", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"inventory"}}}}'

sleep 3



mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HOSTNAME'-registry", "port-id":"reports", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"states"}}}}'

sleep 3


mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/harris-01/siding-south-east' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "harris-01", "port-id" : "siding-south-east",  "state": {"reported": "on"}}}'


sleep 3


mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HOSTNAME'-registry", "port-id":"reports", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"states"}}}}'
