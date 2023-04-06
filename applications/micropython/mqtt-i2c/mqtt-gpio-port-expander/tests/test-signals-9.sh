#test.sh

HNAME="mqtt-gpio-port-expander"


echo "test signal signal- clear "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "clear"}}}'

sleep 4

echo "test signal signal- approach "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 4

echo "test signal signal- stop "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "stop"}}}'

sleep 4

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 4