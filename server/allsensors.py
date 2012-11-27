#!/usr/bin/env python

print "Sensor Manager..."
print "CS294-84 project based on code from Tinaja labs"
print "-----------------------------------------------"

import os, serial, syslog, time
from server import log_data_file, instructions_data_file

SERIALPORT = "/dev/ttyAMA0"    # the com/serial port the XBee is connected to
BAUDRATE = 9600      # the baud rate we talk to the xbee

##############################################################
# the main function
def mainloop(idleevent):

    data = ser.read()

    if not data:
      return

    plant_num = 1
    sensor_data = data

    # respond to the XBee
    respond(plant_num)

    # log the data
    log_data(plant_num, sensor_data)
    alert_sever(plant_num, sensor_data)


def respond(plant_num):
  instructions_file = open(instructions_data_file(plant_num), 'w+')
  final_line = chr(1)
  for line in instructions_file:
    final_line = line
  ser.write(final_line)
  instructions_file.truncate(0)
  instructions_file.close()

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
