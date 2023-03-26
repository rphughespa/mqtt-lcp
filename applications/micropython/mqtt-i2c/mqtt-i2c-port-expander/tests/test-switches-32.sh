#test.sh
HNAME="mqtt-i2c-port-expander-relay"


echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

#sleep 2

echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/oak/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"oak", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 4

echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

#sleep 2

echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/oak/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"oak", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 4


echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/oak/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"oak", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

#sleep 2

echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 4

echo "test switch off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/oak/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"oak", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

#sleep 2

echo "test throw off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

