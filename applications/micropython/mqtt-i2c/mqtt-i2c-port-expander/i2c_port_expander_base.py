#!/usr/bin/python3
# # ic2_port_expander_base.py
"""

I2cPortExpanderBase - low level hardware driver fot a port expander connected to i2c
                         Pin number range from 1 - 16


The MIT License (MIT)

Copyright 2023 richard p hughes

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



import time

from global_constants import Global
from global_synonyms import Synonyms

from io_data import IoData
from utility import Utility
from io_device_data import IoDeviceData

class I2cPortExpanderBase():
    """ Class for an I2C connected relay controller device"""

    def __init__(self, io_device=None, node_name=None, pub_topics=None, logger=None):
        """ Initialize """
        self.io_device = io_device
        self.logger = logger
        self.node_name = node_name
        self.pub_topics = pub_topics
        self.sensor_topic = self.pub_topics.get(Global.SENSOR, Global.UNKNOWN)
        self.blink_pins = []
        for p in range(16):
            self.blink_pins.append(None)
        self.port_map = {}
        self.input_pin_port_map = {}
        self.input_pin_report_map = {}
        self.send_after_port_queue = {}  # ports that have active send after operations

    def initialize(self):
        """ initlaize class """
        #print(">>> init port_expander base")
        self.initialize_configured_devices()

    def perform_periodic_operation(self):
        """ perform operations that are not related to received messages """
        rett_messages = None
        current_ms = time.ticks_ms()
        for p in range(16):
            if self.blink_pins[p] is not None:
                (new_state, blink_rate, last_current_ms) = self.blink_pins[p]
                ops_time = last_current_ms + blink_rate
                if current_ms < last_current_ms:
                    # tick flipped over, adjust
                    ops_time = current_ms - 1
                if ops_time < current_ms:
                    # self.logger.log_line(">>> blink: "+str(ops_time)+" ... "+str(current_ms)+ " ... "+str(blink_rate))
                    self.send_pin_changes([(p, new_state, 0)])
                    next_state =  not new_state
                    self.blink_pins[p] = (next_state, blink_rate, current_ms)
        return self.read_input_messages()

    def process_response_message(self, new_message):
        """ a response message has been received """
        pass

    def process_request_message(self, new_message):
        """ a request message has been received """
        response = None
        self.logger.log_line("Req: " + str(new_message.mqtt_desired) + " : " + new_message.mqtt_port_id)
        sub_device = self.port_map.get(new_message.mqtt_port_id, None)
        if sub_device is not None:
            if response is None:
                response = []
            (return_reported, metadata, data_reported) = self.request_device_action(new_message)
            self.logger.log_line(" ... Res: "+str(return_reported))
            response.append((return_reported, metadata, data_reported, new_message))
        return response

    def process_data_message(self, new_message):
        pass

    def read_input(self):
        """ read changed pins on port expander """
        return None

    def read_input_messages(self):
        """ read input, generate messages for input """
        rett_messages = None
        changed_pins = self.read_input()
        if changed_pins is not None:
            #print(">>> changed_pins: "+str(changed_pins))
            rett_messages = []
            for (changed_pin, new_value) in changed_pins:
                report_value_map = self.input_pin_report_map.get(changed_pin, {})
                report_value = report_value_map.get(new_value, None)
                if report_value is not None:
                    pin_port = self.input_pin_port_map.get(changed_pin, None)
                    if pin_port is not None:
                        body = IoData()
                        body.mqtt_port_id = pin_port
                        body.mqtt_reported = report_value
                        body.mqtt_message_root = Global.SENSOR
                        body.mqtt_node_id = self.node_name
                        body.mqtt_version = "1.0"
                        body.mqtt_timestamp = Utility.now_milliseconds()
                        rett_messages.append((self.sensor_topic, body))
                        self.logger.log_line("Data: "+str(body.mqtt_reported)+" : "+str(body.mqtt_node_id))
        return rett_messages

    def request_device_action(self, message):
        """ send rquest to i2c device; message is an io_data instance"""
        return_reported = Global.ERROR
        return_message = "Unknown request: " + str(message.mqtt_desired)
        send_after = None
        if message.mqtt_message_root == Global.SWITCH:
            (return_reported, return_message, data_reported) = \
                self.send_request_to_switch(message)
        elif message.mqtt_message_root == Global.SIGNAL:
            (return_reported, return_message, data_reported) = \
                self.send_request_to_signal(message)
        return (return_reported, return_message, data_reported)

    def perform_other(self):
        """ perform periodic operations """
        pass

    def initialize_configured_devices(self):
        """ initialize the device """
        #print(">>> init a device")
        if self.io_device.io_sub_devices is not None:
            for (_key, sub_device) in self.io_device.io_sub_devices.items():
                self.logger.log_line("sub dev: " + str(sub_device))
                self.initialize_a_port(sub_device)
        self.logger.log_line("ports: "+str(self.port_map))

    def initialize_a_port(self, sub_device):
        #print(">>> init a port")
        # self.logger.log_line(">>> 0: " + str(type(sub_device)))
        self.logger.log_line("port type: " + str(sub_device.io_device_type))
        if sub_device.io_device_type == Global.SENSOR:
            self.initialize_a_sensor(sub_device)
        elif sub_device.io_device_type == Global.SWITCH:
            self.initialize_a_switch(sub_device)
        elif sub_device.io_device_type == Global.SIGNAL:
            self.initialize_a_signal(sub_device)
        else:
            self.log_warning(
                "Port Exander Config Error, Unknown device type: " +
                str(sub_device.io_device_type))

    def initialize_a_sensor(self, io_device):
        """ initialize the input pins for a sensor """
        in_pin = io_device.io_sub_address
        in_pin_report = {Global.ON: Global.ON, Global.OFF: Global.OFF}
        in_pin_active_low = True
        if io_device.io_metadata is not None:
            #self.logger.log_line(">>> metadata: "+str(io_device.io_metadata))
            in_pin_report = io_device.io_metadata.get(Global.REPORT, {
                Global.ON: Global.ON,
                Global.OFF: Global.OFF
            })
            active = io_device.io_metadata.get(Global.ACTIVE, Global.LOW)
            if active == Global.HIGH:
                in_pin_active_low = False
        self.logger.log_line("Init Sensor: " + str(in_pin))
        self.init_input_pin(in_pin, active_low=in_pin_active_low)
        self.input_pin_port_map.update({in_pin: io_device.mqtt_port_id})
        self.input_pin_report_map.update({in_pin: in_pin_report})

    def initialize_a_switch(self, io_device):
        """ initilaize the output pins for a switch """
        #print(">>> init a signal")
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
            # self.logger.log_line(">>> pins: "+str(base_pin) +" ... "+str(out_pin))
            self.init_output_pin(selected_pin, active_low=out_pin_active_low)
        # self.logger.log_line(">>> 1: " + str(io_device.mqtt_send_sensor_message))
        sub_dev = IoDeviceData()
        sub_dev.dev_type = Global.SWITCH
        sub_dev.dev_sub_type = switch_type
        sub_dev.base_pin = base_pin
        sub_dev.number_of_pins = number_of_pins
        sub_dev.send_sensor_message = io_device.mqtt_send_sensor_message
        sub_dev.pulse = pulse
        sub_dev.blink = blink
        sub_dev.state = Global.OFF
        self.port_map.update({io_device.mqtt_port_id: sub_dev})

    def initialize_a_signal(self, io_device):
        """ initialize the output pins for a signal """
        #print(">>> init a signal")
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
        self.logger.log_line("Init Signal: " + str(signal_type))
        if signal_type == Global.COLOR:
            number_of_pins = 3  # use 3 consecutive pins for the signal: green, yellow, red
        elif signal_type == Global.POSITION:
            # use 4 consecutive pins for the signal: clear, approach, stop, center light
            number_of_pins = 4
        for out_pin in range(0, number_of_pins):
            selected_pin = base_pin + out_pin
            #self.logger.log_line(">>> pins: "+str(base_pin) +" ... "+str(out_pin))
            self.init_output_pin(selected_pin, active_low=out_pin_active_low)
        sub_dev = IoDeviceData()
        sub_dev.dev_type = Global.SIGNAL
        sub_dev.dev_sub_type = signal_type
        sub_dev.base_pin = base_pin
        sub_dev.number_of_pins = number_of_pins
        sub_dev.send_sensor_message = io_device.mqtt_send_sensor_message
        sub_dev.pulse = pulse
        sub_dev.blink = blink
        sub_dev.state = Global.OFF
        self.port_map.update({io_device.mqtt_port_id: sub_dev})

    def send_request_to_signal(self, message):
        """ send a request to a signal """
        data_reported = None
        return_reported = Global.ERROR
        return_message = "Unknown request: " + str(message.mqtt_desired)
        send_after_message = None
        process_this_message = True
        data_reported = None
        return_message = "Unknown request: " + str(message.mqtt_desired)
        desired = message.mqtt_desired
        # self.logger.log_line(">>> "+str(desired))
        if desired in (Global.ON, Global.OFF, Global.CLEAR, Global.APPROACH,
                       Global.STOP):
            sub_dev = self.port_map.get(message.mqtt_port_id, None)
            if sub_dev is None:
                return_message = "Unknown Port ID: " + \
                    str(message.mqtt_port_id)
            else:
                blink_rate = sub_dev.blink
                signal_type = sub_dev.dev_sub_type
                # self.logger.log_line(">>> "+str(signal_type))
                selected_pins = []
                if signal_type == Global.SINGLE:
                    pin = sub_dev.base_pin
                    if desired == Global.OFF:
                        # turn off any blinking in place for this pin
                        self.blink_pins[pin] = None
                    elif blink_rate != 0:
                        # set up blinking for this pin
                        current_ms = time.ticks_ms()
                        self.blink_pins[pin] = (False, blink_rate, current_ms)
                    if process_this_message:
                        selected_pins = self.set_single_signal_pins(sub_dev, desired)
                elif signal_type in (Global.COLOR, Global.POSITION):
                    selected_pins = self.set_multi_signal_pins(
                        sub_dev, desired)
                self.send_pin_changes(selected_pins)
                if process_this_message:
                    return_reported = desired
                else:
                    return_reported = None
                return_message = None
        #self.logger.log_line(">>> 2: " + str(sub_dev.send_sensor_message))
        if return_reported is not None and \
                return_reported != Global.ERROR and \
                sub_dev.send_sensor_message:
            data_reported = return_reported
        return (return_reported, return_message, data_reported)


    def set_single_signal_pins(self, sub_dev, desired):
        """ set pins for a single lamp signal """
        # self.logger.log_line(">>> single_signal: "+str(sub_dev.base_pin)+" ... "+str(desired))
        pulse = sub_dev.pulse  # pulse pins on rather than continous
        signal_pins = []
        if desired == Global.ON:
            signal_pins.append((sub_dev.base_pin, True, pulse))
        else:
            signal_pins.append((sub_dev.base_pin, False, 0))
        return signal_pins

    def set_multi_signal_pins(self, sub_dev, desired):
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

    def send_request_to_switch(self, message):
        """ request a chnage to a switch """
        # self.logger.log_line(">>> switch request: " + str(message))
        data_reported = None
        return_reported = Global.ERROR
        return_message = "Unknown request: " + str(message.mqtt_desired)
        send_after_message = None
        sub_dev = self.port_map.get(message.mqtt_port_id, None)
        if sub_dev is None:
            return_message = "Unknown Port ID: " + \
            str(message.mqtt_port_id)
        else:
            desired = message.mqtt_desired
            if desired == Global.THROW:
                if sub_dev.state == Global.OFF:
                    desired = Global.ON
                else:
                    desired = Global.OFF
            if Synonyms.is_synonym_activate(message.mqtt_desired):
                desired = Global.ON
            elif Synonyms.is_synonym_deactivate(desired):
                desired = Global.OFF
            if desired in (Global.ON, Global.OFF):
                # pulse pins on rather than continous
                pulse = sub_dev.pulse
                selected_pins = []
                if desired == Global.ON:
                    #self.logger.log_line(">>> on: "+str(sub_dev))
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
                        #self.logger.log_line(">>> off: "+str(sub_dev))
                        # duplex switch, turn off before on
                        selected_pins.append((sub_dev.base_pin + 1, False, 0))
                        selected_pins.append((sub_dev.base_pin, True, pulse))
                    else:
                        # toggle switch
                        selected_pins.append((sub_dev.base_pin, False, 0))
                self.send_pin_changes(selected_pins)
                return_reported = Synonyms.desired_to_reported(desired)
                sub_dev.state = return_reported
                self.port_map.update({message.mqtt_port_id: sub_dev})
                return_message = None
        #self.logger.log_line(">>> 2: " + str(sub_dev.send_sensor_message))
        if return_reported != Global.ERROR and sub_dev.send_sensor_message:
            data_reported = return_reported
        if message.mqtt_respond_to is None:
            return_reported = None
            data_reported = None
        return (return_reported, return_message, data_reported)

    def init_output_pin(self, selected_pin, active_low=None):
        print(">>> Oops, init_output_pin method not overridden")
        pass

    def send_pin_changes(self, selected_pins):
        """ set pins on hardware device"""
        self.logger.log_line("Oops: send pin changes not overoaded in drived class")