#test.sh


echo "test reports"

# set tower server
#export HNAME="mqtt"
# export HNAME=$HOSTNAME
export HNAME='mqtt-dev-ex'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/registry/'$HNAME'-registry/report/req' \
 -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HNAME'-registry", "port-id":"reports", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report": "inventory"}}}}'

