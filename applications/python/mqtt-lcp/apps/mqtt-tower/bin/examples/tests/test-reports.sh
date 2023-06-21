#test.sh

cp ../../data/*.json ~/mqtt-lcp/data

echo "test reports"

# set tower server
export HNAME="mqtt-tower"

echo ":report inventory"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/inventory/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"inventory", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "report"}}}'

sleep 2

echo "report panels"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/panel/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"panel", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "report"}}}'

sleep 2

echo "report signals"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/signal/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'-", "port-id":"signal", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "report"}}}'

sleep 2

echo "report switches"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/switch/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'-", "port-id":"switch", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "report"}}}'

sleep 2

echo "report blocks"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/block/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'-", "port-id":"block", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "report"}}}'

sleep 2

echo "report locators"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/locator/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'-", "port-id":"locator", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "report"}}}'

sleep 2

echo "report states"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/state/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'-", "port-id":"state", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "report"}}}'

sleep 2
