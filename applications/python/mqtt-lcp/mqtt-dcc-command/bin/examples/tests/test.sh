#test.sh

# test
echo "power off"

body1='{"track": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2='"node-id": "desktop-throttle", "port-id": "track", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/res",'
body3='"state": {"desired": {"power" : "off"}}}}'
body=$body1$body2$body3
# echo $body

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/track/mqtt-dev-dcc-command/track/req' \
 -m "$body"

sleep 1

echo "power on"

body1='{"track": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2='"node-id": "desktop-throttle", "port-id": "track", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/res",'
body3='"state": {"desired": {"power":"on"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/track/mqtt-dev-dcc-command/track/req' \
 -m "$body"

sleep 1

echo "power report"

body1='{"track": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2='"node-id": "desktop-throttle", "port-id": "track", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/res",'
body3='"state": {"desired": {"report":"power"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/track/mqtt-dev-dcc-command/track/req' \
 -m "$body"

sleep 1

echo "connect"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2='"node-id": "desktop-throttle", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/res",'
body3='"state": {"desired": "connect"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "connect"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2='"node-id": "handheld-throttle",  "respond-to": "cmd/mqtt-lcp/node/handheld-throttle/res", '
body3='"state": {"desired": "connect"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m  "$body"

sleep 1

echo "acquire, cab-a"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "loco-id": "2239", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res",'
body3='"state": {"desired": "acquire"}, "metadata": {"name" : "PTC Trolley"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "loco-id": "2234", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res",'
body3='"state": {"desired": "acquire"}, "metadata": {"direction": "reverse"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "loco-id": "3234", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res",'
body3='"state": {"desired": "acquire"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "acquitre, cab-b"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-b", "loco-id": "0603", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-b/res", '
body3='"state": {"desired": "acquire"}, "metadata": {"name" : "P54"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-b", "loco-id":"4352", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-b/res", '
body3='"state": {"desired": "acquire"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "acquitre, cab-1"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2=' "node-id": "handheld-throttle", "port-id": "cab-1", "loco-id":"3477", "respond-to": "cmd/mqtt-lcp/node/handheld-throttle/cab-1/res", '
body3='"state": {"desired": "acquire"}, "metadata" : {"name":"prr-e8b-green-3477"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "acquitre, cab-2"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2=' "node-id": "handheld-throttle", "port-id": "cab-2", "loco-id":"2865", "respond-to": "cmd/mqtt-lcp/node/handheldp-throttle/cab-1/res", '
body3='"state": {"desired": "acquire"}, "metadata" : {"name":"prr-k4s-2865"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "set lead"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "loco-id": "2234", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res", '
body3='"state": {"desired": "set-lead"}}}'
body=$body1$body2$body3
echo "$body"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

echo "steal a loco"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2=' "node-id": "handheld-throttle", "port-id": "cab-2", "loco-id":"0603", "respond-to": "cmd/mqtt-lcp/node/handheld-throttle/cab-2/res", '
body3='"state": {"desired": "acquire"}}}'
body=$body1$body2$body3
echo "$body"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2=' "node-id": "handheld-throttle", "port-id": "cab-2", "loco-id":"0603", "respond-to": "cmd/mqtt-lcp/node/handheld-throttle/cab-2/res", '
body3='"state": {"desired": "steal"}}}'
body=$body1$body2$body3
echo "$body"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
  -m "$body"

sleep 1

echo "move multiple locos forward"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res", '
body3='"state": {"desired": {"direction":"forward"}}}}'
body=$body1$body2$body3
echo "$body"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "set speed to 12"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res", '
body3='"state": {"desired": {"speed":12}}}}'
body=$body1$body2$body3
echo "$body"
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res", '
body3='"state": {"desired": {"report":"speed"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "stop loco"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res", '
body3='"state": {"desired": {"speed":0}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

echo "report speed"

sleep 1
body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-b", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-b/res", '
body3='"state": {"desired": {"report":"speed"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

echo "report direction"

sleep 1
body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-b", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-b/res", '
body3='"state": {"desired": {"report":"direction"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

echo "ping throttle to keep it alive"
sleep 1
body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res", '
body3='"state": {"desired": "ping"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle' \
 -m "$body"

echo "ping throttle to keep it alive"
sleep 1
body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-b", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-b/res", '
body3='"state": {"desired": "ping"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle' \
 -m "$body"

echo "move one loco forward"

echo "set speed to 12"

 body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
 body2='"node-id": "handheld-throttle", "port-id": "cab-2", "loco-id":"2865", "respond-to": "cmd/mqtt-lcp/node/handheld-throttle/cab-2/res", '
 body3='"state": {"desired": {"speed":12}}}}'
 body=$body1$body2$body3
 mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
  -m "$body"

