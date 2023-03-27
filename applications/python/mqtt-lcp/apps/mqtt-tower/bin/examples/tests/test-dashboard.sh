#test.sh

echo "test ping"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/ping/mqtt-node-one' \
 -m '{"ping": {"version": "1.0", "timestamp": 1577804139, "node-id": "mqtt-node-one", "state": {"reported": "ping"}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/ping/mqtt-node-two' \
 -m '{"ping": {"version": "1.0", "timestamp": 1577804139, "node-id": "mqtt-node-two", "state": {"reported": "ping"}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/ping/mqtt-node-three' \
 -m '{"ping": {"version": "1.0", "timestamp": 1577804139, "node-id": "mqtt-node-three", "state": {"reported": "ping"}}}'

sleep 10

echo "test reports"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/report/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HOSTNAME'-registry", "port-id":"reports", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"dashboard"}}}}'


echo "waiting till test nodes time out ..."

sleep 60

# report, check test node has errored out

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/report/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HOSTNAME'-registry", "port-id":"reports", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"dashboard"}}}}'


