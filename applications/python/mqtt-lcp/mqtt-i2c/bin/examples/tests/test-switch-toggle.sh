#test.sh


echo "test mcp23017"
echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/lumber-yard-siding/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"lumber-yard-siding", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 2


echo "test close switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/lumber-yard-siding/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"lumber-yard-siding", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 2


echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/lumber-yard-siding/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"lumber-yard-siding", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 2


echo "test throw off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/lumber-yard-siding/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"lumber-yard-siding", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2

echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/mill-siding"/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"mill-siding", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 2

echo "test relays"
echo "test close switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/mill-siding/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"mill-siding", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 2


echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/mill-siding/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"mill-siding", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 2


echo "test throw off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/mill-siding/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"mill-siding", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'
