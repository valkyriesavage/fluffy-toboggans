#!/usr/bin/env python

# original source: http://github.com/adafruit/Tweet-a-Watt/blob/master/wattcher.py
# tps, 03.14.2011 - fix for data output spikes
print "Sensor Manager..."
print "CS294-84 project based on code from Tinaja labs"
print "-----------------------------------------------"

import os, serial, syslog, time
from xbee import xbee
from server import log_data_file

SERIALPORT = "/dev/ttyAMA0"    # the com/serial port the XBee is connected to
BAUDRATE = 9600      # the baud rate we talk to the xbee

##############################################################
# the main function
def mainloop(idleevent):

    # grab one packet from the xbee, or timeout
    try:
        packet = xbee.find_packet(ser)
        if not packet:
            syslog.syslog("H2OIQ.mainloop exception: no serial packet found..." )
            return

    except Exception, e:
        syslog.syslog("H2OIQ.mainloop exception: Serial packet: "+str(e))
        return

    try:
        xb = xbee(packet)    # parse the packet
        if not xb:
            syslog.syslog("H2OIQ.mainloop exception: no xb packet found...")
            return
    except Exception, e:
        syslog.syslog("H2OIQ.mainloop exception: xb packet: "+str(e))
        return

    # this traps an error when there is no address_16 attribute for xb
    # why this happens is a mystery to me
    try:
        if xb.address_16 == 99:
            return
    except Exception, e:
        syslog.syslog("H2OIQ.mainloop exception: xb attribute: "+str(e))
        return

    # respond to the XBee
    respond(xb)

    # log the data
    plant_num = xb.address_16
    sensor_data = xb.analog_samples[0]
    log_data(plant_num, sensor_data)
    alert_sever(plant_num, sensor_data)


def respond(xb):
  print xb.address_16

ZERO_BYTES_FROM = 0
FILE_END = 2

def log_data(plant_num, sensor_value):
  oclock = time.time()
  lf = open(log_data_file(plant_num), "w+")
  lf.seek(ZERO_BYTES_FROM, FILE_END)
  lf.write(oclock + " " + sensor_value + "\n")

def alert_server(plant_num):
  urllib.urlopen('localhost:8888/sensorupdated/' + plant_num + '/' + sensor_data)

# open up the serial port to get data transmitted to xbee
try:
    ser = serial.Serial(SERIALPORT, BAUDRATE)
    ser.open()
    syslog.syslog("H2OIQ.opening: serial port opened...")
except Exception, e:
    syslog.syslog("H2OIQ.opening exception: serial port: "+str(e))
    exit()

syslog.syslog("<<<  Starting the Smart Watering Sensor System for H2OIQ  >>>")

while True:
    mainloop(None)
