#!/usr/bin/env python

# original source: http://github.com/adafruit/Tweet-a-Watt/blob/master/wattcher.py
# tps, 03.14.2011 - fix for data output spikes
print "Sensor Manager..."
print "CS262a/CS294-84 project based on code from Tinaja labs"
print "------------------------------------------------------"

import serial, time, datetime, sys, random, math
import syslog
from xbee import xbee
import sensorhistory
import ConfigParser, os

# to send feeds to Sen.se
import urllib, urllib2, httplib
import simplejson
print "imported simplejson lib..."

SERIALPORT = "/dev/ttyAMA0"    # the com/serial port the XBee is connected to
BAUDRATE = 9600      # the baud rate we talk to the xbee

# open up the serial port to get data transmitted to xbee
try:
    ser = serial.Serial(SERIALPORT, BAUDRATE)
    ser.open()
    print "TLSM - serial port opened..."
    syslog.syslog("TLSM.opening: serial port opened...")
except Exception, e:
    print "Serial port exception: "+str(e)
    syslog.syslog("TLSM.opening exception: serial port: "+str(e))
    exit

# detect command line arguments
DEBUG = False
if (sys.argv and len(sys.argv) > 1):
    if sys.argv[1] == "-d":
        DEBUG = True


##############################################################
# the main function
def mainloop(idleevent):
    global sensorhistories, DEBUG

    # grab one packet from the xbee, or timeout
    try:
        packet = xbee.find_packet(ser)
        if not packet:
            print "    no serial packet found... "+ time.strftime("%Y %m %d, %H:%M")
            syslog.syslog("TLSM.mainloop exception: no serial packet found..." )
            return
    except Exception, e:
        print "TLSM.mainloop exception: Serial packet: "+str(e)
        syslog.syslog("TLSM.mainloop exception: Serial packet: "+str(e))
        return


    try:
        xb = xbee(packet)    # parse the packet
        if not xb:
            print "    no xb packet found..."
            syslog.syslog("TLSM.mainloop exception: no xb packet found...")
            return
    except Exception, e:
        print "TLSM.mainloop exception: xb packet: "+str(e)
        syslog.syslog("TLSM.mainloop exception: xb packet: "+str(e))
        return

    # this traps an error when there is no address_16 attribute for xb
    # why this happens is a mystery to me
    try:
        if xb.address_16 == 99:
            return
    except Exception, e:
        print "xb attribute (address_16) exception: "+str(e)
        syslog.syslog("TLSM.mainloop exception: xb attribute: "+str(e))
        return

    # ------------------------------------------------------------------
    # break out and do something for each device

    if xb.address_16 == 1: # Tomato
        SenseFeedKeys = [0,0,0,0]
        cosmLogKey = "29631"

        adcinputs = [0,1,2,3]
        for i in range(len(adcinputs)):
            cXbeeAddr = str(xb.address_16)
            cXbeeAdc = str(adcinputs[i])
            adcSensorNum = int(cXbeeAddr + cXbeeAdc)
            SenseFeedKey = str(SenseFeedKeys[i])

            # print "adcSensorNum", adcSensorNum, avgunit
            sensorhistory = sensorhistories.find(adcSensorNum)
            addunithistory(sensorhistory, avgunit)
            fiveminutelog(sensorhistory, xb.rssi, adcinputs[i])


    else:
        return


# sub-routines
##############################################################
def fiveminutelog(loSensorHistory, xbRssi, adcinput):
    # Determine the minute of the hour (ie 6:42 -> '42')
    # currminute = (int(time.time())/60) % 10
    currminute = (int(time.time())/60) % 5
    fiveminutetimer = loSensorHistory.fiveminutetimer

    # Figure out if its been five minutes since our last save
    if (((time.time() - fiveminutetimer) >= 60.0) and (currminute % 5 == 0)):
        # print " . 5min test: time.time()=", time.time(), " fiveminutetimer=", fiveminutetimer, "currminute=", currminute, " currminute % 5: ", currminute % 5
        # units used in last 5 minutes
        sensornum = loSensorHistory.sensornum
        avgunitsused = loSensorHistory.avgunitsover5min()

        syslog.syslog("TLSM.fiveminutelog: Sensor# "+str(sensornum)+" has averaged: "+str(avgunitsused))

        # log to the local CSV file
        logtocsv(sensornum, avgunitsused, logfile)

        # Reset the 5 minute timer
        loSensorHistory.reset5mintimer()


##############################################################
# log to the local CSV file
def logtocsv(lnSensorNum, lnAvgUnits, loLogfile):

        # Lets log it! Seek to the end of our log file
        if loLogfile:
            loLogfile.seek(0, 2) # 2 == SEEK_END. ie, go to the end of the file
            loLogfile.write(time.strftime("%Y %m %d, %H:%M")+", "+
                          str(lnSensorNum)+", "+
                          str(lnAvgUnits)+"\n")
            loLogfile.flush()
            # print "Sensor# ", lnSensorNum, "logged ", lnAvgUnits, " to ", loLogfile.name


##############################################################
def getlogfile():
    LOCALLOGPATH = "/home/pi/fraiche/sensorlog"

    TimeStamp = "%s" % (time.strftime("%Y%m%d"))
    # print "TimeStamp", TimeStamp
    filename = LOCALLOGPATH+TimeStamp+".csv"   # where we will store our flatfile data

    lfile = None
    try:
        lfile = open(filename, 'r+')
    except IOError:
        # didn't exist yet
        lfile = open(filename, 'w+')
        lfile.write("#Date, time, sensornum, value\n");
        lfile.flush()

    return lfile



##############################################
# open our datalogging file
logfile = getlogfile()
print "Log file "+logfile.name+" opened..."

# load sensor history from the logfile
sensorhistories = sensorhistory.SensorHistories(logfile)
# print "Sensor history: ", sensorhistories
print "Sensor history loaded..."


##############################################
syslog.syslog("<<<  Starting the Tinaja Labs Sensor Manager (TLSM)  >>>")
print "The main loop is starting..."


##############################################
# the 'main loop' runs once a second or so
while True:
    mainloop(None)
