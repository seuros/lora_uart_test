#!/usr/bin/env python3

import RPi.GPIO as GPIO
import serial
import time
import sys

M0 = 22
M1 = 27
MODE = ["BROADCAST_AND_MONITOR", "P2P"]

CFG_REG = [
    b'\xC2\x00\x09\xFF\xFF\x00\x62\x00\x17\x03\x00\x00',
    b'\xC2\x00\x09\x00\x00\x00\x62\x00\x17\x03\x00\x00'
]
RET_REG = [
    b'\xC1\x00\x09\xFF\xFF\x00\x62\x00\x17\x03\x00\x00',
    b'\xC1\x00\x09\x00\x00\x00\x62\x00\x17\x03\x00\x00'
]

if len(sys.argv) != 2:
    print("Incorrect number of arguments; please input mode: BROADCAST_AND_MONITOR or P2P.")
    sys.exit(0)

if sys.argv[1] not in MODE:
    print("Invalid parameter; accepted values are: BROADCAST_AND_MONITOR or P2P.")
    sys.exit(0)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(M0, GPIO.OUT)
GPIO.setup(M1, GPIO.OUT)

GPIO.output(M0, GPIO.LOW)
GPIO.output(M1, GPIO.HIGH)
time.sleep(1)

ser = serial.Serial("/dev/ttyAMA0", 9600)
ser.flushInput()

try:
    mode_index = MODE.index(sys.argv[1])
    print(f"Setting mode: {sys.argv[1]}")
    ser.write(CFG_REG[mode_index])

    while True:
        if ser.inWaiting() > 0:
            time.sleep(0.1)
            r_buff = ser.read(ser.inWaiting())
            if r_buff == RET_REG[mode_index]:
                print(f"{sys.argv[1]} mode was activated")
                GPIO.output(M1, GPIO.LOW)
                time.sleep(0.01)
                continue  # Skip further processing for this loop iteration

            if r_buff:
                try:
                    decoded_message = r_buff.decode('ascii')
                    print(f"Received ASCII message in {sys.argv[1]} mode: {decoded_message}")
                except UnicodeDecodeError:
                    print("Received non-ASCII bytes:", r_buff.hex())

        delay_temp += 1
        message_interval = 200000 if sys.argv[1] == MODE[1] else 400000
        if delay_temp > message_interval:
            message = f"This is a {sys.argv[1]} message\r\n".encode()
            ser.write(message)
            delay_temp = 0

except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    if ser.isOpen():
        ser.close()
    GPIO.cleanup()
