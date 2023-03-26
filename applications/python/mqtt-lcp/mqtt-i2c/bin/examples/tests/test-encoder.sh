#test.sh

echo "test encode reset "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/throttle/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"throttle", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "reset"}}}'

