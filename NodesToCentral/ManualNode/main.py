import os
import socket
import time
import struct
from network import LoRa

import pycom # we need this module to control the LED
pycom.heartbeat(False) # disable the blue blinking


WAIT_COLOR = 0x111100
OK_COLOR = 0x00FF00
FAIL_COLOR = 0xFF0000
PAUSE_COLOR = 0x000011


## An ID for the protocol, as there may be lots of messages flying around
PROTOCOL_ID = 0x01

# A basic package header, B: 1 byte for the deviceId, B: 1 bytes for the pkg size
_LORA_PKG_FORMAT = "BBB%ds"
_LORA_PKG_ACK_FORMAT = "BBBB"



##### Set this to your group number. If you have more than one device, use the first digit,
##### i.e. group 4, would have devices 0x04, 0x14, 0x24 etc.
DEVICE_ID = 0x01





print("Manual Node %X starting up!" % (DEVICE_ID) )
pycom.rgbled(WAIT_COLOR)
# Open a Lora Socket, use tx_iq to avoid listening to our own messages
lora = LoRa(mode=LoRa.LORA, tx_iq=False,  rx_iq=False  )
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

print("ManualNode LoRa OK")

    
def send(msg):
    # Package send containing a simple string
    print("Device %X sending message: %s" % (DEVICE_ID, msg))
    pkg = struct.pack(_LORA_PKG_FORMAT % len(msg),PROTOCOL_ID,  DEVICE_ID, len(msg), msg)
    lora_sock.send(pkg)
    pycom.rgbled(OK_COLOR)
    time.sleep(0.2)
    pycom.rgbled(PAUSE_COLOR)

    

