#test.sh

HNAME="mqtt-dev-i2c"
# HNAME='mqtt-zero'

echo "test signal signal- on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/130w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"130w-39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/131w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"131w-39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 2

echo "test signal signal- clear "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e-39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "clear"}}}'


mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/112e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112e-39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "clear"}}}'

sleep 2

echo "test multi signal - approach "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e-39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/112e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112e 39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 2

echo "test multi signal - stop"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/121e-39/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e-39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "stop"}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/112e-39/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112e-39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "stop"}}}'

sleep 2

echo "test multi signal - off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/121e-39/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e-39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/112e-39/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112e-39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/130w-39/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"130w-39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/131w-39/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"131w-39", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2
