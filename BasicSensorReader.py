#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# SDS011_Feinstaub_Sensor.py
# 
# Copyright 2017 <webmaster@raspberryblog.de>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
# 
# 
 
from __future__ import print_function
import serial, struct, sys, time, signal
 
ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600
 
ser.open()
ser.flushInput()
 
def dump_data(d):
	print(' '.join(x.encode('hex') for x in d))
 
def process_frame(d):
	#dump_data(d) #debug
	r = struct.unpack('<HHxxBBB', d[2:])
	pm25 = r[0]/10.0
	pm10 = r[1]/10.0
	checksum = sum(ord(v) for v in d[2:8])%256
	print("{}: PM 2.5: {} μg/m^3 PM 10: {} μg/m^3 CRC={}".format(time.ctime(), pm25, pm10, "OK" if (checksum==r[2] and r[3]==0xab) else "NOK"))
	f = open("out.txt", "a")
	f.write("{},{},{},{}\n".format(time.ctime(), pm25, pm10, "OK" if (checksum==r[2] and r[3]==0xab) else "NOK"))
	f.close()

def sensor_read():
	byte = 0
	while byte != "\xaa":
		byte = ser.read(size=1)
	d = ser.read(size=10)
	if d[0] == "\xc0":
		process_frame(byte + d)
 
def sensor_wake():
	ser.write('\x01')

def sensor_sleep():
	bytes = ['\xaa', #head
	'\xb4', #command 1
	'\x06', #data byte 1
	'\x01', #data byte 2 (set mode)
	'\x00', #data byte 3 (sleep)
	'\x00', #data byte 4
	'\x00', #data byte 5
	'\x00', #data byte 6
	'\x00', #data byte 7
	'\x00', #data byte 8
	'\x00', #data byte 9
	'\x00', #data byte 10
	'\x00', #data byte 11
	'\x00', #data byte 12
	'\x00', #data byte 13
	'\xff', #data byte 14 (device id byte 1)
	'\xff', #data byte 15 (device id byte 2)
	'\x05', #checksum
	'\xab'] #tail
 
	for b in bytes:
 		ser.write(b)
 
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sensor_sleep()
        time.sleep(2)
        sys.exit(0)

def main(args):
	signal.signal(signal.SIGINT, signal_handler)

	sensor_wake()
	time.sleep(12)
	
	while True:
		ser.flushInput()
		sensor_read()
		time.sleep(2)
 
if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))

