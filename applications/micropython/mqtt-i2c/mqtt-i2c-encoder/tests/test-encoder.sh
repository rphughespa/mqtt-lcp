#test.sh

HNAME="mqtt-i2c-encoder"

echo "test reset encoder "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/sensor/'$HNAME'/throttle1/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"throttle1", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "reset"}}}'

sleep 2

echo "test throw sensor "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/sensor/'$HNAME'/throttle1/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"throttle1", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": 10}}}'

sleep 2

echo "test close sensor "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/sensor/'$HNAME'/throttle1/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"throttle1", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": 40}}}'

sleep 2


echo "test close sensor "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/sensor/'$HNAME'/throttle1/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"throttle1", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": 80}}}'

sleep 2

echo "test close sensor "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/sensor/'$HNAME'/throttle1/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"throttle1", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "XYZ"}}}'

sleep 2

echo "test sensor on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/sensor/'$HNAME'/throttle1/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"throttle1", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": 100}}}'

sleep 2

echo "test sensor on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/sensor/'$HNAME'/throttle1/req' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"throttle1", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "reset"}}}'

sleep 4

