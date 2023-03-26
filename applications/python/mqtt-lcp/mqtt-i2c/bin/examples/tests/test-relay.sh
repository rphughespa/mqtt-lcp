#test.
echo "test on signal w/blink"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 2

echo "test on signal w/blink"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/130w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"130w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 2
130w
echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/maryville-toggle/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville-toggle", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 2

echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/maryville-duplex/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville-duplex", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 2

echo "test throw switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/maryville-duplex-pulse/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville-duplex-pulse", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 2

echo "test on signal "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/130w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"130w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "on"}}}'

sleep 2

echo "test stop signal "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/112e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "stop"}}}'

sleep 2

echo "test stop signal "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "stop"}}}'

sleep 2

echo "test yield signal "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/112e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 2

echo "test yield signal "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 2

echo "test clear signal "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/112e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "clear"}}}'

sleep 2

echo "test clear signal "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "clear"}}}'

sleep 2

echo "test off signal "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/112e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2

echo "test off signal "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2
echo "test off signal "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/130w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"130w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 2


echo "test close switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/maryville-toggle/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville-toggle", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 2

echo "test close switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/maryville-duplex/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville-duplex", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 2

echo "test close switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/maryville-duplex-pulse/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville-duplex-pulse", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 2

echo "... waiting "
sleep 10

echo "test off signal w/blink"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 10
echo "test off signal w/blink"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-i2c/122w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"122w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "off"}}}'

sleep 10
