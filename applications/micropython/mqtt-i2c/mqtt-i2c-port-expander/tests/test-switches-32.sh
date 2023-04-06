#test.sh
HNAME="mqtt-i2c-port-expander"

echo "test signal signal- on"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/single2/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"single2", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 4

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/single2/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"single2", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 4

echo "test signal signal- on"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/blink2/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"blink2", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 8

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/blink2/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"blink2", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 4

echo "test signal signal- on"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/flash2/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"flash2", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 8

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/flash2/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"flash2", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 4

echo "test signal signal- clear "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/112w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "clear"}}}'

sleep 4

echo "test signal signal- approach "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/112w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 4

echo "test signal signal- stop "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/112w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "stop"}}}'

sleep 4

echo "test signal signal- off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/signal/'$HNAME'/112w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 4
echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 2

echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/oak/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"oak", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 4

echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 2

echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/oak/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"oak", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 4


echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/oak/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"oak", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 2

echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 4

echo "test switch off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/oak/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"oak", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2

echo "test throw off "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

echo "test switch on "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 4