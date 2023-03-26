#test.sh

echo "home"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-turntable/home/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "home", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "head"}}}'

sleep 30

echo "head 1"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-turntable/track-1/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "track-1", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "head"}}}'

sleep 5

echo "tail 3, should fail, turntable is busy"


mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-turntable/track-3/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "track-3", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "tail"}}}'


sleep 30

echo "head 6"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-turntable/track-3/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "track-3", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "head"}}}'


sleep 3

