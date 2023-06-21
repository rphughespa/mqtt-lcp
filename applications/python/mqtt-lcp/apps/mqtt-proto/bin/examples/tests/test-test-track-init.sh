echo "test test track messages"

HNAME="mqtt-dev-proto"
RAILCOM="mqtt-broker-railcom"

echo "initialize layout"

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$HNAME'/21' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-21", "block-id":"21", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$HNAME'/22' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-22", "block-id":"22", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$HNAME'/23' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-23", "block-id":"23", "state": {"reported": "occupied"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$HNAME'/24' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-24", "block-id":"24", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$HNAME'/25' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-25", "block-id":"25", "state": {"reported": "occupied"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$HNAME'/26' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-26", "block-id":"26", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$HNAME'/27' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-27", "block-id":"27", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/switch/'$HNAME'/oak' \
 -m '{"switch": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"oak", "state": {"reported": "closed"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/switch/'$HNAME'/maryville' \
 -m '{"switch": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"maryville", "state": {"reported": "closed"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/switch/'$HNAME'/garland' \
 -m '{"switch": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"garland", "state": {"reported": "closed"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/switch/'$HNAME'/summersville' \
 -m '{"switch": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"summersville", "state": {"reported": "closed"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/110w' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"110e", "state": {"reported": "approach"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/111w' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"111e", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/112e' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"112w", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/120e' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"120w", "state": {"reported": "approach"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/121e' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"121w", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/122w' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"122e", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/130w' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"130w", "state": {"reported": "approach"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/131w' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"131w", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/132e' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"132e", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/140e' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"140e", "state": {"reported": "approach"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/141e' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"141e", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/signal/'$HNAME'/142w' \
 -m '{"signal": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"142w", "state": {"reported": "clear"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/railcom-25' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-25", "loco-id":1234,  "block-id":"25", "direction":"east","state": {"reported": "entered"}, "metadata":{"type":"railcom"}}}'

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$HNAME'/railcom-23' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-23", "loco-id":5678,  "block-id":"23", "direction":"west", "state": {"reported": "entered"}, "metadata":{"type":"railcom"}}}'
