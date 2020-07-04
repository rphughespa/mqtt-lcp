# mqtt_registry_helper.py

"""

    mqtt_registry_helper - helper class that generates/parses mqtt messages to/from mqtt-registry


The MIT License (MIT)

Copyright © 2020 richard p hughes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the “Software”), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import os
import json
import time

from global_constants import Global
from node_base_mqtt import NodeBaseMqtt

class MqttRegistryHelper():
    """ helper class for processing mqtt-registry messages """

    def __init__(self, parent, log_queue):
        """ initialize """
        self.parent = parent
        if not isinstance(self.parent, NodeBaseMqtt):
            raise TypeError("MqttRegistryHelper parent object not NodeBaseMqtt")
        self.log_queue = log_queue

    def request_registry_reports(self, report_type):
        """ publish a request for a registry report """
        if report_type not in (Global.ROSTER, Global.SWITCHES,
                Global.SIGNALS, Global.WARRANTS, Global.SENSORS,
                Global.DASHBOARD, Global.LAYOUT):
            self.parent.log_queue.add_message("error",
                    Global.REGISTRY+" "+Global.REPORT+" "+Global.TYPE+" "+Global.INVALID+": "+str(report_type))
        else:
            # publish a report request to mqtt
            now_seconds = self.parent.now_seconds()
            session_id = 'dt:'+str(int(now_seconds))
            if self.parent.topic_registry_pub is not None:
                state_topic = self.parent.topic_registry_pub
                state_message = self.parent.format_state_body(self.parent.node_name, Global.REGISTRY,
                        session_id, None, {Global.REPORT:report_type},
                        response_topic=self.parent.topic_self_subscribed+"/"+Global.RES)
                self.parent.send_to_mqtt(state_topic, state_message)
                #self.parent.log_queue.add_message("info",
                #        Global.PUBLISH+": "+Global.REGISTRY+" "+Global.REPORT+" "+Global+REQUEST+": "+str(report_type))
