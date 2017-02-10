import socket
import struct
from network import LoRa
import time
from binascii import hexlify


import pycom # we need this module to control the LED
pycom.heartbeat(False) # disable the blue blinking


WAIT_COLOR = 0x111100
RCV_COLOR = 0x0000FF

## An ID for the protocol, as there may be lots of messages flying around
PROTOCOL_ID = 0x01


# A basic package header, B: 1 byte for the deviceId, B: 1 byte for the pkg size, %ds: Formated string for string
_LORA_PKG_FORMAT = "BBB%ds"
# A basic ack package, B: 1 byte for the protocol id, B: 1 byte for the deviceId, B: 1 bytes for the pkg size, B: 1 byte for the Ok (200) or error messages
_LORA_PKG_ACK_FORMAT = "BBBB"

print("Gateway starting up...")
pycom.rgbled(WAIT_COLOR) # make the LED light up in yellow color
# Open a LoRa Socket, use rx_iq to avoid listening to our own messages
lora = LoRa(mode=LoRa.LORA, rx_iq=False,  tx_iq=False)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(True)
print("Gateway LoRa good")


while (True):
    recv_pkg = lora_sock.recv(512) #512 is the max amount to receive
    if (len(recv_pkg) > 2):        #Check packet is valid, and has some data
        pycom.rgbled(RCV_COLOR)     #LED goes blue
        recv_pkg_len = recv_pkg[2]  #3rd byte says how much data is in the packet?
        print("Got packet %s (length: %d)" % (hexlify(recv_pkg), recv_pkg_len))
        try:
            # Unpack the packet to get the protocol ID, device ID, data length and data as a string
            proto_id,  device_id, pkg_len, msg = struct.unpack(_LORA_PKG_FORMAT % recv_pkg_len, recv_pkg)
            if( proto_id == PROTOCOL_ID ):
                #Print out the data
                print('Dev %02x says "%s"' % (device_id, msg))

                #Send back an acknowledgement
                ack_pkg = struct.pack(_LORA_PKG_ACK_FORMAT, PROTOCOL_ID,  device_id, 1, 200)
                lora_sock.send(ack_pkg)
                time.sleep(0.05)
                pycom.rgbled(WAIT_COLOR) # turn LED back to yellow
            else:
                print("Unknown protocol: %02x" % (proto_id) )
        except Exception as e:
            print("Bad packet: %s" % (str(e)))
