#!/usr/bin/env python
import serial
from xbee import xbee

SERIALPORT = "/dev/tts/0"    # the com/serial port the XBee is connected to
BAUDRATE = 9600      # the baud rate we talk to the xbee

# open up the FTDI serial port to get data transmitted to xbee
ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.open()

while True:
    # grab one packet from the xbee, or timeout
    packet = xbee.find_packet(ser)
    if packet:
        xb = xbee(packet)

	print ">>> "
        print xb
