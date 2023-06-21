
HNAME="mqtt-dev-proto"
RAILCOM="mqtt-broker-railcom"

# initialize

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-25' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-25", "loco-id":1234,  "block-id":"25", "direction":"east", "state": {"reported": "entered"}, "metadata":{"type":"railcom"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$RAILCOM'/25' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-25", "block-id":"25", "state": {"reported": "occupied"}}}'

sleep 3

# move to block 26

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/switch/'$HNAME'/oak' \
 -m '{"switch": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"oak", "state": {"reported": "thrown"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$RAILCOM'/26' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-26", "block-id":"26", "state": {"reported": "occupied"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-26' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-26", "loco-id":1234,  "block-id":"26", "direction":"east", "state": {"reported": "entered"}, "metadata":{"type":"railcom"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$RAILCOM'/25' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-25", "block-id":"25", "state": {"reported": "clear"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo  \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-25' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-25", "loco-id":1234,  "block-id":"25", "direction":"east", "state": {"reported": "exited"}, "metadata":{"type":"railcom"}}}'

sleep 3

# move to block 22

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$RAILCOM'/22' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-22", "block-id":"22", "state": {"reported": "occupied"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/switch/'$HNAME'/oak' \
 -m '{"switch": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"oak", "state": {"reported": "closed"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-22' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-22", "loco-id":1234,  "block-id":"22", "direction":"east", "state": {"reported": "entered"}, "metadata":{"type":"railcom"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$RAILCOM'/22' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-26", "block-id":"26", "state": {"reported": "clear"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-26' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-26", "loco-id":1234,  "block-id":"26", "direction":"east", "state": {"reported": "exited"}, "metadata":{"type":"railcom"}}}'

sleep 3

# entered 24

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$RAILCOM'/24' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-24", "block-id":"24", "state": {"reported": "occupied"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/switch/'$HNAME'/maryville' \
 -m '{"switch": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"maryville", "state": {"reported": "thrown"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-24' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-24", "loco-id":1234,  "block-id":"24", "direction":"east", "state": {"reported": "entered"}, "metadata":{"type":"railcom"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$RAILCOM'/22' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-22", "block-id":"22", "state": {"reported": "clear"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-22' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-22", "loco-id":1234,  "block-id":"22", "direction":"east", "state": {"reported": "exited"}, "metadata":{"type":"railcom"}}}'

sleep 3

# entered 25

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$RAILCOM'/25' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-25", "block-id":"25", "state": {"reported": "occupied"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-25' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-25", "loco-id":3456,  "block-id":"25", "direction":"east", "state": {"reported": "entered"}, "metadata":{"type":"railcom"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/block/'$RAILCOM'/24' \
 -m '{"block": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"block-24", "block-id":"24", "state": {"reported": "clear"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-24' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-24", "loco-id":3456,  "block-id":"24", "direction":"east", "state": {"reported": "exited"}, "metadata":{"type":"railcom"}}}'

sleep 1


EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-25' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-25", "loco-id":1234,  "block-id":"25", "direction":"east", "state": {"reported": "entered"}, "metadata":{"type":"railcom"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-24' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-24", "loco-id":1234,  "block-id":"24", "direction":"east", "state": {"reported": "exited"}, "metadata":{"type":"railcom"}}}'
sleep 3

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/switch/'$HNAME'/maryville' \
 -m '{"switch": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"maryville", "state": {"reported": "closed"}}}'

sleep 3

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/locator/'$RAILCOM'/railcom-25' \
 -m '{"locator": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$RAILCOM'", "port-id":"railcom-25", "loco-id":3456,  "block-id":"25", "direction":"east", "state": {"reported": "exited"}, "metadata":{"type":"railcom"}}}'

sleep 1

EPOCH=`date +"%s"`000
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'dt/mqtt-lcp/switch/'$HNAME'/maryville' \
 -m '{"switch": {"version": "1.0", "timestamp": '$EPOCH', "session-id": "req:'$EPOCH'", "node-id": "'$HNAME'", "port-id":"maryville", "state": {"reported": "closed"}}}'

sleep 3