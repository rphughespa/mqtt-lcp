# node_base_command_station.py - base class for generic command station
"""


 node_base_command_station - base class for nodes that interact with multiple types of dcc command stations

the MIT License (MIT)

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

import time
import copy

from global_constants import Global
from local_constants import Local
from queue_py import Queue

from mqtt_throttle import MqttThrottle
from mqtt_cab import MqttCab
from dcc_device import DccDevice
from io_data import IoData
from global_synonyms import Synonyms
# change the specific command station type
from node_base_dccpp import NodeBaseDccpp


class NodeBaseCommandStation(NodeBaseDccpp):
    """
        Base class for node programs that interact with dcc++ command stations.
        Manages runs on main thread
    """

    def __init__(self):
        super().__init__()
        self.throttles = {}
        self.cabs = {}
        self.dcc_devices = []
        self.mqtt_devices = {}
        self.dcc_out_queue = Queue(100)
        self.dcc_in_queue = Queue(100)

    def initialize_threads(self):
        """ initialize all IO threads"""
        # load config file
        super().initialize_threads()
        self.__parse_config_data()

    def shutdown_theads(self):
        """ shutdown all IO threads"""

        # shutdown track power before exiting
        self.set_track_power_off()
        time.sleep(1)
        super().shutdown_threads()

    def __parse_config_data(self):
        """ Parse out Dcc items from config json file"""
        self.log_queue.add_message("debug", "parse i2c config")
        if Global.CONFIG in self.config:
            if Global.IO in self.config[Global.CONFIG]:
                if Global.DCC in self.config[Global.CONFIG][Global.IO]:
                    for dcc_node in self.config[Global.CONFIG][Global.IO][Global.DCC]:
                        dcc_type = None
                        dcc_device = None
                        mqtt_port = None
                        mqtt_type = None
                        mqtt_send_sensor_msg = False
                        dcc_address = None
                        dcc_sub_address = None
                        if Global.ADDRESS in dcc_node:
                            dcc_address = int(dcc_node[Global.ADDRESS])
                        # self.log_queue.add_message("info", "I2C Device config: "+str(address))
                        if Global.DEVICE_TYPE in dcc_node:
                            dcc_type = dcc_node[Global.DEVICE_TYPE]
                        if Global.DEVICE_TYPE in dcc_node:
                            dcc_type = dcc_node[Global.DEVICE_TYPE]
                        if Global.SUB_ADDRESS in dcc_node:
                            dcc_sub_address = dcc_node[Global.SUB_ADDRESS]
                        if Global.MQTT+"-"+Global.PORT in dcc_node:
                            mqtt_port = dcc_node[Global.MQTT+"-"+Global.PORT]
                        if Global.MQTT+"-"+Global.TYPE in dcc_node:
                            mqtt_type = dcc_node[Global.MQTT+"-"+Global.TYPE]
                        if Global.MQTT+"-"+Global.SENSOR in dcc_node:
                            sensor = dcc_node[Global.MQTT+"-"+Global.SENSOR]
                            mqtt_send_sensor_msg = bool(sensor == Global.TRUE)
                        dcc_device = DccDevice(self.log_queue, dcc_address,
                            mqtt_port=mqtt_port,
                            mqtt_type=mqtt_type,
                            mqtt_send_sensor_msg=mqtt_send_sensor_msg,
                            dcc_device_type=dcc_type,
                            dcc_sub_address=dcc_sub_address)
                        self.dcc_devices.append({'type': dcc_type, 'mqtt-port': mqtt_port, 'dev': dcc_device})
                        if mqtt_port is not None:
                            mqtt_key = str(mqtt_port)+":"+mqtt_type
                            self.mqtt_devices[mqtt_key] = dcc_device

        # override in child class

    def publish_cab_data_message(self, io_data):
        """ override in child class """
        pass

    def publish_response_message(self, io_data):
        """ override in child class """
        pass

        ####

    def __get_incomming_dcc_message_from_queue(self):
        """ retrieve a receieved message from the in queue """
        message = None
        if not self.dcc_in_queue.empty():
            message = self.dcc_in_queue.get()
        return message

    def __get_outgoing_dcc_message_from_queue(self):
        """ retrieve a receieved message from the out queue """
        message = None
        if not self.dcc_out_queue.empty():
            message = self.dcc_out_queue.get()
        return message

    def received_from_dcc(self, data):
        """ override in child class """
        pass

    def __send_to_dcc(self, request):
        rtype = request[Global.TYPE]
        io_data = request[Global.MESSAGE]
        if rtype == Global.SWITCH:
            self.__process_switch_request(io_data)
        elif rtype == Global.TRACK:
            self.__process_track_request(io_data)
        elif rtype == Global.THROTTLE:
            self.__process_track_request(io_data)
        elif rtype == Global.CAB:
            self.__process_cab_request(io_data)
        else:
            new_io_data = copy.deepcopy(io_data)
            new_io_data.reported = Global.ERROR
            new_io_data.metadata = {Global.MESSAGE:Local.MSG_ERROR_INVALID_REQUEST+" "+rtype}
            self.dcc_in_queue.put(new_io_data)

    def process_input(self):
        # process all input of a given type in order of importance: keyboard, serial, mqtt
        self.write_log_messages()
        dcc_output = self.__get_outgoing_dcc_message_from_queue()
        while dcc_output is not None:
            self.__send_to_dcc(dcc_output)
            dcc_output = self.__get_outgoing_dcc_message_from_queue()
        dcc_input = self.__get_incomming_dcc_message_from_queue()
        while dcc_input is not None:
            self.received_from_dcc(dcc_input)
            dcc_input = self.__get_incomming_dcc_message_from_queue()
        super().process_input()

    # switch functions

    def __process_switch_request(self, io_data):
        """ process a switch attahced to a dcc decoder """
        mqtt_key = str(io_data.mqtt_port)+":"+io_data.mqtt_type
        if mqtt_key not in self.mqtt_devices:
            io_data.reported = Global.ERROR
            io_data.metadata = Local.MSG_ERROR_BAD_PORT + " " +str(mqtt_key)
        else:
            dcc_device = self.mqtt_devices[mqtt_key]
            action = -1    # unknown
            if Synonyms.is_synonym_throw(io_data.mqtt_desired):
                action = 1  # throw/open/on
            elif Synonyms.is_synonym_close(io_data.mqtt_desired):
                action = 0  # close/off
            if action == -1:
                io_data.reported = Global.ERROR
                io_data.metadata = Local.MSG_ERROR_BAD_STATE + io_data.mqtt_desired
            else:
                io_data.reported = Synonyms.desired_to_reported(io_data.mqtt_desired)
                self.dcc_set_dcc_decoder(dcc_device.dcc_address, dcc_device.dcc_sub_address, action)
        self.dcc_in_queue.put(io_data)

    # track functions

    def __process_track_request(self, io_data):
        """ process track power request """
        request_ok = False
        power_value = io_data.get_desired_value_by_key(Global.POWER)
        if power_value is not None:
            if power_value == Global.OFF:
                self.set_track_power_off()
                resp_io_data = copy.deepcopy(io_data)
                resp_io_data.mqtt_reported = {Global.POWER:self.dcc_power_status}
                self.publish_response_message(resp_io_data)
                request_ok = True
            elif power_value == Global.ON:
                self.set_track_power_on()
                resp_io_data = copy.deepcopy(io_data)
                resp_io_data.mqtt_reported = {Global.POWER:self.dcc_power_status}
                self.publish_response_message(resp_io_data)
                request_ok = True
        else:
            report_value = io_data.get_desired_value_by_key(Global.REPORT)
            if report_value is not None:
                if report_value == Global.POWER:
                    self.get_track_status()
                    resp_io_data = copy.deepcopy(io_data)
                    resp_io_data.mqtt_reported = {Global.POWER:self.dcc_power_status}
                    self.publish_response_message(resp_io_data)
                    request_ok = True

        if not request_ok:
            error_msg = (Global.UNKNOWN + " " +
                    Global.TRACK + " "+ Global.STATE+" : ["+ str(io_data.mqtt_desired)+"]")
            self.publish_error_reponse(error_msg, io_data.mqtt_resp_topic, io_data)

    def set_track_power_on(self):
        """ set track power  on """
        self.log_queue.add_message("debug", Global.TRACK + " " +
                Global.POWER +' '+Global.REQUEST+': ('+Global.ON+')')
        self.dcc_set_track_power(Global.ON)
        self.log_queue.add_message("debug", Global.TRACK + " " +
                Global.POWER +' '+Global.RESPONSE + " {"+ str(self.dcc_power_status) +"}")
        return self.dcc_power_status

    def set_track_power_off(self):
        """ set track power off """
        self.log_queue.add_message("debug", Global.TRACK + " " +
                Global.POWER +' '+Global.REQUEST+': ('+Global.OFF+')')
        self.dcc_set_track_power(Global.OFF)
        self.log_queue.add_message("debug", Global.TRACK + " " +
                Global.POWER +' '+Global.RESPONSE + " {"+ str(self.dcc_power_status) +"}")
        self.__clear_throttles()
        return self.dcc_power_status

    def get_track_status(self):
        """ get status of dcc++ comamnd station """
        self.dcc_get_track_status()

    # throttle functions

    def purge_expired_throttles(self, now_seconds):
        """ force a disconnect throttle """
        pass

    def __connect_throttle(self, node_id):
        """ connect a new throttle """
        reported = Global.ERROR
        message = ""
        if node_id in self.throttles:
            reported = Global.ERROR
            message = Local.MSG_ERROR_THROTTLE_ALREADY_CONNECTED
        else:
            new_throttle = MqttThrottle(node_id)
            new_throttle.timestamp = self.now_seconds()
            self.throttles[new_throttle.node_id] = new_throttle
            reported = "connected"
        return reported, message

    def __disconnect_throttle(self, node_id):
        """ disconnect a throttle """
        reported = Global.ERROR
        message = ""
        if node_id not in self.throttles:
            reported = Global.ERROR
            message = Local.MSG_ERROR_THROTTLE_NOT_CONNECTED
        else:
            throttle = self.throttles[node_id]
            for cab_key in list(throttle.cabs):
                cab = throttle.cabs[cab_key]
                reported, message = self.__release_cab(throttle.node_id, cab.port_id)
                if reported == Global.ERROR:
                    break
            if reported != Global.ERROR:
                del self.throttles[node_id]
                reported = "disconnected"
        return reported, message

    def __clear_throttles(self):
        """ clear out all throttles """
        for throttle_key in list(self.throttles):
            throttle = self.throttles[throttle_key]
            reported, _message = self.__disconnect_throttle(throttle.node_id)
            io_data = IoData()
            io_data.mqtt_type = Global.CAB
            io_data.mqtt_node_id = throttle.node_id
            io_data.mqtt_metadata = {Global.MESSAGE: Local.MSG_ERROR_FORCED_DISCONNECT}
            io_data.reported = reported
            self.publish_cab_data_message(io_data)
        self.throttles = {}
        self.cabs = {}
        self.dcc_initialize_slots()

    # cab functions

    def __process_cab_request(self, io_data):
        """ process stationary request message"""
        request_ok = False
        desired = str(io_data.mqtt_desired)
        if desired == Global.CONNECT:
            reported, error_msg = self.__connect_throttle(io_data.mqtt_node)
            if reported != Global.ERROR:
                request_ok = True
        elif desired == Global.DISCONNECT:
            reported, error_msg = self.__disconnect_throttle(io_data.mqtt_node)
            if reported != Global.ERROR:
                request_ok = True
        elif desired == Global.ACQUIRE:
            consist = None
            if ((io_data.mqtt_metadata is not None) and
                    (Global.CONSIST in io_data.mqtt_metadata)):
                consist = io_data.mqtt_metadata[Global.CONSIST]
            reported, error_msg = self.__acquire_cab(io_data.mqtt_node,
                    io_data.mqtt_port, consist)
            if reported != Global.ERROR:
                request_ok = True
        elif desired == Global.STEAL:
            consist = None
            if ((io_data.mqtt_metadata is not None) and
                    (Global.CONSIST in io_data.mqtt_metadata)):
                consist = io_data.mqtt_metadata[Global.CONSIST]
            reported, error_msg = self.__acquire_cab(io_data.mqtt_node,
                    io_data.mqtt_port, consist, steal_cab=True)
            if reported != Global.ERROR:
                request_ok = True
        elif desired == Global.SHARE:
            consist = None
            if ((io_data.mqtt_metadata is not None) and
                    (Global.CONSIST in io_data.mqtt_metadata)):
                consist = io_data.mqtt_metadata[Global.CONSIST]
            reported, error_msg = self.__acquire_cab(io_data.mqtt_node,
                    io_data.mqtt_port, consist, share_cab=True)
            if reported != Global.ERROR:
                request_ok = True
        elif desired == Global.RELEASE:
            reported, error_msg = self.__release_cab(io_data.mqtt_node, io_data.mqtt_port)
            if reported != Global.ERROR:
                request_ok = True
        else:
            desired_speed = io_data.get_desired_value_by_key(Global.SPEED)
            if desired_speed is not None:
                desired_direction = io_data.get_desired_value_by_key(Global.DIRECTION)
                if ((desired_speed is not None) and (desired_direction is not None)):
                    reported, error_msg = self.__change_speed(io_data.mqtt_node, io_data.mqtt_port,
                        desired_speed, desired_direction)
                    if reported != Global.ERROR:
                        request_ok = True
            else:
                desired_function = io_data.get_desired_value_by_key(Global.FUNCTION)
                if desired_function is not None:
                    desired_action = io_data.get_desired_value_by_key(Global.ACTION)
                    if ((desired_function is not None) and (desired_action is not None)):
                        reported, error_msg = self.__change_function(io_data.mqtt_node,
                                io_data.mqtt_port,
                                desired_function, desired_action)
                        if reported != Global.ERROR:
                            request_ok = True
        if request_ok:
            pub_io_data = copy.deepcopy(io_data)
            pub_io_data.mqtt_reported = reported
            self.publish_response_message(pub_io_data)
        else:
            self.publish_error_reponse(error_msg, io_data.mqtt_resp_topic, io_data)

    def __is_cab_in_use(self, cab):
        """ is any loco in cab is use by any other cab in other throttles """
        in_use = False
        matching_cab = None
        for loco in cab.locos_by_id.values():
            if in_use:
                break
            dcc_id = loco.dcc_id
            for scab in self.cabs.values():
                if in_use:
                    break
                for cloco in scab.locos_by_id.values():
                    if dcc_id == cloco.dcc_id:
                        in_use = True
                        matching_cab = scab
                        break
        return in_use, matching_cab

    def __steal_cab(self, node_id, port_id, matching_cab):
        """ steal a cab, remove it from other throttle(s) """
        for throttle in self.throttles.values():
            if matching_cab.port_id in throttle.cabs:
                del throttle.cabs[matching_cab.port_id]
                io_data = IoData()
                io_data.mqtt_type = Global.CAB
                io_data.mqtt_node_id = node_id
                io_data.mqtt_port_id = port_id
                io_data.mqtt_metadata = {Global.CURRENT+"-"+Global.THROTTLE+"-"+Global.NODE_ID:throttle.node_id,
                    Global.ACQUIRE+"-"+Global.THROTTLE+"-"+Global.NODE_ID:node_id}
                io_data.reported = Global.STOLEN
                self.publish_cab_data_message(io_data)
        if port_id in self.cabs:
            del self.cabs[port_id]

    def __share_cab(self, node_id, port_id, matching_cab):
        """ steal a cab, remove it from other throtle(s) """
        for throttle in self.throttles.values():
            if matching_cab.port_id in throttle.cabs:
                io_data = IoData()
                io_data.mqtt_type = Global.CAB
                io_data.mqtt_node_id = node_id
                io_data.mqtt_port_id = port_id
                io_data.mqtt_metadata = {Global.CURRENT+"-"+Global.THROTTLE+"-"+Global.NODE_ID:throttle.node_id,
                        Global.ACQUIRE+"-"+Global.THROTTLE+"-"+Global.NODE_ID:node_id}
                io_data.reported = Global.SHARED
                self.publish_cab_data_message(io_data)

    def __assign_loco_regisers(self, cab):
        """ assign each loco a register """
        for loco in cab.locos_by_seq:
            loco.slot = self.dcc_assign_loco_to_slot(loco.dcc_id)

    def __acquire_cab(self, node_id, port_id, consist, steal_cab=False, share_cab=False):
        """ acquire a set of locos """
        reported = Global.ERROR
        message = ""
        if node_id not in self.throttles:
            message = Local.MSG_ERROR_THROTTLE_NOT_CONNECTED
        else:
            throttle = self.throttles[node_id]
            if port_id in throttle.cabs:
                message = Local.MSG_ERROR_CAB_ALREADY_ACQUIRED
            else:
                new_cab = MqttCab(port_id)
                new_cab.consist = consist
                reported, message = new_cab.initialize_cab()
                if reported != Global.ERROR:
                    cab_in_use, matching_cab = self.__is_cab_in_use(new_cab)
                    if (cab_in_use and (steal_cab or share_cab)):
                        locos_length = len(new_cab.locos_by_id)
                        if locos_length > self.dcc_get_slots_available():
                            reported = Global.ERROR
                            message = Local.MSG_ERROR_NO_SLOTS_AVAIL
                        else:
                            matching_cab_loco_length = len(matching_cab.locos_by_id)
                            if ((locos_length != 1) or(matching_cab_loco_length != 1)):
                                # can only steal/share a single loco, not a consist
                                reported = Global.ERROR
                                message = Local.MSG_ERROR_SINGLE_STEAL
                            elif steal_cab:
                                steal_cab(new_cab, matching_cab)
                            elif share_cab:
                                share_cab(new_cab, matching_cab)
                            elif cab_in_use:
                                reported = Global.BUSY
                    if reported not in (Global.ERROR, Global.BUSY):
                        self.__assign_loco_regisers(new_cab)
                        throttle.cabs[new_cab.port_id] = new_cab
                        if new_cab.port_id not in self.cabs:
                            self.cabs[new_cab.port_id] = new_cab
                        reported = Global.ACQUIRED
        return reported, message

    def __release_cab(self, node_id, port_id):
        """ release a set of locos """
        reported = Global.ERROR
        message = ""
        if node_id not in self.throttles:
            message = Local.MSG_ERROR_THROTTLE_NOT_CONNECTED
        else:
            throttle = self.throttles[node_id]
            if port_id not in throttle.cabs:
                message = Local.MSG_ERROR_CAB_NOT_ACQUIRED
            else:
                cab = throttle.cabs[port_id]
                reported, message = cab.release_cab(self)
                if reported != Global.ERROR:
                    del throttle.cabs[port_id]
                    cab_in_use = False
                    for throttle in self.throttles.values():
                        if cab in throttle.cabs:
                            cab_in_use = True
                            break
                    if not cab_in_use:
                        # cab not in use by any other throttle
                        del self.cabs[port_id]
                    reported = "release"
        return reported, message

    def __emergency_stop_loco(self, loco):
        """ issue emergency stop to a loco"""
        self.dcc_emergency_stop(loco.slot, loco.dcc_id)

    def __set_loco_speed(self, loco):
        """ set a locos speed and direction"""
        direction = loco.direction_is_reversed
        # some locos in consist may be facing the opposite of the lead loco
        # in that case,  reverse the dcc direction for these locos
        if not loco.is_direction_normal:
            direction = not direction
        return self.dcc_set_loco_speed(loco.slot, loco.dcc_id, loco.speed, direction)

    def __change_speed(self, _node_id, port_id, speed, direction):
        """ change speed for a list of locos in a cab """
        reported = Global.ERROR
        message = ""
        if port_id not in self.cabs:
            message = Local.MSG_ERROR_CAB_NOT_ACQUIRED
        else:
            cab = self.cabs[port_id]
            for loco in cab.locos_by_seq:
                if ((direction == Global.FORWARD) and
                    (loco.direction_is_reversed) and
                    (loco.speed > 0)):
                    # loco currently moving in opposite direction
                    self.__emergency_stop_loco(loco)
                elif ((direction == Global.REVERSE) and
                    (not loco.direction_is_reversed) and
                    (loco.speed > 0)):
                    # loco currently moving in opposite direction
                    self.__emergency_stop_loco(loco)
                loco.speed = speed
                if direction == Global.REVERSE:
                    loco.direction_is_reversed = True
                else:
                    loco.direction_is_reversed = False
                reported, message = self.__set_loco_speed(loco)
            reported = {Global.SPEED: speed, Global.DIRECTION: direction}
        return reported, message

    def __change_function(self, _node_id, port_id, function, action):
        """ change a function value for a list of locos in a cab """
        reported = Global.ERROR
        message = ""
        if port_id not in self.cabs:
            message = Local.MSG_ERROR_CAB_NOT_ACQUIRED
        else:
            func_num = int(function)
            if func_num not in range(0, 29): # f0 thri f28
                message = Local.MSG_ERROR_FUNC_NUM
            else:
                func_action = 11
                if action == Global.ON:
                    func_action = 1
                elif action == Global.OFF:
                    func_action = 0
                if func_action == -1:
                    message = Local.MSG_ERROR_FUNC_ACTION
                else:
                    cab = self.cabs[port_id]
                    for loco in cab.locos_by_seq:
                        if loco.apply_functions:
                            loco.functions[func_num] = func_action
                            self.dcc_set_loco_functions(loco.slot, loco.dcc_id, func_num, loco.functions)
                    reported = {Global.FUNCTION: function, Global.ACTION: action}
        return reported, message
