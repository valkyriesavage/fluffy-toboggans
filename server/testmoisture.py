from xbee import xbee
import serial
import math

SERIALPORT = "/dev/tts/0"    # the com/serial port the XBee is connected to
BAUDRATE = 9600      # the baud rate we talk to the xbee

print "we set the ports"

# open up the FTDI serial port to get data transmitted to xbee
ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.open()

print 'we opened the ports'

# try:
    # print 'trying...'
while True:
  # grab one packet from the xbee, or timeout
  # print 'while loop... '
  # packet = xbee.find_packet(ser)

  try:
    packet = xbee.find_packet(ser)
      if not packet:
        print "    no serial packet found... "+ time.strftime("%Y %m %d, %H:%M")
          continue

  except Exception, e:
    print "TLSM.mainloop exception: Serial packet: "+str(e)
    continue


  print 'packet received'
  if packet:
    # xb = xbee(packet)
    try:
      xb = xbee(packet)    # parse the packet
        if not xb:
          print "    no xb packet found..."
          continue

    except Exception, e:
      print "TLSM.mainloop exception: xb packet: "+str(e)
      continue

  print 'packet from device #: ' + str(xb.address_16)
  # Tempurature reading code
  # xb.analog_samples[sample #][A/D pin#] is used to grab the first sample and pin in the xb packet

  if xb.address_16 == 7:
    mVolts = xb.analog_samples[0][2]  # Report the millivolts from the TMP36
    # tempC = mVolts * 0.1              # Convert millivolts to Celcius
    voltage = mVolts * 3.3 / 1024              # Convert millivolts to Celcius
    tempC = (voltage - .5) * 100              # Convert millivolts to Celcius
    tempF = math.floor(tempC * 9 / 5 + 32)        # Convert to Fehrenheit
    # print "7-2 ", tempC, "C \t", tempF, "F - ", mVolts, voltage     # Print formated tempurature readings

  if xb.address_16 == 7:
    mVolts0 = xb.analog_samples[0][0]  # Report the millivolts from moisture
    mVolts1 = xb.analog_samples[0][1]  # Report the millivolts from