sleep 1

echo "report speed"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "handheld-throttle", "port-id": "cab-2", "loco-id":"2865", "respond-to": "cmd/mqtt-lcp/handheld-throttle/cab-2/res", '
body3='"state": {"desired": {"report":"speed"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "report direction"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "handheld-throttle", "port-id": "cab-2", "loco-id":"2865", "respond-to": "cmd/mqtt-lcp/handheld-throttle/cab-2/res", '
body3='"state": {"desired": {"report":"direction"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "stop loco"

 body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "handheld-throttle", "port-id": "cab-2", "loco-id":"2865", "respond-to": "cmd/mqtt-lcp/handheld-throttle/cab-2/res", '
 body3='"state": {"desired": {"speed":0}}}}'
 body=$body1$body2$body3
 mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
  -m "$body"

sleep 1

echo "move loco reverse"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "handheld-throttle", "port-id": "cab-2", "loco-id":"2865", "respond-to": "cmd/mqtt-lcp/handheld-throttle/cab-2/res", '
body3='"state": {"desired": {"direction":"reverse"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "speed 12"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "handheld-throttle", "port-id": "cab-2", "loco-id":"2865", "respond-to": "cmd/mqtt-lcp/handheld-throttle/cab-2/res", '
body3='"state": {"desired": {"speed":12}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "stop loco"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "handheld-throttle", "port-id": "cab-2", "loco-id":"2865", "respond-to": "cmd/mqtt-lcp/handheld-throttle/cab-2/res", '
body3='"state": {"desired": {"speed":0}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "function on"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res", '
body3='"state": {"desired": {"function":5, "action":"on"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res", '
body3='"state": {"desired": {"function":5, "action":"off"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "handheld-throttle", "port-id": "cab-1", "loco-id":"3477", "respond-to": "cmd/mqtt-lcp/node/handheld-throttle/cab-1/res", '
body3='"state": {"desired": {"function":5, "action":"on"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "function off"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "handheld-throttle", "port-id": "cab-1", "loco-id":"3477", "respond-to": "cmd/mqtt-lcp/node/handheld-throttle/cab-1/res", '
body3='"state": {"desired": {"function":5, "action":"off"}}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 1

echo "test throw switch east"

body1='{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "siding-north-east", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/res", '
body3='"state": {"desired": "throw"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/switch/mqtt-dev-dcc-command/siding-east/req' \
 -m "$body"

sleep 1

echo "test close switch east"

body1='{"switch": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "siding-north-east", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/res", '
body3='"state": {"desired": "close"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
  -t 'cmd/mqtt-lcp/switch/mqtt-dev-dcc-command/siding-east/req' \
 -m "$body"

sleep 1

echo "release cabs"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-a", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-a/res", '
body3='"state": {"desired": "release"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "port-id": "cab-b", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/cab-b/res", '
body3='"state": {"desired": "release"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
-t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
-m "$body"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "handheld-throttle", "port-id": "cab-1", "respond-to": "cmd/mqtt-lcp/node/handheld-throttle/cab-1/res", '
body3='"state": {"desired": "release"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"


sleep 1

echo "disconnect throttles"

sleep 3

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "desktop-throttle", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/res", '
body3='"state": {"desired": "disconnect"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle/req' \
 -m "$body"

sleep 3

echo "power off"

body1='{"track": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139",'
body2='"node-id":"desktop-throttle", "port-id": "track", "respond-to": "cmd/mqtt-lcp/node/desktop-throttle/res",'
body3='"state": {"desired": {"power" : "off"}}}}'
body=$body1$body2$body3
# echo $body

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/track/mqtt-dev-dcc-command/track/req' \
 -m "$body"

sleep 3


echo "ping throttle to keep it alive"

body1='{"cab": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", '
body2='"node-id": "handheld-throttle", "port-id": "cab-1", "respond-to": "cmd/mqtt-lcp/node/handheld-throttle/cab-1/res", '
body3='"state": {"desired": "ping"}}}'
body=$body1$body2$body3
mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'dt/mqtt-lcp/cab/mqtt-dev-dcc-command/throttle' \
 -m "$body"

echo "Waiting for a timeout of throttle-2 (60 seconds)... "
date

sleep 60

echo "... wait done"
date

sleep 3

echo "test shutdown"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
 -t 'cmd/mqtt-lcp/node/mqtt-dev-dcc-command/req' \
 -m '{"node": {"version": "1.0", "timestamp": 1577804139, "session-id": "req:1577804139", "node-id": "all", "respond-to": "cmd/mqtt-lcp/throttle/throttle1/res", "state": {"desired": "shutdown"}}}'


