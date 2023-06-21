#test.sh

cp ../../data/*.json ~/mqtt-lcp/data

echo "test reports"

# set tower server
export HNAME="mqtt-tower"

echo ":report inventory"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/tower/'$HNAME'/inventory/req' \
 -m '{"tower": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"inventory", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": "report"}}}'

