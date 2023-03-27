echo "test test track messages"

HNAME="mqtt-dev-proto"

echo "init layout"

echo "test signal approach 130w"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/130w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"130w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

echo "test signal approach 131w"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/131w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"131w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

echo "test signal approach 132e"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/132e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"132e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 1

echo "test signal approach 111w"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/111w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"111w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'


echo "test signal approach 112e"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/112e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"112e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

echo "test signal approach 110w"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/110w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"110w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 1

echo "test signal approach 120e"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/120e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"120e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'


echo "test signal approach 121e"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/121e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"121e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'


echo "test signal approach 122w"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/122w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"122w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 1

echo "test signal approach 142w"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/142w/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"142w", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'


echo "test signal approach 141e"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/132e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"141e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'


echo "test signal approach 140e"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/140e/req' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"140e", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "approach"}}}'

sleep 1

echo "test close switch maryville"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

echo "test close switch oak"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"oak", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

echo "test close switch summersville"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"summersville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

echo "test close switch garland"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"garland", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

echo "block 22 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"22", "state": {"reported": "clear"}}}'

echo "block 24 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"24", "state": {"reported": "clear"}}}'

echo "block 27 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"27", "state": {"reported": "clear"}}}'

echo "block 26 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"26", "state": {"reported": "clear"}}}'


echo "block 25 occupied"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"25", "state": {"reported": "occupied"}}}'

echo "locate loco 1234 in block 25"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"25", "loco-id":1234, "state": {"reported": "entered"}},"metadata":{"type":"railcom"}}'

echo "block 23 occupied"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"23", "state": {"reported": "occupied"}}}'

echo "locate loco 5678 in block 22"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"23", "loco-id":5678, "state": {"reported": "entered"},"metadata":{"type":"railcom"}}}'

sleep 3

echo "move loco 1234"

echo "test throw switch maryville"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 3


echo "block 24 occupied"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"24", "state": {"reported": "occupied"}}}'

echo "locate loco 1234 in block 24"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"24", "loco-id":1234, "state": {"reported": "entered"}}}'

sleep 2

echo "block 25 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"25", "state": {"reported": "clear"}}}'

echo "exit loco 1234 in block 25"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"25", "loco-id":1234, "state": {"reported": "exited"}}}'

sleep 3

echo "test close switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/maryville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"maryville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 3

echo "block 22 occupied"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"22", "state": {"reported": "occupied"}}}'

echo "locate loco 1234 in block 22"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"22", "loco-id":1234, "state": {"reported": "entered"},"metadata":{"type":"railcom"}}}'

sleep 2

echo "locate loco 1234 in rfid loc 'station'"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"station", "loco-id":1234, "state": {"reported": "detected"},"metadata":{"type":"rfid"}}}'
sleep 2

echo "block 24 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"24", "state": {"reported": "clear"}}}'

echo "exit loco 1234 in block 24"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"24", "loco-id":1234, "state": {"reported": "exited"}, "metadata":{"type":"railcom"}}}'

sleep 3

echo "block 26 occupied"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"26", "state": {"reported": "occupied"}}}'

echo "locate loco 1234 in block 26"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"26", "loco-id":1234, "state": {"reported": "entered"},"metadata":{"type":"railcom"}}}'

sleep 2

echo "block 22 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"22", "state": {"reported": "clear"}}}'

echo "exit loco 1234 in block 22"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"22", "loco-id":1234, "state": {"reported": "exited"},"metadata":{"type":"railcom"}}}'

sleep 3

echo "test throw switch oak"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/oak/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"oak", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 3

echo "block 25 occupied"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"25", "state": {"reported": "occupied"},"metadata":{"type":"railcom"}}}'

echo "locate loco 1234 in block 25"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"25", "loco-id":1234, "state": {"reported": "entered"},"metadata":{"type":"railcom"}}}'

sleep 2

echo "block 26 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"26", "state": {"reported": "clear"}}}'

echo "exit loco 1234 in block 26"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"26", "loco-id":1234, "state": {"reported": "exited"},"metadata":{"type":"railcom"}}}'

sleep 3

echo "test close switch oak"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/oak/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"oak", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 3

echo "move loco 5678"

echo "test throw switch summersville"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/summersville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"summersville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 3


echo "block 26 occupied"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"26", "state": {"reported": "occupied"}}}'

echo "locate loco 5678 in block 26"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"26", "loco-id":5678, "state": {"reported": "entered"}}}'

sleep 2

echo "block 23 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"23", "state": {"reported": "clear"}}}'

echo "exit loco 5678 in block 23"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"23", "loco-id":5678, "state": {"reported": "exited"}}}'

sleep 3

echo "test close switch "
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/summersville/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"summersville", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 3

echo "block 27 occupied"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"27", "state": {"reported": "occupied"}}}'

echo "locate loco 5678 in block 27"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"27", "loco-id":5678, "state": {"reported": "entered"},"metadata":{"type":"railcom"}}}'

sleep 2


echo "block 26 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"26", "state": {"reported": "clear"}}}'

echo "exit loco 5678 in block 26"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"26", "loco-id":5678, "state": {"reported": "exited"}, "metadata":{"type":"railcom"}}}'

sleep 3

echo "block 24 occupied"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"24", "state": {"reported": "occupied"}}}'

echo "locate loco 5678 in block 24"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"24", "loco-id":5678, "state": {"reported": "entered"},"metadata":{"type":"railcom"}}}'

sleep 2

echo "block 27 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"27", "state": {"reported": "clear"}}}'

echo "exit loco 5678 in block 27"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"27", "loco-id":5678, "state": {"reported": "exited"},"metadata":{"type":"railcom"}}}'

sleep 3

echo "test throw switch garland"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/garland/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"garland", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "throw"}}}'

sleep 3

echo "block 23 occupied"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"23", "state": {"reported": "occupied"},"metadata":{"type":"railcom"}}}'

echo "locate loco 5678 in block 23"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"23", "loco-id":5678, "state": {"reported": "entered"},"metadata":{"type":"railcom"}}}'

sleep 2

echo "block 24 clear"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"24", "state": {"reported": "clear"}}}'

echo "exit loco 5678 in block 24"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/req' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'", "port-id":"24", "loco-id":5678, "state": {"reported": "exited"},"metadata":{"type":"railcom"}}}'

sleep 3

echo "test close switch garland"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HNAME'/garland/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-xxx-pi-throttle", "port-id":"garland", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "close"}}}'

sleep 3