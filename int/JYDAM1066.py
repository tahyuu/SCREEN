#!/usr/bin/env python
import binascii
import serial
from optparse import OptionParser
import time
import math

def order_list(cmd):
    a_list = []
    for i in cmd.split():
        a_list.append(binascii.a2b_hex(i))
    return a_list
def hexShow(line,argv):  
    result = ''  
    hLen = len(argv)  
    valHi=""
    valLo=""
    for i in xrange(hLen):  
        hvol = ord(argv[i])  
        hhex = '%02x'%hvol  
        result += hhex+' '  
	if i==3:
	    valHi=hhex
	if i==4:
	    valLo=hhex
	print hhex,
    voltage=float(int(valHi+ valLo,16))/1000
    print '#i Line %s Voltage is: %sV' %(line,voltage)
    return voltage
def checkAcquisition(value,lowlimit,highlimit):
    if value>=lowlimit and value<=highlimit:
	print "#i test voltage %sV is in range(%sV,%sV)" %(value,lowlimit,highlimit)
    	print "#i PASSED"
    else:
	print "#i test voltage %s is not in range(%sV,%sV)" %(value,lowlimit,highlimit)
    	print "#f FAILED"
def acquisition(line):
    if int(line)<0 or int(line)>5:
	print "Wrong line number line should be in 0 to 5"	
	return
    inq_line_0 = 'FE 04 00 00 00 01 25 C5'
    inq_line_1 = 'FE 04 00 01 00 01 74 05'
    inq_line_2 = 'FE 04 00 02 00 01 84 05'
    inq_line_3 = 'FE 04 00 03 00 01 D5 C5'
    inq_line_4 = 'FE 04 00 04 00 01 64 04'
    inq_line_5 = 'FE 04 00 05 00 01 35 C4'
    try:
    	ser = serial.Serial('/dev/ttyUSB0', 9600)
    	ser.writelines(order_list(eval("inq_line_%s" %line)))
	#print eval("dio_line_%s_on" %line)
#    	ser.writelines(order_list(eval("dio_line_%s_off" %line)))
    	#ser.writelines(order_list(eval("dio_line_%s_on" %line)))
    	x=ser.read(7)
    	return hexShow(line,x)
    except IOError:
	print "#f Open Serial port Error"
def dio_line_on_off(line,on_off):
    dio_line_1_on="FE 05 00 00 FF 00 98 35"
    dio_line_1_off="FE 05 00 00 00 00 D9 C5"
    dio_line_2_on="FE 05 00 01 FF 00 C9 F5"
    dio_line_2_off="FE 05 00 01 00 00 88 05"
    dio_line_3_on="FE 05 00 02 FF 00 39 F5"
    dio_line_3_off="FE 05 00 02 00 00 78 05"
    dio_line_4_on="FE 05 00 03 FF 00 68 35"
    dio_line_4_off="FE 05 00 03 00 00 29 C5"
    dio_line_5_on="FE 05 00 04 FF 00 D9 F4"
    dio_line_5_off="FE 05 00 04 00 00 98 04"
    dio_line_6_on="FE 05 00 05 FF 00 88 34"
    dio_line_6_off="FE 05 00 05 00 00 C9 C4"
    dio_line_7_on="FE 05 00 06 FF 00 78 34"
    dio_line_7_off="FE 05 00 06 00 00 39 C4"
    dio_line_8_on="FE 05 00 07 FF 00 29 F4"
    dio_line_8_off="FE 05 00 07 00 00 68 04"
    dio_line_9_on="FE 05 00 08 FF 00 19 F7"
    dio_line_9_off="FE 05 00 08 00 00 58 07"
    dio_line_a_on="FE 05 00 09 FF 00 48 37"
    dio_line_a_off="FE 05 00 09 00 00 09 C7"
    try:
    	ser = serial.Serial('/dev/ttyUSB0', 9600)
	#close all DIO
    	print '#i try to turn off all Line'
    	ser.writelines(order_list("FE 0F 00 00 00 0A 02 00 00 A0 CC"))
    	x=ser.read(8)
	for i in x:
		print '%02x'%ord(i),
	print 
	time.sleep(0.2)
    	print '#i try to turn on/off Line %s' %line
    	ser.writelines(order_list(eval("dio_line_%s_%s" %(str(hex(line))[-1:],on_off))))
    	x=ser.read(8)
	for i in x:
		print '%02x'%ord(i),
	print 
	time.sleep(0.2)
    	ser.writelines(order_list("FE 01 00 00 00 0A A8 02"))
    	x=ser.read(7)
    	print '#i try to check lines status %s' %line
	for i in x:
		print '%02x'%ord(i),
	print 
	if ord(x[3])==math.pow(2,int(line)-1) or ord(x[4])==math.pow(2,int(line)-9):
    		print '#i PASSED DIO open line %s sucess' %line
		time.sleep(8)
    	else:
    		print '#f FAILED DIO open line %s fail' %line

    except IOError:
	    print "#f Open Serial port Error"
	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])")
    parser.add_option("-t", "--type", \
                      action="store", \
                      dest="type", \
                      default="daq", \
                      help="type for use[dio|daq]")
    parser.add_option("-c", "--c", \
                      action="store", \
                      dest="channel", \
                      default="1", \
                      help="channel for acquisition/dio")
    parser.add_option("-i", "--h", \
                      action="store", \
                      dest="highlimit", \
                      default="1", \
                      help="high limit for acquisition")
    parser.add_option("-o", "--l", \
                      action="store", \
                      dest="lowlimit", \
                      default="1", \
                      help="low limit for acquisition")
    parser.add_option("-a", "--action", \
                      action="store", \
                      dest="action", \
                      default="on", \
                      help="action for dio[on|off]")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
        parser.error("wrong number of arguments")
        sys.exit(1)
    if options.type=="daq":
    	voltage=acquisition(options.channel)
    	checkAcquisition(voltage,float(options.lowlimit),float(options.highlimit))
    elif options.type=="dio":
        dio_line_on_off(int(options.channel),options.action)
