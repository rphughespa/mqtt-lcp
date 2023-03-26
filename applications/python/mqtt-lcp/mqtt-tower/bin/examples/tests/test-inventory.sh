# test inventory


echo "Test Inventory"

echo "Report State"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/report/req' \
  -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HOSTNAME'-registry", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"states"}}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/report/req' \
  -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "'$HOSTNAME'-registry", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"states"}}}}'


sleep 3

echo "Test Update Inventory"

body1='{"registry": {"version": "1.0", "timestamp": 1597354169, "session-id": "req:1597354169", "node-id": "bayside-tower", "state": {"desired": {"report": "inventory"}, "reported": {"report": "inventory"}},'

meta1='"metadata": {"inventory":'
meta2='{"switch": ['
meta3='{"name": "siding-north-east","node-id": "bayside-tower","port-id": "siding-north-east",'
meta4='"reported" : {"switch": "closed"},"timestamp" : 1597858046},'
meta5='{"name": "siding-south-west","node-id": "bayside-tower","port-id": "siding-south-west",'
meta6='"reported" : {"switch": "thrown"},"timestamp" : 1597858036}'
meta7='],"sensor": ['
meta8='{"name": "siding-north","node-id": "bayside-tower","port-id": "siding-north",'
meta9='"reported" : {"block": "clear"},"timestamp" : 1597858026},'
meta10='{"name": "siding-south","node-id": "bayside-tower","port-id": "siding-south",'
meta11='"reported" : {"block": "occupied"},"timestamp" : 1597858016}'
meta12='],"signal": ['
meta13='{"name": "north-eb","node-id": "bayside-tower","port-id": "north-eb",'
meta14='"reported" : {"block": "approach"},"timestamp" : 1597858016},'
meta15='{"name": "south-eb","node-id": "bayside-tower","port-id": "south-eb",'
meta16='"reported" : {"block": "stop"},"timestamp" : 1597858076}'
meta17=']}}}}'

body2=$meta1$meta2$meta3$meta4$meta5$meta6$meta7$meta8$meta9
body3=$meta10$meta11$meta12$meta13$meta14$meta15$meta16$meta17
body=$body1$body2$body3

echo "Inventory Body: $body"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
	-t 'cmd/mqtt-lcp/node/'$HOSTNAME'-registry/res' \
	-m "$body"

sleep 10

echo "Report after inventory update"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/report/req' \
  -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"inventory"}}}}'

sleep 3

echo "Test Update State"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/report/req' \
  -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"states"}}}}'

sleep 3

echo "test ping"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "siding-north-east", "state": {"reported": {"sensor": "on"}}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "siding-north-south", "state": {"reported": {"sensor": "clicked"}}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"sensor": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "siding-north-north", "state": {"reported": {"data": 123}}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "siding-south-west", "state": {"reported": {"switch": "closed"}}}}'


mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"signal": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "south-eb", "state": {"reported": {"signal": "approach"}}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "main-north-eb", "state": {"reported": {"block": "entered"}}, "loco-id":"1234"}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "main-siding-north", "state": {"reported": {"block": "occupied"}}}}'

####
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/report/req' \
  -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"states"}}}}'

sleep 3
####

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"switch": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "siding-south-west", "state": {"reported": {"switch": "thrown"}}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"block": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "siding-south", "state": {"reported": {"block": "clear"}}}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "main-north-eb", "state": {"reported": {"block": "entered"}}, "loco-id":"5678"}}'

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "main-north-sb", "state": {"reported": {"detected": "123456"}}, "loco-id":"5678"}}'

####
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/report/req' \
  -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"states"}}}}'

sleep 3
####
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/sensor/bayside-tower' \
 -m '{"locator": {"version": "1.0", "timestamp": 1577804139, "node-id": "bayside-tower", "port-id": "main-north-eb", "state": {"reported": {"block": "exited"}}, "loco-id":"1234"}}'
sleep 10

echo "Test Reports after update state"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/registry/'$HOSTNAME'-registry/report/req' \
  -m '{"registry": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "speed-test-requestor", "respond-to": "cmd/mqtt-lcp/nodes/speed-test-requestor/res", "state": {"desired": {"report":"states"}}}}'


sleep 3