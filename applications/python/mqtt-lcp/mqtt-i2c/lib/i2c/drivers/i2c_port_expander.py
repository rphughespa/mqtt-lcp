#!/usr/bin/python3
# # ic2_port_expander.py
"""

    I2cPortExpander.py - helper class to process i2c port expander devices


The MIT License (MIT)

Copyright 2021 richard p hughes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys

sys.path.append('../../lib')

import copy

from utils.global_constants import Global
from utils.global_synonyms import Synonyms
from structs.io_data import IoData

from structs.io_device_data import IoDeviceData
from processes.base_process import SendAfterMessage

from i2c.drivers.i2c_base_driver import I2cBaseDriver
from i2c.devices.i2c_port_expander_mcp23017 import I2cPortExpanderMcp23017
from i2c.devices.i2c_port_expander_relay16_qwiic import I2cPortExpanderRelay16Qwiic
from i2c.devices.i2c_port_expander_relay_attiny84 import I2cPortExpanderRelayAttiny84

class I2cPortExpander(I2cBaseDriver):
    """ Class for an I2C connected port expander device"""
    def __init__(self, io_devices=None, i2c_bus=None, log_queue=None):
        """ Initialize """
        self.io_devices = io_devices
        super().__init__(name="port expander",
                         i2c_address=self.io_devices.io_address,
                         i2c_bus=i2c_bus,
                         log_queue=log_queue)
        # print(">>> Port Expander Device: "+ str(self.io_devices.io_device))
        if self.io_devices.io_device == Global.PORT_EXPANDER_RELAY_16:
            self.device_driver = I2cPortExpanderRelay16Qwiic(
                i2c_address=self.io_devices.io_address,
                i2c_bus=i2c_bus,
                log_queue=log_queue)
        elif self.io_devices.io_device == Global.PORT_EXPANDER_RELAY_QUAD:
            self.device_driver = I2cPortExpanderRelayAttiny84(
                i2c_address=self.io_devices.io_address,
                i2c_bus=i2c_bus,
                log_queue=log_queue)
        else:
            self.device_driver = I2cPortExpanderMcp23017(
                i2c_address=self.io_devices.io_address,
                i2c_bus=i2c_bus,
                log_queue=log_queue)
        self.port_map = {}
        self.input_pin_map = {}
        self.input_pin_report_map = {}
        self.send_after_port_queue = {
        }  # ports that have active send after operations
        self.__initialize_device()


    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def read_input(self):
        """ read changed pins on port expander """
        changed_pins = self.device_driver.read_input()
        return_data = None
        if changed_pins is not None:
            #print(">>> ;;; "+str(changed_pins))
            self.log_debug("Pins Changed: " + str(changed_pins))
            return_data = []
            for (pin, on_off) in changed_pins:
                #print(">>> in pins: "+str(pin)+" ... "+str(on_off))
                pin_io_data = IoData()
                pin_io_data.mqtt_port_id = self.input_pin_map.get(
                    pin, Global.UNKNOWN)
                if pin_io_data.mqtt_port_id != Global.UNKNOWN:
                    pin_report = self.input_pin_report_map.get(
                        pin, {
                            Global.ON: Global.ON,
                            Global.OFF: Global.OFF
                        })
                    #print(">>> pin_report: "+str(pin_report))
                    pin_report_on = pin_report.get(Global.ON, None)
                    pin_report_off = pin_report.get(Global.OFF, None)
                    pin_io_data = IoData()
                    pin_io_data.mqtt_port_id = self.input_pin_map.get(
                        pin, Global.UNKNOWN)
                    if on_off and pin_report_on is not None:
                        # only publish on if reprt has an on valu
                        pin_io_data.mqtt_reported = pin_report_on
                        return_data.append(pin_io_data)
                    elif pin_report_off is not None:
                        # assume a "toggle", publish both on and off
                        pin_io_data.mqtt_reported = pin_report_off
                        return_data.append(pin_io_data)
        return return_data

    def request_device_action(self, message):
        """ send rquest to i2c device; message is an io_data instance"""
        return_reported = Global.ERROR
        return_message = "Unknown request: " + str(message.mqtt_desired)
        send_after = None
        if message.mqtt_message_root == Global.SWITCH:
            (return_reported, return_message, data_reported, send_after) = \
                self.__send_request_to_switch(message)
        elif message.mqtt_message_root == Global.SIGNAL:
            (return_reported, return_message, data_reported, send_after) = \
                self.__send_request_to_signal(message)
        return (return_reported, return_message, data_reported, send_after)

    def perform_other(self):
        """ perform periodic operations """
        pass

    #
    # private functions
    #

    def __initialize_device(self):
        """ initialize the device """
        if self.io_devices.io_sub_devices is not None:
            for (_key, sub_device) in self.io_devices.io_sub_devices.items():
                self.log_debug("sub dev: " + str(sub_device))
                self.__initialize_a_port(sub_device)

    def __initialize_a_port(self, sub_device):
        # print(">>> 0: " + str(type(sub_device)))
        self.log_debug("port type: " + str(sub_device.io_device_type))
        if sub_device.io_device_type == Global.SENSOR:
            self.__initialize_a_sensor(sub_device)
        elif sub_device.io_device_type == Global.SWITCH:
            self.__initialize_a_switch(sub_device)
        elif sub_device.io_device_type == Global.SIGNAL:
            self.__initialize_a_signal(sub_device)
        else:
            self.log_warning(
                "Port Exander Config Error, Unknown device type: " +
                str(sub_device.io_device_type))

    def __initialize_a_sensor(self, io_device):
        """ initialize the input pins for a sensor """
        in_pin = io_device.io_sub_address
        in_pin_report = {Global.ON: Global.ON, Global.OFF: Global.OFF}
        in_pin_active_low = True
        if io_device.io_metadata is not None:
            #print(">>> metadata: "+str(io_device.io_metadata))
            in_pin_report = io_device.io_metadata.get(Global.REPORT, {
                Global.ON: Global.ON,
                Global.OFF: Global.OFF
            })
            active = io_device.io_metadata.get(Global.ACTIVE, Global.LOW)
            if active == Global.HIGH:
                in_pin_active_low = False
        self.log_debug("Init Sensor: " + str(in_pin))
        self.device_driver.init_input_pin(in_pin, active_low=in_pin_active_low)
        self.input_pin_map.update({in_pin: io_device.mqtt_port_id})
        self.input_pin_report_map.update({in_pin: in_pin_report})

    def __initialize_a_switch(self, io_device):
        """ initilaize the output pins for a switch """
        base_pin = io_device.io_sub_address
        number_of_pins = 1  # use only 1 pin for the switch: an on/off toggle
        switch_type = Global.DUPLEX
        pulse = 0
        blink = 0
        out_pin_active_low = True
        if isinstance(io_device.io_metadata, dict):
            switch_type = io_device.io_metadata.get(Global.SWITCH_TYPE,
                                                    Global.TOGGLE)
            # when pin is set on, pulse the pin (in milliseconds) rather than continous on
            pulse = io_device.io_metadata.get(Global.PULSE, 0)
            blink = io_device.io_metadata.get(Global.BLINK, 0)
            active = io_device.io_metadata.get(Global.ACTIVE, Global.LOW)
            if active == Global.HIGH:
                out_pin_active_low = False
        if switch_type == Global.DUPLEX:
            # use 2 consecutive pins for the switch: close(off), throw(on)
            number_of_pins = 2
        for out_pin in range(0, number_of_pins):
            selected_pin = base_pin + out_pin
            # print(">>> pins: "+str(base_pin) +" ... "+str(out_pin))
            self.device_driver.init_output_pin(selected_pin,
                                               active_low=out_pin_active_low)
        # print(">>> 1: " + str(io_device.mqtt_send_sensor_message))
        sub_dev = IoDeviceData()
        sub_dev.dev_type = Global.SWITCH
        sub_dev.dev_sub_type = switch_type
        sub_dev.base_pin = base_pin
        sub_dev.number_of_pins = number_of_pins
        sub_dev.send_sensor_message = io_device.mqtt_send_sensor_message
        sub_dev.pulse = pulse
        sub_dev.blink = blink
        self.port_map.update({io_device.mqtt_port_id: sub_dev})

    def __initialize_a_signal(self, io_device):
        """ initialize the output pins for a signal """
        base_pin = io_device.io_sub_address
        number_of_pins = 1  # ue only 1 pin for the signal
        signal_type = Global.SINGLE
        pulse = 0
        blink = 0
        out_pin_active_low = True
        if isinstance(io_device.io_metadata, dict):
            signal_type = io_device.io_metadata.get(Global.SIGNAL_TYPE,
                                                    Global.SINGLE)
            # when pin is set on, pulse the pin (in) milliseconds) rather than continous on
            pulse = io_device.io_metadata.get(Global.PULSE, 0)
            blink = io_device.io_metadata.get(Global.BLINK, 0)
            active = io_device.io_metadata.get(Global.ACTIVE, Global.LOW)
            if active == Global.HIGH:
                out_pin_active_low = False
        self.log_debug("Init Signal: " + str(signal_type))
        if signal_type == Global.COLOR:
            number_of_pins = 3  # use 3 consecutive pins for the signal: green, yellow, red
        elif signal_type == Global.POSITION:
            # use 4 consecutive pins for the signal: clear, approach, stop, center light
            number_of_pins = 4
        for out_pin in range(0, number_of_pins):
            selected_pin = base_pin + out_pin
            #print(">>> pins: "+str(base_pin) +" ... "+str(out_pin))
            self.device_driver.init_output_pin(selected_pin,
                                               active_low=out_pin_active_low)
        sub_dev = IoDeviceData()
        sub_dev.dev_type = Global.SIGNAL
        sub_dev.dev_sub_type = signal_type
        sub_dev.base_pin = base_pin
        sub_dev.number_of_pins = number_of_pins
        sub_dev.send_sensor_message = io_device.mqtt_send_sensor_message
        sub_dev.pulse = pulse
        sub_dev.blink = blink
        self.port_map.update({io_device.mqtt_port_id: sub_dev})

    def __send_request_to_signal(self, message):
        data_reported = None
        return_reported = Global.ERROR
        return_message = "Unknown request: " + str(message.mqtt_desired)
        send_after_message = None
        process_this_message = True
        data_reported = None
        return_message = "Unknown request: " + str(message.mqtt_desired)
        desired = message.mqtt_desired
        # print(">>> "+str(desired))
        if desired in (Global.ON, Global.OFF, Global.CLEAR, Global.APPROACH,
                       Global.STOP):
            sub_dev = self.port_map.get(message.mqtt_port_id, None)
            if sub_dev is None:
                return_message = "Unknown Port ID: " + \
                    str(message.mqtt_port_id)
            else:
                blink = sub_dev.blink
                signal_type = sub_dev.dev_sub_type
                # print(">>> "+str(signal_type))
                selected_pins = []
                if signal_type == Global.SINGLE:
                    if blink != 0:
                        (process_this_message, send_after_message) = \
                            self.__create_signal_blink_send_after_message(
                                message, blink)
                    if process_this_message:
                        selected_pins = self.__set_single_signal_pins(
                            sub_dev, desired)
                elif signal_type in (Global.COLOR, Global.POSITION):
                    selected_pins = self.__set_multi_signal_pins(
                        sub_dev, desired)
                self.__send_pin_changes(selected_pins)
                if process_this_message and message.mqtt_respond_to != Global.BLINK:
                    return_reported = desired
                else:
                    return_reported = None
                return_message = None
        #print(">>> 2: " + str(sub_dev.send_sensor_message))
        if return_reported is not None and \
                return_reported != Global.ERROR and \
                sub_dev.send_sensor_message:
            data_reported = return_reported
        return (return_reported, return_message, data_reported,
                send_after_message)

    def __set_single_signal_pins(self, sub_dev, desired):
        """ set pins for a single lamp signal """
        # print(">>> single_signal: "+str(sub_dev.base_pin)+" ... "+str(desired))
        pulse = sub_dev.pulse  # pulse pins on rather than continous
        signal_pins = []
        if desired == Global.ON:
            signal_pins.append((sub_dev.base_pin, True, pulse))
        else:
            signal_pins.append((sub_dev.base_pin, False, 0))
        return signal_pins

    def __set_multi_signal_pins(self, sub_dev, desired):
        """ set pins for color or position multi lamp signal """
        signal_pins = []
        base_pin = sub_dev.base_pin
        number_of_pins = sub_dev.number_of_pins
        if desired == Global.OFF:
            for p in range(base_pin, base_pin + number_of_pins):
                signal_pins.append((p, False, 0))
        elif desired == Global.CLEAR:
            signal_pins.append((base_pin, True, 0))
            signal_pins.append((base_pin + 1, False, 0))
            signal_pins.append((base_pin + 2, False, 0))
            if number_of_pins == 4:
                # position light center lamp
                signal_pins.append((base_pin + 3, True, 0))
        elif desired == Global.APPROACH:
            signal_pins.append((base_pin, False, 0))
            signal_pins.append((base_pin + 1, True, 0))
            signal_pins.append((base_pin + 2, False, 0))
            if number_of_pins == 4:
                # position light center lamp
                signal_pins.append((base_pin + 3, True, 0))
        elif desired == Global.STOP:
            signal_pins.append((base_pin, False, 0))
            signal_pins.append((base_pin + 1, False, 0))
            signal_pins.append((base_pin + 2, True, 0))
            if number_of_pins == 4:
                # position light center lamp
                signal_pins.append((base_pin + 3, True, 0))
        return signal_pins

    def __send_request_to_switch(self, message):
        data_reported = None
        return_reported = Global.ERROR
        return_message = "Unknown request: " + str(message.mqtt_desired)
        send_after_message = None
        desired = message.mqtt_desired
        if Synonyms.in_synonym_activate(message.mqtt_desired):
            desired = Global.ON
        elif Synonyms.in_synonym_deactivate(desired):
            desired = Global.OFF
        if desired in (Global.ON, Global.OFF):
            sub_dev = self.port_map.get(message.mqtt_port_id, None)
            #print(">>> sub dev: " + str(sub_dev))
            if sub_dev is None:
                return_message = "Unknown Port ID: " + \
                    str(message.mqtt_port_id)
            else:
                # pulse pins on rather than continous
                pulse = sub_dev.pulse
                selected_pins = []
                if desired == Global.ON:
                    #print(">>> on: "+str(sub_dev))
                    if sub_dev.number_of_pins == 2:
                        # duplex switch, turn off before on
                        selected_pins.append((sub_dev.base_pin, False, 0))
                        selected_pins.append(
                            (sub_dev.base_pin + 1, True, pulse))
                    else:
                        # toggle switch
                        selected_pins.append((sub_dev.base_pin, True, pulse))
                else:
                    if sub_dev.number_of_pins == 2:
                        #print(">>> off: "+str(sub_dev))
                        # duplex switch, turn off before on
                        selected_pins.append((sub_dev.base_pin + 1, False, 0))
                        selected_pins.append((sub_dev.base_pin, True, pulse))
                    else:
                        # toggle switch
                        selected_pins.append((sub_dev.base_pin, False, 0))
                self.__send_pin_changes(selected_pins)
                return_reported = Synonyms.desired_to_reported(
                    message.mqtt_desired)
                return_message = None
        #print(">>> 2: " + str(sub_dev.send_sensor_message))
        if return_reported != Global.ERROR and sub_dev.send_sensor_message:
            data_reported = return_reported
        if message.mqtt_respond_to is None:
            return_reported = None
            data_reported = None
        return (return_reported, return_message, data_reported,
                send_after_message)

    def __send_pin_changes(self, selected_pins):
        """ send pin chnages to the device """
        # some pins groups may have mutually exclusive pins
        # set the "off" pins first
        #print(">>> set pins: "+str(selected_pins))
        for (set_pin, set_mode, set_pulse) in selected_pins:
            if not set_mode:
                #print(">>> "+str(set_pin)+" ... "+str(set_mode))
                self.device_driver.set_output_pin(set_pin, set_mode, set_pulse)
        # set the "on" pins next
        for (set_pin, set_mode, set_pulse) in selected_pins:
            if set_mode:
                #print(">>> "+str(set_pin)+" ... "+str(set_mode))
                self.device_driver.set_output_pin(set_pin, set_mode, set_pulse)

    def __create_signal_blink_send_after_message(self, message, blink):
        send_after_message = None
        desired = message.mqtt_desired
        port_id = message.mqtt_port_id
        process_this_message = False
        if message.mqtt_respond_to == Global.BLINK:
            # message is a blink, is port still allowed to blink
            if port_id in self.send_after_port_queue:
                # ok, allow the blink
                process_this_message = True
                send_after_message = self.__format_blink_message(
                    message, blink)
            else:
                process_this_message = False
                send_after_message = None
        else:
            process_this_message = True
            # message is not a blink message
            if desired == Global.ON:
                # add port to map to allow future blink messages
                self.send_after_port_queue[port_id] = port_id
                send_after_message = self.__format_blink_message(
                    message, blink)
            else:
                # remove port from map to stop furture blinks
                if self.send_after_port_queue.get(port_id, None) is not None:
                    del self.send_after_port_queue[port_id]
        return (process_this_message, send_after_message)

    def __format_blink_message(self, message, blink):
        send_after_desired = Global.ON
        if message.mqtt_desired == Global.ON:
            send_after_desired = Global.OFF
        blink_io_data = copy.deepcopy(message)
        blink_io_data.mqtt_desired = send_after_desired
        blink_io_data.mqtt_respond_to = Global.BLINK
        send_after_message = SendAfterMessage(Global.IO_REQUEST, blink_io_data,
                                              blink)
        return send_after_message
