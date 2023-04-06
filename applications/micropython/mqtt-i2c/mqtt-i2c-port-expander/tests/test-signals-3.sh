#test.sh

HNAME="mqtt-i2c-port-expander"


echo "test signal signal- on"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/blink/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"blink", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 8

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/blink/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"blink", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 4

