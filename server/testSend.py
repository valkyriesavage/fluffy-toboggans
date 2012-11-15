# testing the send function
import serial
from xbee import XBee
import time

SERIALPORT = "/dev/tts/0"    # the com/serial port the XBee is connected to
BAUDRATE = 9600      # the baud rate we talk to the xbee

serial_port = serial.Serial(SERIALPORT,BAUDRATE)
xbee = XBee(serial_port)

print xbee.at(command='ND')

while 0:

    packet = xbee.wait_read_frame()
    print packet
    # print packet['source_addr'], packet['id'], packet['rssi'], packet['options']

    if packet['id'] == 'rx_io_data':

        if packet['source_addr'] == '\x00\x12':
            print packet['source_addr']

#MAC, number written on the back of the XBee module
# CO3 = my coordinator
# EP1 = my endpoint with the LED on pin 11

device={
        "CO3":'\x00\x00\x00\x00\x00\x00\x00\x00',
        "EP1":'\x00\x13\xa2\x00\x40\x64\x71\x68'
}

#change remote device function
# xbee.remote_at(dest_addr_long=device["EP1"],command='D2',parameter='\x02')
# xbee.remote_at(dest_addr_long=device["EP1"],command='D1',parameter='\x03')
# xbee.remote_at(dest_addr_long=device["EP1"],command='SM',parameter='\x00')
# xbee.remote_at(dest_addr_long=device["EP1"],command='SP',parameter='\x00')
xbee.remote_at(dest_addr_long=device["EP1"],command='ST',parameter='\x1388')
xbee.remote_at(dest_addr_long=device["EP1"],command='IR',parameter='\x04\x00')
xbee.remote_at(dest_addr_long=device["EP1"],command='IC',parameter='\x02')
xbee.remote_at(dest_addr_long=device["EP1"],command='WR')

led=False
while 1:

        #set led status
        led=not led

        if led:
                # xbee.remote_at(dest_addr_long=device["EP1"],command='D4',parameter='\x04')
		xbee.remote_at(dest_addr='\x00\x0f',command='D4',parameter='\x04')
                print "LED Off"
        else:
                # xbee.remote_at(dest_addr_long=device["EP1"],command='D4',parameter='\x05')
		xbee.remote_at(dest_addr='\x00\x0f',command='D4',parameter='\x05')
                print "LED On"

        xbee.remote_at(dest_addr='\x00\x12', command='WR')
        # wait 1 second
        time.sleep(1)

serial_port.close()