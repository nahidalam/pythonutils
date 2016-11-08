#! /usr/bin/python

import datetime
import socket
from time import sleep
import threading
from xbee import ZigBee
import serial
import Queue
import time

import sys, getopt, os.path, glob, HTMLParser, re
import urllib
import re
import csv

PORT='COM17'
BAUD_RATE = 9600
count=0

UNKNOWN = '\xff\xfe'
SETPOSString='setpos:30'
STOPString='STOP'

packets = Queue.Queue()

#stop_time = datetime.datetime.now() + datetime.timedelta(hours=96)
stop_time = datetime.datetime.now() + datetime.timedelta(seconds=10)


# Open serial port
ser = serial.Serial(PORT, BAUD_RATE)

#T4-HF
#WHERE = '\x00\x13\xA2\x00\x40\xF7\x0A\x65'

# this is a call back function.  When a message
# comes in this function will get the data
def message_received(data):
        packets.put(data, block=False)
        print 'gotta packet'

def sendPacket(where, what):
        # I'm only going to send the absolute minimum.
        zb.send('tx',
                dest_addr_long = where,
                dest_addr = UNKNOWN,
                data = what)

def handlePacket(data):
        print 'In handlePacket: ',
        print data['id'],
        if data['id'] == 'tx_status':
                print data['deliver_status'].encode('hex')
        elif data['id'] == 'rx':
                #this section receives data
                print data 
                print repr(data['source_addr_long'])
                print data['rf_data']
                z=str(data)
                timestr = time.strftime("%Y%m%d")
                with open(timestr, "a") as myfile:
                #with open("t2.txt", "a") as myfile:
                    myfile.seek(0)
                    myfile.write(z+'\n')
                #save address and data in json format
        else:
                print 'Unimplemented frame type'


# Create XBee library API object, which spawns a new 
zb = ZigBee(ser, callback=message_received)


def process():
    while datetime.datetime.now() < stop_time:
        #global count
        #if count == 0:
                SETPOSString='setpos:60'
                sendPacket(WHERE, SETPOSString)
                SETPOSString='setpos:0'
                sendPacket(WHERE, SETPOSString)
                SETPOSString='setpos:-60'
                sendPacket(WHERE, SETPOSString)
                SETPOSString='setpos:0'
                sendPacket(WHERE, SETPOSString)
                #count = count +1
        try:
                time.sleep(0.1)
                if packets.qsize() > 0:
                        print 'packet available'
                        newPacket = packets.get_nowait()
                        handlePacket(newPacket)
                        #write code for json storing
        except KeyboardInterrupt:
                sendPacket(WHERE, STOPString)
                count=0
                zb.halt()
                ser.close()
                break

thread = threading.Thread(target=process)
thread.daemon = True
thread.start()


#now = datetime.datetime.now()
#print now.year, now.month, now.day, now.hour, now.minute, now.second
#while datetime.datetime.now() < stop_time:
    #rotate motor here
    #print "hello"




