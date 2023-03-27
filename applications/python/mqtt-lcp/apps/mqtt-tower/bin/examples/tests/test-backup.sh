test.sh

echo "test inventory"


body1='{"backup": {"version": "1.0", "timestamp": 1597354169, "session-id": "dt:1597354169", "node-id": "harris-1", "state": {"reported": {"report": "inventory"}},'
meta1='"metadata": {"config":{'
meta2='"node": {"name": "harris-1"},'
meta3='"logger" : {"level": "info"},'
meta4='"io": {"mqtt" : {"broker" : "mqtt-broker.local","port" : 1883,"user" : "trains",'
meta5='"password" : "choochoo","ping" : 15,'
meta6='"sub-topics": {"self": "cmd/mqtt-lcp/node/**node**/#","broadcast": "cmd/mqtt-lcp/node/all/req"},'
meta7='"pub-topics": {"ping": "dt/mqtt-lcp/ping/**node**"}}},'
meta8='"options": {"shutdown-command": "sudo /usr/sbin/shutdown -h now",'
meta9='"reboot-command": "sudo /usr/sbin/shutdown -r now"}}}}}'



body=$body1$meta1$meta2$meta3$meta4$meta5$meta6$meta7$meta8$meta9

echo "Inventory Body: $body"

mosquitto_pub -h mqtt-broker.local -u trains -P choochoo \
	-t 'dt/mqtt-lcp/backup/harris-1' \
	-m "$body"
