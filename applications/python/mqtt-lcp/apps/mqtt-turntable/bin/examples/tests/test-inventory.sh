echo "test inventory report request"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-railcom/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "mqtt-dev-supervisor", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": {"report" : "inventory"}}}}'
