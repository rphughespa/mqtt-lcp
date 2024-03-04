#!/usr/bin/env python
import time
import binascii
import serial
import serial.tools.list_ports
usb_vendor_id =  5840
usb_product_id = 1613

serial_dev = None

devs = serial.tools.list_ports.comports()
for dev in devs:
    print("Device: " + dev.device + ",  Name: " + \
                          dev.name + ",  Description: " + dev.description)
    if dev.vid is not None:
        print(" Vendor ID: " + str(dev.vid) + ", " +
                    hex(dev.vid) +
                    " Product ID: " + str(dev.pid) + ", " +
                    hex(dev.pid))
        if dev.vid == usb_vendor_id and dev.pid == usb_product_id:
            serial_dev = dev.device
            print("Found serial device: "+str(serial_dev))

ser = serial.Serial(
        port=serial_dev, #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)
counter=0
print("starting...\n")
ser.write(b'\x20')
ser.write(b'\x60')
cmd_buff =

while 1:
    # ser.write('Write counter: " + strcounter))
    x = ser.read()
    if x:
        cmd_buff += " " + str(binascii.hexlify(x))
        if x == b'\xff':
            print(cmd_buff+"\n")
            cmd_buff = ""
