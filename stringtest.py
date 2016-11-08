#! /usr/bin/python

SETPOSString='setpos:'
angle =["60","0","-60","0"]

for i in range(0,4):
    c=SETPOSString+angle[i]
    print c
