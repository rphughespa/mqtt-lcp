# change_rfid_address.py

#  change i2c address of SparkFun rdid reader from default of 0x7d to another address in valid range
# plug in rfid read into i2c buss by itself



def rewrite_rfid_reader_address(addr, change_addr, new_addr):
    if (new_addr < 0x07) or (new_addr > 0x77): # Range of legal addresses
        return False
    with SMBus(1) as bus:
        bus.write_byte_data(addr, change_addr, new_addr)

old_address = 0x7d
change_addr_register = 0xC7
new_address = 0x77

rewrite_rfid_reader_address(old_address, change_address_register, new_address)


# check that change worked with i2cdetect -l
