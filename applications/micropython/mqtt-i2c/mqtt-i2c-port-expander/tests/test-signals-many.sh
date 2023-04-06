#test.sh

HNAME="mqtt-i2c-port-expander"


echo "test signal signal- on"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/single/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"single", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 2

echo "test signal signal- on"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/blink/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"blink", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'
sleep 2

echo "test signal signal- on"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/flash/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"flash", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 2

echo "test signal signal- approach "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/130w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"130w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 2

echo "test signal signal- approach "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/112e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 2

echo "test signal signal- approach "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 12
echo "..."
sleep 8

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/130w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"130w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2


echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/flash/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"flash", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/112e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/blink/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"blink", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/single/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"single", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2