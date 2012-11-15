import serial
from xbee import XBee
import time

SERIALPORT = "/dev/tts/0"
BAUDRATE = 9600

serial_port = serial.Serial(SERIALPORT,BAUDRATE)
xbee = XBee(serial_port)

thisDest = '\x00\x0f'

xbee.send('remote_at',
          frame_id='C',
          dest_addr=thisDest,
          options='\x02',
          command='IR',
          parameter='\x32')

print xbee.wait_read_frame()['status']

# Deactivate LED pin, D4
xbee.remote_at(dest_addr=thisDest,command='D4',parameter='\x04')
xbee.remote_at(dest_addr=thisDest,command='WR')

led=False
while True:
  #set led status
  led=not led

  if led:
    xbee.remote_at(dest_addr=thisDest,command='D4',parameter='\x04')
    print "LED Off"
  else:
    xbee.remote_at(dest_addr=thisDest,command='D4',parameter='\x05')
    print "LED On"

  # wait 1 second
  time.sleep(1)

serial_port.close()
