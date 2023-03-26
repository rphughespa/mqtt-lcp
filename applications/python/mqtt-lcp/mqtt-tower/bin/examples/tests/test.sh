#test.sh

./test-dashboard.sh

./test-reports.sh

./test-fastclock.sh

./test-inventory.sh

./test-backup.sh

sleep 6


echo  "test backup request"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-registry/req' \
 -m '{"command": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "throttle-1", "port-id": "rotary-1", "respond-to": "dt/mqtt-lcp/backup", "state": {"desired": "backup"}}}'


sleep 6

echo "test shutdown"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/node/'$HOSTNAME'-registry/req' \
 -m '{"node": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "all", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "shutdown"}}}'


