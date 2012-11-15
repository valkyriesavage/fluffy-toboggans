#!/usr/bin/env python
import serial, syslog, time
from xbee import xbee

SERIALPORT = "/dev/tts/0"    # the com/serial port the XBee is connected to
BAUDRATE = 9600      # the baud rate we talk to the xbee

# open up the FTDI serial port to get data transmitted to xbee
ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.open()
print "serial port opened...?"
syslog.syslog("serial port opened...")

print "ready...  and waiting for sensor data"
while True:
    # grab one packet from the xbee, or timeout
    syslog.syslog("testReader.py - " + time.strftime("%Y %m %d, %H:%M"))
    packet = xbee.find_packet(ser)
    if packet:
        xb = xbee(packet)

        try:

            if xb.address_16 == 140:
                print "014: ", xb.analog_samples[0][0], xb.analog_samples[0][1], xb.analog_samples[0][2], xb.analog_samples[0][3], xb.analog_samples[0][4]
            if xb.address_16 == 15:
                print "015: ", xb.analog_samples[0][0], xb.analog_samples[0][1], xb.analog_samples[0][2], xb.analog_samples[0][3], xb.analog_samples[0][4]
            if xb.address_16 == 160:
                print "016: ", xb.analog_samples[0][0], xb.analog_samples[0][1], xb.analog_samples[0][2], xb.analog_samples[0][3], xb.analog_samples[0][4]
            if xb.address_16 == 170:
                print "017: ", xb.analog_samples[0][0], xb.analog_samples[0][1], xb.analog_samples[0][2], xb.analog_samples[0][3], xb.analog_samples[0][4]
            if xb.address_16 == 180:
                print "018: ", xb.analog_samples[0][0], xb.analog_samples[0][1], xb.analog_samples[0][2], xb.analog_samples[0][3], xb.analog_samples[0][4]
            if xb.address_16 == 190:
                print "019: ", xb.analog_samples[0][0], xb.analog_samples[0][1], xb.analog_samples[0][2], xb.analog_samples[0][3], xb.analog_samples[0][4]
            if xb.address_16 == 200:
                print "020: ", xb.analog_samples[0][0], xb.analog_samples[0][1], xb.analog_samples[0][2], xb.analog_samples[0][3], xb.analog_samples[0][4]
            if xb.address_16 == 210:
                print "021: ", xb.analog_samples[0][0], xb.analog_samples[0][1], xb.analog_samples[0][2], xb.analog_samples[0][3], xb.analog_samples[0][4]


        except Exception, e:
            print "xb exception: "+str(e)
            syslog.syslog("xb exception: "+str(e))
