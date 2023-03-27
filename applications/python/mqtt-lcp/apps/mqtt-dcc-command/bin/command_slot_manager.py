#!/usr/bin/python3
# command_slots.py
"""

    CommandSlotManager.py - Class representing a the dcc slots dict used by mqtt-dcc-command

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

sys.path.append('../lib')

# from structs.gui_message import GuiMessage
from utils.global_constants import Global

from command_loco import CommandLoco



class CommandSlotManager(object):
    """ Class representing a manager of slots of loco info used in command station"""
    # note: slot id's are one based, not zero based
    def __init__(self, slot_count=12, log_queue=None):
        self.log_queue = log_queue
        self.slot_count = slot_count
        self.slots = {}
        self.slots_by_dcc_id = {}
        self.slots_by_cab_id = {}  # lists of slot id's keyed by node/throtttle/cab ids
        self.__initialize_slots()

    def connect_throttle(self, gui_message):
        """ connect a new throttle """
        # a new throttle connection, clear out any old info from a prev connection
        self.disconnect_throttle(gui_message)
        gui_message.reported = Global.CONNECTED
        return gui_message

    def disconnect_throttle(self, gui_message):
        """ disconnect a throttle"""
        # release any loco used by this throttle
        throttle_locos = self.find_throttle_locos(self, gui_message)
        release_message = copy.deepcopy(gui_message)
        release_message.sub_command = Global.RELEASE
        for loco in throttle_locos:
            release_message.dcc_id = loco.dcc_id
            release_message.slot_id = loco.slot_id
            self.release_loco(release_message)
        gui_message.reported = Global.DISCONNECTED
        return gui_message

    def acquire_loco(self, req_gui_message):
        """ acquire a loco """
        gui_message = copy.deepcopy(req_gui_message)
        # print(">>> acquire loco: " + str(gui_message.dcc_id))

        node_id = gui_message.node_id
        throttle_id = gui_message.throttle_id
        cab_id = gui_message.cab_id
        slots_list = self.find_loco_slot(gui_message)
        #print(">>> slots list: " + str(slots_list))
        if slots_list:
            # dcc_id already in use
            (existing_slot, existing_slot_loco) = slots_list[0]
            # print(">>> acq: "+str(gui_message.dcc_id) + " " +str(existing_slot))
            if existing_slot is not None:
                #print(">>> existing loco: "  )
                if existing_slot_loco.throttle_id == throttle_id and \
                        existing_slot_loco.node_id == node_id and \
                        existing_slot_loco.cab_id == cab_id:
                    #print(">>> already owned by this throttle: ")
                    gui_message.slot_id = existing_slot
                    gui_message.reported = Global.ACQUIRED
                else:
                    #print(">>> steal needed: ")
                    # owned by another throttle
                    gui_message.slot_id = -1
                    gui_message.reported = Global.STEAL_NEEDED
        else:
            slot_id = self.assign_loco_to_slot(gui_message)
            self.__add_loco_to_cab(slot_id)
            if slot_id is None:
                gui_message.slot_id = -1
                gui_message.reported = Global.ERROR
                gui_message.mode = Global.FULL
            else:
                gui_message.slot_id = slot_id
                gui_message.reported = Global.ACQUIRED
        self.__log_cab_locos(gui_message)
        # print(">>> : " + str(gui_message))
        return gui_message

    def release_loco(self, gui_message):
        """ release a loco, remove from slot table """
        #print(">>> release loco: " + str(gui_message))
        slots_list = self.find_loco_slot(gui_message)
        if slots_list:
            (slot_id, _slot_loco) = slots_list[0]
            if slot_id is not None:
                #print(">>> Clear slot: " + str(slot_id))
                self.clear_a_slot(slot_id)
        self.__log_cab_locos(gui_message)
        gui_message.reported = Global.RELEASED
        return gui_message

    def get_slots_available(self):
        """ return count of unasigned register slots """
        available = 0
        for _slot_id, slot_loco in self.slots.items():
            if slot_loco is None:
                available += 1
        return available

    def set_lead(self, gui_message):
        """ set the lead loco in consist """
        self.__log_cab_locos(gui_message)
        cab_key = self.__build_cab_key(gui_message)
        cab_slot_list = self.slots_by_cab_id.get(cab_key, None)
        if cab_slot_list:
            if gui_message.dcc_id is not None:
                new_cab_slot_list = []
                old_cab = None
                for slot_id in cab_slot_list:
                    loco = self.slots.get(slot_id, None)
                    if loco is not None:
                        if loco.dcc_id == gui_message.dcc_id:
                            old_cab = loco
                        else:
                            new_cab_slot_list += [slot_id]
                if old_cab is not None:
                    new_cab_slot_list = [old_cab.slot_id] + new_cab_slot_list
                self.slots_by_cab_id[cab_key] = new_cab_slot_list
        self.__log_cab_locos(gui_message)

    def set_loco_speed(self, gui_message):
        """ set loco speed """
        slot_list = self.find_loco_slot(gui_message)
        if slot_list:
            for (_slot_id, slot_loco) in slot_list:
                if slot_loco is not None:
                    slot_loco.set_speed(gui_message.speed)

    def set_loco_direction(self, gui_message):
        """ set loco direction """
        slot_list = self.find_loco_slot(gui_message)
        if slot_list:
            old_lead_loco = self.get_lead_loco(slot_list)
            for (_slot_id, slot_loco) in slot_list:
                if slot_loco is not None:
                    slot_loco.set_direction(gui_message.direction)
            new_lead_loco = self.get_lead_loco(slot_list)
            if new_lead_loco.slot_id != old_lead_loco.slot_id:
                # move func setting for light, bell, horn
                for f in range(3):
                    new_lead_loco.function_states[f] = old_lead_loco.function_states[f]
                    old_lead_loco.function_states[f] = 0

    def set_loco_function(self, gui_message):
        """ set loco function """
        slot_list = self.find_loco_slot(gui_message)
        if slot_list:
            if gui_message.function < 3:   # light, bell, horn only apply to consist lead
                lead_loco = self.get_lead_loco(slot_list)
                lead_loco.set_function(gui_message.function, gui_message.mode)
            else:
                for (_slot_id, slot_loco) in slot_list:
                    if slot_loco is not None:
                        slot_loco.set_function(gui_message.function, gui_message.mode)

    def assign_loco_to_slot(self, gui_message, existing_slot_id=None):
        """ asssign a register slot to a loco """
        rett = None
        first_avail = None
        if existing_slot_id is not None:
            first_avail= existing_slot_id
        else:
            for slot_id, slot_loco in self.slots.items():
                if slot_loco is None:
                    first_avail = slot_id
                    break
       # print(">>> first avail: " + str(first_avail))
        if first_avail is not None:
            # assign loco to first avail slot
            rett = first_avail
            slot_loco = CommandLoco.parse_gui_message(gui_message)
            slot_loco.slot_id = rett
            self.slots[rett] = slot_loco
            # self.add_to_slots_by_cab_id(slot_loco)
        self.__rebuild_slots_by_dcc_id()
        self.__rebuild_slots_by_cab_id()
        # print(">>> rett slot: " + str(rett))
        return rett

    def clear_a_slot(self, slot_id):
        """ clear out a register slot, make it available for reuse"""
        if 1 <= slot_id <= self.slot_count:
            self.slots[slot_id] = None
        self.__rebuild_slots_by_dcc_id()
        self.__rebuild_slots_by_cab_id()
        #print(">>> clear a slot: [" + str(slot_id) + "] " + str(self.slots))
        return slot_id

    def find_loco_slot(self, gui_message):
        """ find the assigned slot number of a loco by its dcc_id or cab_key """
        rett = []
        if gui_message.dcc_id is not None:
            slot_id = self.slots_by_dcc_id.get(gui_message.dcc_id, None)
            if slot_id is not None:
                rett = [(slot_id, self.slots[slot_id])]
        else:
            cab_key = self.__build_cab_key(gui_message)
            cab_slot_list = self.slots_by_cab_id.get(cab_key, None)
            if cab_slot_list:
                for slot_id in cab_slot_list:
                    rett += [(slot_id, self.slots[slot_id])]
        return rett

    def clear_all_throttle_locos(self, node_id, throttle_id):
        """ clear out slot table loco for a given throttle id """
        for slot_id, slot_loco in self.slots.items():
            if slot_loco is not None and \
                    slot_loco.node_id == node_id and \
                    slot_loco.throttle_id == throttle_id:
                self.slots[slot_id] = None
        self.__rebuild_slots_by_dcc_id()
        self.__rebuild_slots_by_cab_id()

    def find_throttle_locos(self, node_id, throttle_id):
        """ get a list of slot locos associated with this throttle """
        rett = []
        for _slot_id, slot_loco in self.slots.items():
            if slot_loco is not None and \
                    slot_loco.node_id == node_id and \
                    slot_loco.throttle_id == throttle_id:
                rett.append(copy.deepcopy(slot_loco))
        return rett

    def add_to_slots_by_cab_id(self, command_loco):
        """ add a new slot to a cab """
        print("add slot:" + str(command_loco.dcc_id) + " ... " + str(command_loco.slot_id))
        cab_key = self.__build_cab_key(command_loco)
        cab_slot_list = self.slots_by_cab_id.get(cab_key, None)
        if cab_slot_list is None:
            # create new list
            self.slots_by_cab_id[cab_key] = [command_loco.slot_id]
        else:
            # append to existing list
            self.slots_by_cab_id[cab_key] += [command_loco.slot_id]

    def get_lead_loco(self, slot_list):
        """ find the lead loco in a cab """
        (_slot_id, lead_loco) = slot_list[0]
        if (lead_loco.current_direction == Global.REVERSE and lead_loco.is_direction_normal is True) or \
                (lead_loco.current_direction == Global.FORWARD and lead_loco.is_direction_normal is False):
            # consist is reversed, lead is last loco
            (_slot_id, lead_loco) = slot_list[-1]
        return lead_loco

    #
    # private functions
    #

    def __initialize_slots(self):
        """ initialize the register slots """
        for slot in range(1, \
                self.slot_count + 1):  # slot 0 is for programming, don't use it
            self.slots[slot] = None

    def __build_cab_key(self, command_loco):
        """ build the key for a loco list for a cab """
        return command_loco.node_id + ":" + \
                command_loco.throttle_id + ":" + \
                command_loco.cab_id

    def __add_loco_to_cab(self, slot_id):
        """ append a slot_id of a loco to the cabs loco list """
        slot_loco = self.slots.get(slot_id, None)
        if slot_loco is not None:
            cab_key = self.__build_cab_key(slot_loco)
            if cab_key is not None:
                cab_loco_list = self.slots_by_cab_id.get(cab_key, [])
                cab_loco_list += [slot_id]
                self.slots_by_cab_id[cab_key] = cab_loco_list

#    def __remove_loco_from_cab(self, slot_id):
#        """ remove a slot_id of a loco from the cabs loco list """
#        slot_loco = self.slots.get(slot_id, None)
#        if slot_loco is not None:
#            cab_key = self.__build_cab_key(slot_loco)
#            if cab_key is not None:
#                new_cab_loco_list = []
#                for cab_slot_id in self.slots_by_cab_id.get(cab_key, []):
#                    if cab_slot_id != slot_id:
#                        new_cab_loco_list += [cab_slot_id]
#                self.slots_by_cab_id[cab_key] = new_cab_loco_list

    def __rebuild_slots_by_dcc_id(self):
        """ rebuild slots by dcc_id to remove slots no longer in use"""
        self.slots_by_dcc_id = {}
        for slot_id, slot_loco in self.slots.items():
            if slot_loco is not None:
                self.slots_by_dcc_id[slot_loco.dcc_id] = slot_id
        # print(">>> slots by ID: " + str(self.slots_by_dcc_id))

    def __rebuild_slots_by_cab_id(self):
        """ rebuild slots by cab_id, removing locos no longer in use """
        cab_key_list = []
        for cab_key in self.slots_by_cab_id:
            cab_key_list.append(cab_key)
        for cab_key in cab_key_list:
            cab_slot_list = self.slots_by_cab_id[cab_key]
            new_cab_slot_list = []
            for slot_id in cab_slot_list:
                slot = self.slots.get(slot_id, None)
                if slot is not None:
                    new_cab_slot_list += [slot_id]
            if new_cab_slot_list:
                self.slots_by_cab_id[cab_key] = new_cab_slot_list
            else:
                # no locos for cab, delete cab list
                del self.slots_by_cab_id[cab_key]
        # print(">>> slots by ID: " + str(self.slots_by_dcc_id))

    def __log_cab_locos(self, gui_message):
        """ log locos in a cab """
        message = "Cab Locos: "
        message += gui_message.node_id + " "
        message += gui_message.throttle_id + " "
        message += gui_message.cab_id + " [ "
        cab_key = self.__build_cab_key(gui_message)
        cab_loco_slots = self.slots_by_cab_id.get(cab_key, [])
        for loco_slot in cab_loco_slots:
            loco = self.slots.get(loco_slot, None)
            if loco is not None:
                message += str(loco.dcc_id) + " "
        message += "]"
        self.__log_info(message)

    def __log_info(self, message):
        """ send a info log entry to log process """
        self.log_queue.put(
                (Global.LOG_LEVEL_INFO, "slot manager: " + message))
