#! /usr/bin/python

import socket
from time import sleep
import threading
from xbee import ZigBee
#from apscheduler.scheduler import Scheduler
import serial
import Queue
import time

import sys, getopt, os.path, glob, HTMLParser, re
import urllib
import re
import csv
#from bs4 import BeautifulSoup

#try:    import psyco ; psyco.jit()  # If present, use psyco to accelerate the program
#except: pass

#PORT = '/dev/tty.usbserial-A104IC2U'
#port at PI
#PORT ='/dev/ttyUSB0'
#port at windows
PORT='COM17'
BAUD_RATE = 9600
count=0

# The XBee addresses I'm dealing with
#BROADCAST = '\x00\x00\x00\x00\x00\x00\xff\xff'

#xbee 3
#WHERE = '\x00\x13\xA2\x00\x40\xD9\xB5\xAA'

#R4
#WHERE = '\x00\x13\xA2\x00\x40\xD9\xB5\x43'



#Davis Test Routers
#T1-KMI
#WHERE = '\x00\x13\xA2\x00\x40\xF7\x43\xC1'
#'source_addr_long': '\x00\x13\xa2\x00@\xf7C\xc1'

#T2-KMI
WHERE = '\x00\x13\xA2\x00\x40\xF7\x43\xAA'
#'source_addr_long': '\x00\x13\xa2\x00@\xf7C\xaa'

#T3-HF
#WHERE = '\x00\x13\xA2\x00\x40\xF7\x0A\x5E'
#'source_addr_long': '\x00\x13\xa2\x00@\xf7\n^'

#T4-HF
#WHERE = '\x00\x13\xA2\x00\x40\xF7\x0A\x65'
#'source_addr_long': '\x00\x13\xa2\x00@\xf7\ne'


UNKNOWN = '\xff\xfe' # This is the 'I don't know' 16 bit address
dataString='This is Nahid......'
LOADString='LOAD:T1name=-60.00&T2name=-40.00&T3name=-20.00&T4name=0.00&T5name=+20.00&T6name=+60.00'
TRACKString='TRACK'
STOWString='STOW'
STOPString='STOP'
ALARMString='alarms'
perfString ='perf'
statusString='status'
setPerfString='setperf:30'
setStatusString='setstatus:30'
NULL='\0'
SETPOSString='setpos:30'


packets = Queue.Queue()

# Open serial port
ser = serial.Serial(PORT, BAUD_RATE)


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

def sendQueryPacket():
        print 'sending query packet'
        #sendPacket(BROADCAST, '?\r')
        sendPacket(WHERE, dataString)
        print 'sent done'


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
        elif data['id'] == 'rx_long_addr':
                #this section doesn't catch the data
                print data 
                print data['source_addr_long']
                print data['rf_data']
        else:
                print 'Unimplemented frame type'



# Create XBee library API object, which spawns a new 
zb = ZigBee(ser, callback=message_received)


def process():
    while True:
        global count
        if count == 0:
                sendPacket(WHERE, dataString)
                time.sleep(3)
                sendPacket(WHERE, LOADString)
                time.sleep(3)
                #sendPacket(WHERE, TRACKString)
                count = count +1
        try:
                time.sleep(0.1)
                if packets.qsize() > 0:
                        print 'packet availabe'
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

while True:
    exit_signal = raw_input('Type any control command \n')
    #code for sending commands
    if exit_signal == 'load':
        sendPacket(WHERE, LOADString)
    if exit_signal == 'stow':
        sendPacket(WHERE, STOWString)
    if exit_signal == 'stop':
        sendPacket(WHERE, STOPString)
    if exit_signal == 'track':
        sendPacket(WHERE, TRACKString)
    if exit_signal == 'status':
            sendPacket(WHERE, statusString)
    if exit_signal == 'perf':
            sendPacket(WHERE, perfString)
    if exit_signal == 'alarms':
        sendPacket(WHERE, ALARMString)
    if exit_signal.startswith('setpos'):
        SETPOSString=exit_signal
        sendPacket(WHERE, SETPOSString)
    if exit_signal.startswith('setstatus'):
        setStatusString=exit_signal
        sendPacket(WHERE, setStatusString)
    if exit_signal.startswith('setperf'):
        setPerfString=exit_signal
        sendPacket(WHERE, setPerfString)
    if exit_signal == 'exit':
        zb.halt()
        ser.close()
        break



