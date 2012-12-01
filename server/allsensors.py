#!/usr/bin/env python

print "Sensor Manager..."
print "CS294-84 project based on code from Tinaja labs"
print "-----------------------------------------------"

import serial, time, urllib
from server import log_data_file, instructions_data_file, touch

SERIALPORT = "/dev/ttyAMA0"    # the com/serial port the XBee is connected to
BAUDRATE = 9600      # the baud rate we talk to the xbee

##############################################################
# the main function
def mainloop():
  data = str(ser.readline())

  if not data:
    return
  print "H2OIQ.data: received " + data

  plant_num = "1"
  sensor_data = data.strip()
  try:
    something_ill_throw_away = int(sensor_data)
  except:
    # didn't get a number for some reason
    return

  # respond to the XBee
  respond(plant_num)

  # log the data
  log_data(plant_num, sensor_data)
  alert_server(plant_num, sensor_data)

def respond(plant_num):
  instructions_file = open(instructions_data_file(plant_num), 'r+')
  final_line = chr(1)
  for line in instructions_file:
    final_line = line
  print "H2OIQ.response: responding to plant with " + final_line
  ser.write(final_line)
  instructions_file.truncate(0)
  instructions_file.close()

ZERO_BYTES_FROM = 0
FILE_END = 2

def log_data(plant_num, sensor_value):
  print "H2OIQ.log: logging " + sensor_value + " for plant " + plant_num
  oclock = str(time.time())
  touch(log_data_file(plant_num))
  lf = open(log_data_file(plant_num), "a")
  lf.write(oclock + " " + sensor_value + "\n")
  lf.close()

def alert_server(plant_num, sensor_data):
  print "H2OIQ.alert: alerting server about new data"
  urllib.urlopen('http://localhost:8888/sensorupdated/' + plant_num + '/' + sensor_data)

if __name__ == "__main__":

  # open up the serial port to get data transmitted to xbee
  try:
    ser = serial.Serial(SERIALPORT, BAUDRATE)
    #ser.open()
    print "H2OIQ.opening: serial port opened..."
  except Exception, e:
    print "H2OIQ.opening exception: serial port: "+str(e)
    exit()

  print "<<<  Starting the Smart Watering Sensor System for H2OIQ  >>>"

  while True:
    mainloop()
