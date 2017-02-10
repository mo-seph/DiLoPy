import socket
import time
import struct
from network import LoRa
from binascii import hexlify

import pycom # we need this module to control the LED
pycom.heartbeat(False) # disable the blue blinking


WAIT_COLOR = 0x111100
OK_COLOR = 0x00FF00
FAIL_COLOR = 0xFF0000
PAUSE_COLOR = 0x000011

## An ID for the protocol, as there may be lots of messages flying around
PROTOCOL_ID = 0x01

# A basic package header, B: 1 byte for the protocol id,  B: 1 byte for the deviceId, B: 1 bytes for the pkg size
_LORA_PKG_FORMAT = "BBB%ds"
_LORA_PKG_ACK_FORMAT = "BBBB"



##### Set this to your group number. If you have more than one device, use the first digit,
##### i.e. group 4, would have devices 0x04, 0x14, 0x24 etc.
DEVICE_ID = 0x01

WAIT_FOR_ACK = True
TIMEOUT = 3000



print("Node %X starting up!" % (DEVICE_ID) )
pycom.rgbled(WAIT_COLOR)

# Open a Lora Socket, use tx_iq to avoid listening to our own messages
lora = LoRa(mode=LoRa.LORA, tx_iq=False,  rx_iq=False  )
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)

print("Node LoRa OK")


def wait_for_response():
    pycom.rgbled(WAIT_COLOR) # make the LED light up yellow   
    # Wait for the response from the gateway. NOTE: For this demo the device does an infinite loop for while waiting the response. Introduce a max_time_waiting for you application
    start = time.ticks_ms()
    waiting_ack = True
    
    while( waiting_ack ):
        time_diff = time.ticks_diff(start,  time.ticks_ms() )
        if ( time_diff < TIMEOUT ):
            recv_ack = lora_sock.recv(256)
            if (len(recv_ack) > 0):
                proto_id,  device_id, pkg_len, ack = struct.unpack(_LORA_PKG_ACK_FORMAT, recv_ack)
                if ( proto_id == PROTOCOL_ID and device_id == DEVICE_ID) :
                    waiting_ack = False
                    if (ack == 200):
                        print("ACK")
                        pycom.rgbled(OK_COLOR)
                        time.sleep(0.1)
                    else:
                        print("Message Failed: %d" % (ack))
                        pycom.rgbled(FAIL_COLOR)
                        time.sleep(0.5)
        else:
            print("Giving up on ack")
            waiting_ack = False
            pycom.rgbled(FAIL_COLOR)
            time.sleep(0.5)
    pycom.rgbled(PAUSE_COLOR)
    time.sleep(0.9)

    
while(True):
    # Package send containing a simple string
    msg = "Hello!"
    print("Device %X sending message: %s" % (DEVICE_ID, msg))
    pkg = struct.pack(_LORA_PKG_FORMAT % len(msg), PROTOCOL_ID, DEVICE_ID, len(msg), msg)
    print(hexlify(pkg))
    lora_sock.send(pkg)
    print("Sent OK!")
    if( WAIT_FOR_ACK ):
        wait_for_response()
    else:
        pycom.rgbled(0xffff00)
        time.sleep(0.3)
        pycom.rgbled(0x001100)
        time.sleep(1.7)
    

