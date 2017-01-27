import os
import socket
import time
import struct
from network import LoRa
from machine import ADC

import pycom # we need this module to control the LED
pycom.heartbeat(False) # disable the blue blinking

PROTOCOL_ID = 0x02

##### Set this to your group number. If you have more than one device, use the first digit,
##### i.e. group 4, would have devices 0x04, 0x14, 0x24 etc.
DEVICE_ID = 0x01
TARGET_ID = 0x02

print("LEDNode %X starting up!" % (DEVICE_ID) )

# A basic package header, B: 1 byte for the protocol, B: 1 byte for the sendingId, B: 1 target ID, B: 1 byte for the value
_LORA_LED_FORMAT = "BBBB"

adc = ADC(0)
adc_c = adc.channel(pin='P13')
adc_c()
adc_c.value()

# Open a Lora Socket, use tx_iq to avoid listening to our own messages
lora = LoRa(mode=LoRa.LORA, tx_iq=False,  rx_iq=False  )
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
print("Node LoRa OK")


def check_for_input():
    recv_ack = lora_sock.recv(256)
    if (len(recv_ack) > 0):
        proto_id,  device_id, target_id, value = struct.unpack(_LORA_LED_FORMAT, recv_ack)
        if (proto_id == PROTOCOL_ID and target_id == DEVICE_ID):
            setled(value,  255-value,  0)
            print("Got value %d from %d" % (value, device_id))
        else:
            print("Bad proto (%d) or target id (%d)" % (proto_id, target_id))

def setled(red, green, blue):
  pycom.rgbled(0x000000 + (red << 16) +  (green << 8) +  blue)
  
def send_knob(value):
    print("Seinding value %d to %d" % (value, TARGET_ID))
    pkg = struct.pack(_LORA_LED_FORMAT, PROTOCOL_ID, DEVICE_ID, TARGET_ID, value)
    lora_sock.send(pkg)


old_knob = 0

while(True):
    knob = adc_c.value() // 16 # Read the analogue to digital, and fit into one byte 
    if( abs(old_knob - knob ) > 2 ):
        send_knob(knob)
        old_knob = knob
    check_for_input();
    time.sleep(0.01)
    #if( WAIT_FOR_ACK ):
    #    wait_for_response()
    #else:
    #    pycom.rgbled(0xffff00)
    #    time.sleep(0.3)
    #    pycom.rgbled(0x001100)
    #    time.sleep(1.7)



