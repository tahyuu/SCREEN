#!/usr/bin/env python
import pxssh
import ConfigParser	
import getpass
from datetime import datetime
from Log import Log
import os
import sys
import time
import commands
import collections
import re

class TestUnit:
	def __init__(self):
		self.stationName="IP-BFT"
		self.slot=0
		self.testDate=time.strftime("%Y-%m-%d", time.localtime())
		self.serialNumber=""
		self.Version="1.0"
		self.partNumber=""
		self.testItems=[]
		self.testResult=True
		self.log_filename=""
class TestItem:
	def __init__(self):
		self.testName=""
		self.testStatus=""
		self.testResult=""
		self.testLog=""
class bcolors:
    def __init__(self):
    	self.HEADER = '\033[95m'
   	self.OKBLUE = '\033[94m'
   	self.OKGREEN = '\033[92m'
   	self.WARNING = '\033[93m'
   	self.FAIL = '\033[91m'
   	self.ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
    def BGPASS(self,s):
	return "%s%s%s" %(self.OKGREEN,s,self.ENDC)
    def BGFAIL(self,s):
	return "%s%s%s" %(self.FAIL,s,self.ENDC)
class SSHCommander:

	def __init__(self):
    		self.cf = ConfigParser.ConfigParser()
    		self.cf.read("config.ini")
    		self.s = pxssh.pxssh()
		self.bc=bcolors()
    		self.hostname = self.cf.get("BootOS_Info", "boot_os_ipaddr") 
    		self.username =	self.cf.get("BootOS_Info", "boot_os_user_name") 
    		self.password = self.cf.get("BootOS_Info", "boot_os_password")
	def Login(self):
		try:
    			self.s.login (self.hostname, self.username, self.password, original_prompt='ROOT>')
			return True
		except pxssh.ExceptionPxssh, e:
    			print "pxssh failed on login. please check you with below step\n1,make sure you can ping %s.\n2,make sure you can login with username:%s password %s\n" %(self.hostname,self.username,self.password)
			return False
	def ExcuteCmd(self,cmd):
    		self.s.sendline (cmd)
    		self.s.prompt()
		return self.s.before
	def Logout(self):
    		self.s.logout()
