#!/usr/bin/python3
# command_throttle_cabs.py
"""

    CommandThrottleCabs.py - Class for mapping MQTT node/throttle/cab data to withrottle throttle/cab
        data.

        This class is used to map the mqtt data to withrottle data.  Each mqtt node/throttle/cab
        combination is mapped to a unique withrottle throttle/cab.

        This mapping is a workaround for the limitations of the Digitrax LNW1 withrottle server.
        This withrottle server has a design limit of a maximun of four throttle connection
        and a total of 32 locos.  The mapping in this class allows any combination of up to
        32 throttle, 1 loco each thru 1 throttle with 32 locos or any combination in between.

the MIT License (MIT)

Copyright © 2023 richard p hughes

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

sys.path.append('../lib')

# from structs.gui_message import GuiMessage

# from utils.global_constants import Global



class CommandWithrottleCab():
    """ Class representing a withrottle cab / mqtt mapping """
    def __init__(self, wi_throttle, wi_cab):
        self.wi_throttle = wi_throttle
        self.wi_cab = wi_cab
        self.mqtt_node_id = None
        self.mqtt_throttle_id = None
        self.mqtt_cab_id = None

    def __repr__(self):
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def clear_mqtt_throttle_data(self):
        """ clear out mqtt throttle data """
        self.mqtt_node_id = None
        self.mqtt_throttle_id = None
        self.mqtt_cab_id = None

    def set_mqtt_throttle_data(self, gui_message):
        """ save mqtt throttle data """
        self.mqtt_node_id = gui_message.node_id
        self.mqtt_throttle_id = gui_message.throttle_id
        self.mqtt_cab_id = gui_message.cab_id

class CommandMappingManager(object):
    """ Class representing a manager of throttle mappings: withrottle throttle/cab <-> mqtt node/throttle/cab"""

    def __init__(self, log_queue=None):
        self.log_queue = log_queue
        self.throttle_mappings = {}
        self.throttle_maps_by_mqtt_key = {}
        self.__initialize_mapping()

    def translate_wi_to_mqtt_cab(self, gui_message):
        """ translate a withrottle throttle/cab to the matching mqtt node/throttle/cab """
        rett = copy.deepcopy(gui_message)
        wi_map_key = self.__build_wi_map_key(gui_message.throttle_id, gui_message.cab_id)
        map_cab = self.throttle_mappings.get(wi_map_key, None)
        if map_cab is not None:
            rett.node_id = map_cab.mqtt_node_id
            rett.throttle_id = map_cab.mqtt_throttle_id
            rett.cab_id = map_cab.mqtt_cab_id
        return rett


    def translate_mqtt_to_wi_cab(self, gui_message):
        """ translate an mqtt node/throttle/cab to the matching  withrottle throttle/cab """
        rett = copy.deepcopy(gui_message)
        mqtt_map_key = \
                self.__build_mqtt_map_key(gui_message.node_id, \
                        gui_message.throttle_id, gui_message.cab_id)
        #print(">>> map cab 0: " +str(gui_message))
        map_cab = None
        map_key = self.throttle_maps_by_mqtt_key.get(mqtt_map_key, None)
        if map_key is not None:
            map_cab = self.throttle_mappings.get(map_key,None)
        #print(">>> map cab 1: " +str(map_cab))
        if map_cab is None:
            # mapping does not exist, create it
            map_cab = self.__add_mapping(gui_message)
        #print(">>> map cab 2: " +str(map_cab))
        if map_cab is not None:
            rett.node_id = None
            rett.throttle_id = map_cab.wi_throttle
            rett.cab_id = map_cab.wi_cab
        return rett

    def clear_mqtt_throttle(self, gui_message):
        """ remove mapping for a given mqtt throttle """
        for mapping in self.throttle_mappings.values():
            if  mapping.mqtt_node_id == gui_message.node_id and \
                    mapping.mqtt_throttle_id == gui_message.throttle_id:
                # clear mapping
                mapping.mqtt_node_id = None
                mapping.mqtt_throttle_id = None
                mapping.mqtt_cab_id = None
        self.__rebuild_maps_by_mqtt()

    #
    # private functions
    #

    def __initialize_mapping(self):
        self.throttle_mappings = {}
        # create 8 cabs for each of 4 throttles
        for c in range(8):
            cab_id = str(c+1) # adjust zero base to ones base
            for t in range(4):
                throttle_id = "withrottle" + str(t+1) # adjust zero base to ones base
                new_cab_map = CommandWithrottleCab(throttle_id, cab_id)
                wi_key = self.__build_wi_map_key(throttle_id, cab_id)
                self.throttle_mappings[wi_key] = new_cab_map
                # print(">>> cab mapping: " + str(wi_key) + " ... " + str(new_cab_map))

    def __build_wi_map_key(self, throttle_id, cab_id):
        """ build a key for the wi side mapping """
        return str(cab_id) + ":" + str(throttle_id)

    def __build_mqtt_map_key(self, node_id, throttle_id, cab_id):
        """ build a key for the mqtt side mapping """
        return str(node_id) + ":" + str(throttle_id) + ":" + str(cab_id)

    def __add_mapping(self, gui_message):
        """ find an used mapping and update for a given mqtt throttle """
        rett = None
        #  print(">>> sorted map keys: " + str(sorted(self.throttle_mappings)))
        for map_key in sorted(self.throttle_mappings):
            mapping = self.throttle_mappings[map_key]
            if mapping.mqtt_node_id is None and \
                    mapping.mqtt_throttle_id is None and \
                    mapping.mqtt_cab_id is None:
                # found an unused mapping
                mapping.mqtt_node_id = gui_message.node_id
                mapping.mqtt_throttle_id = gui_message.throttle_id
                mapping.mqtt_cab_id = gui_message.cab_id
                rett = mapping
                # print(">>> new mapping: " +str(mapping))
                break
        if rett is not None:
            self.__rebuild_maps_by_mqtt()
        return rett

    def __rebuild_maps_by_mqtt(self):
        """ rebuild key after mapping have changed """
        self.throttle_maps_by_mqtt_key = {}
        for map_key, mapping in self.throttle_mappings.items():
            if mapping.mqtt_node_id is None or \
                    mapping.mqtt_throttle_id is not None or \
                    mapping.mqtt_cab_id is not None:
                new_mqtt_key = self.__build_mqtt_map_key(mapping.mqtt_node_id, \
                        mapping.mqtt_throttle_id, mapping.mqtt_cab_id)
                self.throttle_maps_by_mqtt_key[new_mqtt_key] = map_key

#    def __log_error(self, message):
#        """ send a error log entry to log process """
#        self.log_queue.put(
#                (Global.LOG_LEVEL_ERROR, "withrottle map manager: " + message))
