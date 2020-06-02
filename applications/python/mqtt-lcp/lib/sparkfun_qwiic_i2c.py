# sparkfun_qwiic_i2c.py - modified version of sparkfun i2c
#
#   sparkfun_qwiic_i2c - slightly modified version of SparkFun i2c
#       changed to use smbus class .
#
#

#-----------------------------------------------------------------------------
# linux_i2c.py
#
# Encapsulate the Linux Plaform bus interface
#------------------------------------------------------------------------
#
# Written by  SparkFun Electronics, May 2019
#
# This python library supports the SparkFun Electroncis qwiic
# qwiic sensor/board ecosystem on a Raspberry Pi (and compatable) single
# board computers.
#
# More information on qwiic is at https://www.sparkfun.com/qwiic
#
# Do you like this library? Help support SparkFun. Buy a board!
#
#==================================================================================
# Copyright (c) 2019 SparkFun Electronics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#==================================================================================


import sys
if sys.platform.startswith("esp32"):
    from smbus2_esp32 import SMBus
else:
    from smbus2 import SMBus

_retry_count = 3
#-----------------------------------------------------------------------------
# Internal function to connect to the systems I2C bus.
#
# Attempts to fail elegantly - often an issue with permissions with the I2C
# bus. Users of this system should be added to the system i2c group
#

# notes on determining Linux platform
#
# - sys.platform == 'linux' or 'linux2', os.uname ->> res.sysname or res[0]=='Linux'
#   ## Means it's a linux system - and we support it
#
# To find out a particular system:
#
#   - Need to start looking at particular hardware classes in /proc/cpuinfo
#
class SparkfunQwiicI2c(object):

    def __init__(self, log_queue, bus_number):

        # Call the super class. The super calss will use default values if not
        # proviced
        self._i2c_msg = None
        self.log_queue = log_queue
        self.i2c_bus_number = bus_number

    def _connectToI2CBus(self):
        daBus = None
        error=False
        # Connect - catch errors
        try:
            daBus =  smbus2.SMBus(self.i2c_bus_number)
        except Exception as ee:
            if(type(ee) is IOError and ee.errno == 13):
                self.log_queue.add_message("error", "Error:\tUnable to connect to I2C bus %d: Permission denied.\n\tVerify you have permissoin to access the I2C bus" % (iBus), file=sys.stderr)
            else:
                self.log_queue.add_message("error","Error:\tFailed to connect to I2C bus %d. Error: %s" % (iBus, str(ee)), file=sys.stderr)

            # We had an error....
            error=True
        # below is probably not needed, but ...
        if(not error and daBus == None):
            print("Error: Failed to connect to I2C bus %d" % (iBus), file=sys.stderr)
        return daBus

#-------------------------------------------------------------------------
    # read Data Command

    def readWord(self, address, commandCode):

        data = 0

        # add some error handling and recovery....
        with SMBus(self.i2c_bus_number) as bus:
            for i in range(_retry_count):
                try:
                    data = bus.read_word_data(address, commandCode)

                    break # break if try succeeds

                except IOError as ioErr:
                    # we had an error - let's try again
                    if i == _retry_count-1:
                        raise ioErr
                    pass

        return data

    def readByte(self, address, commandCode = None):
        data = 0
        with SMBus(self.i2c_bus_number) as bus:
            for i in range(_retry_count):
                try:
                    if commandCode == None:
                        data = buss.read_byte(address)
                    elif commandCode != None:
                        data = bus.read_byte_data(address, commandCode)

                    break # break if try succeeds

                except IOError as ioErr:
                    # we had an error - let's try again
                    if i == _retry_count-1:
                        raise ioErr
                    pass

        return data


    def readBlock(self, address, commandCode, nBytes):
        data = 0
        with SMBus(self.i2c_bus_number) as bus:
            for i in range(_retry_count):
                try:
                    data = bus.read_i2c_block_data(address, commandCode, nBytes)

                    break # break if try succeeds

                except IOError as ioErr:
                    # we had an error - let's try again
                    if i == _retry_count-1:
                        raise ioErr
                    pass

            return data

    #--------------------------------------------------------------------------
    # write Data Commands
    #
    # Send a command to the I2C bus for this device.
    #
    # value = 16 bits of valid data..
    #

    def writeCommand(self, address, commandCode):
        ret = None
        with SMBus(self.i2c_bus_number) as bus:
            ret =  bus.write_byte(address, commandCode)
        return ret

    def writeWord(self, address, commandCode, value):
        ret = None
        with SMBus(self.i2c_bus_number) as bus:
            ret = bus.write_word_data(address, commandCode, value)
        return ret


    def writeByte(self, address, commandCode, value):
        ret = None
        with SMBus(self.i2c_bus_number) as bus:
            ret =  bus.write_byte_data(address, commandCode, value)
        return ret

    def writeBlock(self, address, commandCode, value):
        with SMBus(self.i2c_bus_number) as bus:
            # if value is a bytearray - convert to list of ints (it's what
            # required by this call)
            tmpVal = list(value) if type(value) == bytearray else value
            self.i2cbus.write_i2c_block_data(address, commandCode, tmpVal)

    #-----------------------------------------------------------------------
    # scan()
    #
    # Scans the I2C bus and returns a list of addresses that have a devices connected
    #

    def scan(self):
        """ Returns a list of addresses for the devices connected to the I2C bus."""

        # The plan - loop through the I2C address space and read a byte. If an
        # OSError occures, a device isn't at that address.


        foundDevices = []

        # Loop over the address space - which is 7 bits (0-127 range)
        with SMBus(self.i2c_bus_number) as bus:
            for currAddress in range(0, 128):
                try:
                    bus.read_byte(currAddress)
                except Exception:
                    continue
                foundDevices.append(currAddress)
        return foundDevices

    #-----------------------------------------------------------------------
    # Custom method for reading +8-bit register using `i2c_msg` from `smbus2`
    #
    def __i2c_rdwr__(self, address, write_message, read_nbytes):
        """
        Custom method used for 16-bit (or greater) register reads
        :param address: 7-bit address
        :param write_message: list with register(s) to read
        :param read_nbytes: number of bytes to be read

        :return: response of read transaction
        :rtype: list
        """

        # Loads i2c_msg if not previously loaded
        if self._i2c_msg == None:
            from smbus2 import i2c_msg
            self._i2c_msg = i2c_msg

        # Sets up write and read transactions for reading a register
        write = _i2c_msg.write(address, write_message)
        read = _i2c_msg.read(address, read_nbytes)

        # Read Register
        with SMBus(self.i2c_bus_number) as bus:
            for i in range(_retry_count):
                try:
                    bus.i2c_rdwr(write, read)

                    break # break if try succeeds

                except IOError as ioErr:
                    # we had an error - let's try again
                    if i == _retry_count-1:
                        raise ioErr
                    pass

        # Return read transaction (list)
        return read

    # from class level method from index.py of i2c

    def isDeviceConnected(self, devAddress):
        """
        .. function:: isDeviceConnected()

            Function to determine if a particular device (at the provided address)
            is connected to the bus.

            :param devAddress: The I2C address of the device to check

            :return: True if the device is connected, otherwise False.
            :rtype: bool

        """

        isConnected = False
        ret = None
        with SMBus(self.i2c_bus_number) as bus:
            try:
                # Try to write a byte to the device, command 0x0
                # If it throws an I/O error - the device isn't connected
                self.writeCommand(devAddress, 0x0)
                isConnected = True
            except Exception as ee:
                print("Error connecting to Device: %X, %s" % (devAddress, ee))
                pass
            return isConnected
