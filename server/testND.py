from xbee import XBee
import serial

ser = serial.Serial('/dev/tts/0', 9600)
xb = XBee(ser)
xb.at(command='ND')  # Send Node Discovery command (ATND)
while True:
    try:
        frame = xb.wait_read_frame()
        print frame
    except KeyboardInterrupt:
        break

ser.close()
