#!/usr/bin/python3
# cab_signals_manager.py
"""

CabSignalsManager - manages cab signals

the MIT License (MIT)

Copyright © 2021 richard p hughes

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

import sys
import copy

sys.path.append('../../lib')

from utils.global_constants import Global
from utils.compass_points import CompassPoints
from structs.io_data import IoData

class LocoCabSignal(object):
    """ data about loco cab signal """

    def __init__(self):
        """ initialize"""
        self.loco_id  = None
        self.block_direction = None # north/east/south/west
        self.block_id = None
        self.throttle_direction = None  # forward/reverse
        self.signal_key = None
        self.signal_aspect = None

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

class CabSignalsManager(object):
    """ tower data shared by multiple processes """

    def __init__(self, parent):
        """ initialize """
        self.parent = parent
        self.block_signals = {}
        self.loco_cab_signals = {}

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def inventory_has_changed(self):
        """ inventory has been updated, rebuild some tables """
        self.__rebuild_block_signals()


    def update_signals(self, message_root, state_data):
        """ process output message """
        if message_root == Global.LOCATOR:
            self.__process_locator_message(copy.deepcopy(state_data))
        if message_root == Global.SIGNAL:
            self.__process_signal_message(copy.deepcopy(state_data))
        if message_root == Global.CAB:
            self.__process_cab_message(copy.deepcopy(state_data))


#
# private functions
#
    def __rebuild_block_signals(self):
        """ create a block signal for each signal inventory """
        self.block_signals = {}
        inv_groups = self.parent.inventory.inventory_groups
        if inv_groups is not None:
            signals = inv_groups.get(Global.SIGNAL, None)
            if signals is not None:
                for _key, s in signals.inventory_items.items():
                    #print(">>> signal: "+(s.key) + " : " + str(s.block_id)+" : "+str(s.direction))
                    block_key = str(s.block_id)+":"+str(s.direction)
                    self.block_signals.update({block_key: s.key})

    def __process_cab_message(self, sensor_data):
        """ a cab message has been received """
        # print(">>> cab: "+str(sensor_data.loco_id)+" : "+\
        #        str(sensor_data.port_id) + " : "+str(sensor_data.direction)+ \
        #        str(sensor_data.reported))
        if sensor_data.loco_id is not None and \
                sensor_data.reported is not None and \
                sensor_data.port_id == Global.DIRECTION:
            # a message for dcc command indicating a chnage if directio of a loco
            loco_id = sensor_data.loco_id
            if loco_id is not None and \
                    isinstance(loco_id, list):
                loco_id = loco_id[0]
            direction = sensor_data.reported
            if direction  is None:
                direction = Global.FORWARD
            current_loco_cab_signal = self.loco_cab_signals.get(loco_id, None)
            if current_loco_cab_signal is None:
                new_loco_cab_signal = LocoCabSignal()
                new_loco_cab_signal.loco_id = loco_id
                new_loco_cab_signal.throttle_direction = direction
                self.loco_cab_signals.update({new_loco_cab_signal.loco_id: new_loco_cab_signal})
                self.__update_cab_signal_key(new_loco_cab_signal.loco_id)
                self.__cab_signal_changed(new_loco_cab_signal.loco_id)
            else:
                current_loco_cab_signal.throttle_direction = direction
                self.__update_cab_signal_key(current_loco_cab_signal.loco_id)
                self.__cab_signal_changed(current_loco_cab_signal.loco_id)

    def __process_locator_message(self, sensor_data):
        """ process a locator message """
        loco_changed = []
        # print(">>> locator: "+str(sensor_data.loco_id) +" : " + \
        #        str(sensor_data.block_id)+" : "+str(sensor_data.reported))
        if sensor_data.loco_id is not None and \
                sensor_data.block_id is not None:
            locos = sensor_data.loco_id
            if locos is None:
                locos = []
            elif isinstance(locos, int):
                locos = [locos]
            for loco_id in locos:
                current_loco_cab_signal = self.loco_cab_signals.get(loco_id, None)
                if current_loco_cab_signal is None and \
                        sensor_data.reported == Global.ENTERED:
                    # loco not in map, and sensor is "entered" add it
                    new_loco_cab_signal = LocoCabSignal()
                    new_loco_cab_signal.loco_id = loco_id
                    new_loco_cab_signal.block_id = sensor_data.block_id
                    new_loco_cab_signal.block_direction = sensor_data.direction
                    self.loco_cab_signals.update({new_loco_cab_signal.loco_id: new_loco_cab_signal})
                    loco_changed.append(new_loco_cab_signal.loco_id)
                else:
                    # loco is in map, update it
                    if sensor_data.reported == Global.EXITED:
                        if current_loco_cab_signal.block_id == sensor_data.block_id:
                            # loco reported exited from block. clear out info
                            new_loco_cab_signal = LocoCabSignal()
                            new_loco_cab_signal.loco_id = loco_id
                            self.loco_cab_signals.update(\
                                    {new_loco_cab_signal.loco_id: new_loco_cab_signal})
                    elif sensor_data.reported == Global.ENTERED:
                        current_loco_cab_signal.block_id = sensor_data.block_id
                        current_loco_cab_signal.block_direction = sensor_data.direction
                        loco_changed.append(current_loco_cab_signal.loco_id)
        for loco_id in loco_changed:
            # print(">> loco changed: "+str(loco_id))
            self.__update_cab_signal_key(loco_id)
            self.__cab_signal_changed(loco_id)


    def __process_signal_message(self, sensor_data):
        """ process a signal message """
        for loco_id, loco_cab_signal in  self.loco_cab_signals.items():
            if loco_cab_signal.signal_key == sensor_data.key and \
                    loco_cab_signal.signal_aspect != sensor_data.reported:
                self.__cab_signal_changed(loco_id)

    def  __cab_signal_changed(self, loco_id):
        """ info about a cab signal has changed, update signal aspect """
        loco_cab_signal = self.loco_cab_signals.get(loco_id, None)
        # print(">>> loco cab signal: "+str(loco_cab_signal))
        if loco_cab_signal is not None:
            if loco_cab_signal.signal_key is not None:
                inventory_groups = self.parent.inventory.inventory_groups
                if inventory_groups is not None:
                    # print(">>> state groups: "+str(state_groups))
                    signals_group = inventory_groups.get(Global.SIGNAL, None)
                    if signals_group is not None:
                        signals = signals_group.inventory_items
                        # print(">>> state group: "+str(signals.keys()))
                        signal = signals.get(loco_cab_signal.signal_key, None)
                        if signal is not None:
                            # if signal.reported != loco_cab_signal.signal_aspect:
                            loco_cab_signal.signal_aspect = signal.reported
                            # change in aspect, pubish cab signal
                            self.__publish_cab_signal_changed(loco_cab_signal)

    def __update_cab_signal_key(self, loco_id):
        """ update cab signal key for a loco"""
        loco_cab_signal = self.loco_cab_signals.get(loco_id, None)
        if loco_cab_signal is not None:
            if loco_cab_signal.block_id is not None and \
                loco_cab_signal.block_direction is not None:
                #pri
                # nt(">>> dir: "+str(loco_cab_signal.block_direction)+\
                #   " : "+str(loco_cab_signal.throttle_direction))
                direction = loco_cab_signal.block_direction
                if loco_cab_signal.throttle_direction == Global.REVERSE:
                    direction = CompassPoints.reverse_direction(direction)
                block_signal_key = str(loco_cab_signal.block_id) + \
                        ":" + str(direction)
                # signal_key = self.block_signals.get(block_signal_key, None)
                #print(">>> bloc signal: " +str(block_signal_key) +" : "+str(signal_key))
                loco_cab_signal.signal_key = self.block_signals.get(block_signal_key)



    def __publish_cab_signal_changed(self, loco_cab_signal):
        """ send a data message notifing a cab signal changed """
        self.parent.log_info("Publish Cab Signal Changed Data: "+\
                             str(loco_cab_signal.loco_id) + " : "+\
                             str(loco_cab_signal.signal_key) + " : " +\
                             str(loco_cab_signal.signal_aspect))
        topic = self.parent.mqtt_config.publish_topics.get(Global.CAB_SIGNAL,
                                                    Global.UNKNOWN)
        # print(">>> topic: "+str(topic))
        data_msg_body = IoData()
        data_msg_body.mqtt_message_root = Global.TOWER
        data_msg_body.mqtt_node_id = self.parent.get_topic_node_id(topic)
        data_msg_body.mqtt_port_id = Global.CAB_SIGNAL
        data_msg_body.mqtt_loco_id = loco_cab_signal.loco_id
        data_msg_body.mqtt_reported = loco_cab_signal.signal_aspect
        self.parent.app_queue.put((Global.PUBLISH, {Global.TYPE: Global.DATA,
                                             Global.TOPIC: topic,
                                             Global.BODY: data_msg_body}))