class  CINT: 
	def __init__(self):
		#init test config
		self.cf = ConfigParser.ConfigParser()
	    	self.cf.read("config.ini")
	    	self.hostname = self.cf.get("BootOS_Info", "boot_os_ipaddr")
	    	self.ping_wait=self.cf.get("BootOS_Info", "ping_wait")
	    	self.bc=bcolors()
	    	self.testUnits=[]
	    	self.testsockets=self.cf.get("test_system", "test_slots").split(",")
	    	self.sc=SSHCommander()
	def Init(self):
		j=0
	    	for i in self.testsockets:
			if i=="0":
				j=j+1
				continue
			while True:
	    			serialNumber=raw_input ("please input serial number for slot %s:" %(j+1))	
			
				#to check the sn format
				self.pattern= self.cf.get("FlexFlow_Info", "sn_re")
		        	p = re.compile(self.pattern)
        			if p.match(serialNumber):
            				break
        			else:
	        			print self.bc.BGFAIL("\nplease input correct serial number %s.\n" %(self.pattern))
            				continue

	    		testUnit=TestUnit()
	    		testUnit.slot=j+1
	    		testUnit.serialNumber= serialNumber
	            	testUnit.log_filename = testUnit.serialNumber + \
	    	     				'-' + datetime.now().strftime("%Y%m%d%H%M%S") + '.log'
	    		testUnit.log = Log()
	    		self.testUnits.append(testUnit)
			j=j+1
	    	#init test items
	    	self.testItems = collections.OrderedDict()
	    	self.testItems["Interposer_SpeedWithCheck"]="~/int/UTS_InterposerSpeedWithCheck.py -i %s"
	    	self.testItems["Interposer_Switch1On"]="~/int/JYDAM1066.py -t dio -c 1 -a on"
	    	self.testItems["Interposer_EthernetCheck1"]="~/int/UTS_InterposerEthernetCheck.py -b %s -i 10"
	    	self.testItems["Interposer_Switch2On"]="~/int/JYDAM1066.py -t dio -c 2 -a on"
	    	self.testItems["Interposer_EthernetCheck2"]="~/int/UTS_InterposerEthernetCheck.py -b %s -i 20"
	    	self.testItems["Interposer_NvmeCheck"]="~/int/UTS_NvmeCheck.py -i %s -c 0"

		startStatus=raw_input ("Are you ready to continue testing (yes/no)?")
		if startStatus.upper()=="YES" or startStatus.upper()=="Y":
			return True
		else:
			return False
	def Run(self):
	    	length=int(self.cf.get("Show_Format", "line_length"))
	    	spacelength=int(self.cf.get("Show_Format", "space_between_units"))
	    	spacestar=int(self.cf.get("Show_Format", "begin_star"))
	    	max_test_name_length=int(self.cf.get("Show_Format", "max_test_name_length"))
	    	#do test
	    	#step 1 power on test unit
	    	#power on
	    	#step 2 ping test unit to make sure we can connect to test mother board
	    	backinfo = commands.getstatusoutput('ping -c 10 -w %s %s'%(self.ping_wait,self.hostname))
	    	#backinfo =  os.system('ping -c 10 -w %s %s'%(ping_wait,hostname))
	    	print backinfo[1]
	    	if backinfo[1].find(", 0% packet loss")<0:
	        	print self.bc.BGFAIL("make sure you can ping %s.\n" %(self.hostname))
	    		#sys.exit(0)
			return
	    	#ssh login
	    	if not self.sc.Login():
	    		#sys.exit(0)
			return
	    	
	    	#testItems={
	    	#	   "Interposer_SpeedWithCheck":"~/int/UTS_InterposerSpeedWithCheck.py -i %s",\
	    	#	   "Interposer_EthernetCheck1":"/root/int/UTS_InterposerEthernetCheck.py -b %s -i 10",\
	    	#	   "Interposer_EthernetCheck2":"/root/int/UTS_InterposerEthernetCheck.py -b %s -i 20",\
	    	#		"Interposer_NvmeCheck":"~/int/UTS_NvmeCheck.py -i %s -c 0",\
	    	#	}
	    
		j=0
	    	for index in self.testsockets:
			if index=="0":
				continue
	    		for (key,value) in self.testItems.items():
	    			testItem=TestItem()
	    			testItem.testName=key
				if value.find("%s")>=0:
	    				testItem.testLog=self.sc.ExcuteCmd(value %j)
				else:
	    				testItem.testLog=self.sc.ExcuteCmd(value)
					time.sleep(10)
	    			if testItem.testLog.find("#f")>=0 or testItem.testLog.find("FAILED")>=0 or testItem.testLog.find("PASSED")<=0:
	    				testItem.testResult=False
	    				#if test result of test unit is true. make it false
	    				if self.testUnits[j].testResult:
	    					self.testUnits[j].testResult=False
	    			else:
	    				testItem.testResult=True
				print ".",
	    			self.testUnits[j].testItems.append(testItem)
	    		#testUnits.append(testUnits[index])
			j=j+1
	    	self.sc.Logout()
	    	#paser test results
	    	
	    	#show test results
	    	line1=""
	    	line2=""
	    	line3=""
	    	line4=""
	    	line5=""
	    	line6=""
	    	line7=""
	    	line8=""
	    	line9=""
	    	self.lines=locals()
	    	str_slot="#"*spacestar+"   SLOT : %s  "
	    	str_serial_number="#"*spacestar+"     SN : %s  "
	    	str_part_number=  "#"*spacestar+"     PN : %s  "
	    	str_test_result=  "#"*spacestar+" Result : %s  "
	    	str_test_item="#"*(spacestar-1)+"%s"
	    	home_dir="/root/CINT/"
	    	#save test results
	    	for testUnit in self.testUnits:
	    		header_complete_str=""
	    		testUnit.log.Open("%s/FTLog/%s/%s"%(home_dir,(testUnit.testResult and "PASS" or "FAIL"),testUnit.log_filename))
	            	testUnit.log.PrintNoTime('                                ')
	            	testUnit.log.PrintNoTime('                                ')
	    		header_complete_str+= ('Station    : ' + testUnit.stationName+"\n")
	    		header_complete_str+= ('Date       : ' + testUnit.testDate+"\n") 
	    		header_complete_str+= ('Version    : ' + testUnit.Version+"\n") 
	    		header_complete_str+= ('Test Result: %s\n' %(testUnit.testResult and "PASSED" or "FAILED")) 
	    		header_complete_str+="\n****************************************************************************************\n"
	    		str_testResults=""
	    		for ti in testUnit.testItems:
	    			str_testResults=ti.testName.ljust(70)+str(ti.testResult and "PASSED" or "FAILED").rjust(10)+"\n"
	    			header_complete_str=header_complete_str+str_testResults
	    		header_complete_str +="****************************************************************************************\n"
	    
	    		for testitem in testUnit.testItems:
	    	    		testUnit.log.Print("Section:%s" %testitem.testName)
	    	    		testUnit.log.Print(testitem.testLog)
	    			if testitem.testResult:
	                			testUnit.log.Print("Tester => PASSED : %s Check Pass" %testitem.testName)
	    			else:
	                			testUnit.log.Print("Tester => FAILED : %s Check Fail" %testitem.testName)
	    		
	    		testUnit.log.Close()
	    		testUnit.log.AddHeader_Long(header_complete_str,'%s/FTLog/%s/%s' %(home_dir, (testUnit.testResult and "PASS" or "FAIL"),testUnit.log_filename))
		testReutsArray=["","","","","",""]
	    	for testUnit in self.testUnits:
			#show test slot/unit information
	    		if testUnit.testResult:
	    			line1+= (self.bc.BGPASS("#"*length)+" "*spacelength)
	    			line2+= (self.bc.BGPASS((str_serial_number %(testUnit.serialNumber)).ljust(length,"#").ljust(length+spacelength)))
	    			line3+= (self.bc.BGPASS((str_part_number %(testUnit.partNumber)).ljust(length,"#").ljust(length+spacelength)))
	    			line4+= (self.bc.BGPASS((str_test_result %(testUnit.testResult and "PASSED" or "FAILED")).ljust(length,"#").ljust(length+spacelength)))
	    			line5+= (self.bc.BGFAIL((str_slot %(testUnit.slot)).ljust(length,"#").ljust(length+spacelength)))
	    		else:
	    			line1+= (self.bc.BGFAIL("#"*length)+" "*spacelength)
	    			line2+= (self.bc.BGFAIL((str_serial_number %(testUnit.serialNumber)).ljust(length,"#").ljust(length+spacelength)))
	    			line3+= (self.bc.BGFAIL((str_part_number %(testUnit.partNumber)).ljust(length,"#").ljust(length+spacelength)))
	    			line4+= (self.bc.BGFAIL((str_test_result %(testUnit.testResult and "PASSED" or "FAILED")).ljust(length,"#").ljust(length+spacelength)))
	    			line5+= (self.bc.BGFAIL((str_slot %(testUnit.slot)).ljust(length,"#").ljust(length+spacelength)))
	    			#line4+= (self.bc.BGFAIL(str_test_result %(testUnit.serialNumber,"#"*(length-len("SN: %s" %testUnit.serialNumber)-spacestar))))
			#show test slot/unit information
	    		i=0
	    		for testitem in testUnit.testItems:
	    			if testUnit.testResult:
					testReutsArray=["","","",""]
	    				testReutsArray[i]+= (self.bc.BGPASS((str_test_item %(testitem.testName.ljust(max_test_name_length)+" | "+(testitem.testResult and "PASSED" or "FAILED"))).ljust(length,"#").ljust(length+spacelength)))
	    			else:
	    				testReutsArray[i]+= (self.bc.BGFAIL((str_test_item %(testitem.testName.ljust(max_test_name_length)+" | "+(testitem.testResult and "PASSED" or "FAILED"))).ljust(length,"#").ljust(length+spacelength)))
	    			i=i+1
	    			
	    		
	    	print 
	    	print line1
	    	print line5
	    	print line2
	    	print line3
	    	print line4
		for line in testReutsArray:
			print line
	    	print line1
if __name__=="__main__":
	while True:
		cint=CINT()
		if cint.Init():
			cint.Run()
