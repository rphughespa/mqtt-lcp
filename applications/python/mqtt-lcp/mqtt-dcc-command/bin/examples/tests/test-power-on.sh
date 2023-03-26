

echo "power on"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/'$HOSTNAME'-dcc-command/power/req' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "power", "respond-to": "cmd/mqtt-lcp/node/throttle1/res", "state": {"desired": "on"}}}'

sleep 3

