#test.sh




echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/mill-siding-duplex-pulse/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"mill-siding-duplex-pulse", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 5



echo "test close switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/mill-siding-duplex-pulse/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"mill-siding-duplex-pulse", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 5

echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/mill-siding-duplex-pulse/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"mill-siding-duplex-pulse", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 5


echo "test close switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/mill-siding-duplex-pulse/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"mill-siding-duplex-pulse", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 5

echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/mill-siding-duplex-pulse/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"mill-siding-duplex-pulse", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 5


echo "test close switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/mqtt-dev-i2c/mill-siding-duplex-pulse/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"mill-siding-duplex-pulse", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 2
