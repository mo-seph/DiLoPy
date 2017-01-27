from network import Bluetooth
import binascii
import time
import struct
from binascii import hexlify

# Data format in bytes 
# From: https://github.com/sandeepmistry/node-bleacon/blob/master/estimote-sticker/estimote-sticker.js
# 0,1  : Manufacturer id (expect 5d 01)
# 2    : Protocol version (expect 01)
# 3-6  : UUID
# 7-8  : major
# 9-10 : minor
# 11   : Type (0x04 -> SB0, otherwise unknown)
# 12   : Firmware
# 13-14: Temperature (mask with 0x0fff, shift right 3)
# 15   : Moving flag (0x04), battery level
# 16-18: Accel, x,y,z, 8bit int
# 19   : Current state duration
# 20   : Prev state duration
# 21   : Power/firmware
#bluetooth = Bluetooth()
#print("Starting Scan")
# scan until we can connect to any BLE device around
#bluetooth.start_scan(-1)

#ESTIMOTE_FORMAT = "HB3c2c2cBBBBBBBBBBB"

bluetooth = Bluetooth()

def parse(data):
    setup = {}
    setup["manuf_id"] = hexlify( data[0:1])
    setup["proto"] = hexlify( data[2:3] )
    setup["uuid"] = hexlify(data[3:7])
    setup["maj_version"] = hexlify( data[7:9] )
    setup["min_version"] = hexlify( data[9:11] )
    setup["type"] = hexlify( data[11:12] )
    setup["firmware"] = hexlify( data[12:13] )
    sense = {}
    raw_temp = (struct.unpack("<h",data[13:14])[0] & 0x0fff) << 4
    temperature = -1000
    if raw_temp & 0x8000:
        temperature = ((raw_temp & 0x7fff) - 32768.0)/256
    else:
        temperature = raw_temp / 256
    sense["raw_temp"] = raw_temp
    sense["temperature"] = temperature
    sense["moving"] = (data[15] & 0x40 ) != 0
    sense["x"] = struct.unpack("!b", data[16:17])[0] * 15.625 / 1000
    sense["y"] = struct.unpack("!b", data[17:18])[0] * 15.625 / 1000
    sense["z"] = struct.unpack("!b", data[18:19])[0] * 15.625 / 1000
    sense["cur_dur"] = data[19]
    sense["prev_dur"] = data[20]
    return { "sensors":sense,  "device":setup}

def scan(scan_time = -1):
    bluetooth.stop_scan()
    bluetooth.start_scan(scan_time)
    while bluetooth.isscanning():
        adv = bluetooth.get_adv()
        if adv:
            try:
                #print("Got adv:")
                data = bluetooth.resolve_adv_data(adv.data, Bluetooth.ADV_MANUFACTURER_DATA)
                if( data[0] == 0x5d and data[1] == 0x01 ): #Company id
                    #print("Got an Estimote packet")
                    if(data[2] == 0x01 ): # Nearable protocol version
                        #print("...and its a Nearable")
                        return data
            except Exception as e:
                print(e)
                print("Bad adv")
    

def stream_data():
    while(True):
        data = scan(1)
        if( data ):
            print(parse(scan())["sensors"])
        else:
            print('.')
        
