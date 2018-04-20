#!/usr/bin/env python

from telnetlib import Telnet
from optparse import OptionParser
import subprocess
import re
import time


class Command():
    def __init__(self):
	self.PROMPT="ROOT>"
	pass

    def SendReturn(self, cmdAsciiStr):
        self.f = subprocess.Popen(cmdAsciiStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	#tmp = "Send = "+cmdAsciiStr
	#print tmp
	self.uts_format("Send command:\t" + cmdAsciiStr,"i")

    def uts_format(self,s,label):
	print "#%s %s" %(label,s)

    def RecvTerminatedBy(self, *prompt_ptr):
	if len(prompt_ptr) == 0:
	    prompt = self.PROMPT
	else:
	    prompt = prompt_ptr[0]

	#print 'Rece = '
	stdout = ''
	while self.f.poll() == None:
	    stdout_line = self.f.stdout.readline()
	    stdout = stdout + stdout_line
	    if stdout_line != '':
		pass
		#self.uts_format("Recive String:" + stdout_line,"i")
		#print stdout_line,
	else:
	    stdout_lines = self.f.stdout.read()
	    stdout = stdout + stdout_lines
	    if stdout_line != '':
		pass
		#self.uts_format("Recive String:" + stdout_line,"i")
		#print stdout_lines,

	if stdout != '':
	    self.uts_format("Recive String:\n" + stdout,"i")
	    return stdout
	    
	else:
	    stderr = self.f.stderr.read()
	    #if stderr != '':
	    #    print stderr
	    print stderr,
	    self.uts_format("Recive String:\n" + stdout_line,"i")
	    return stderr

    def close(self):
        pass

class UTS_InterposeEthernetCheck():
    section_str = "Section: Ethernet GB loop back test"
    def __init__(self):
        #self.pattern = self.cmdPattern.EthernetVersion
        self.pattern = "(?P<Version>0x800009fa)"
        self.p = re.compile(self.pattern)
	self.port0=""
	self.port1=""
	self.port2=""
	self.port3=""
	self.busIds=["0000:af:00.2","0000:b0:00.2","0000:18:00.2","0000:19:00.2"]
	self.device="ixgbe"
	self.fw="0x800009fa"
	self.comm= Command()
    def PrintI(self,string):
	print "#i %s" %string
    def PrintF(self,string):
	print "#f %s" %string
    def Start(self,busids,ipsegment):
	self.PrintI(UTS_InterposeEthernetCheck.section_str)
        try:
	    testFlag=True
	    self.FindEthDev()
	    if ipsegment=="10":
	    	if busids.find("0")>-1:
	    		self.ConfigEthPort(self.port0,"10")
	    		if self.port0=="" or self.PingTest("192.168.10.2")!=5:
	    			testFlag=False
				self.PrintI("Ping test fail at %s" %self.port0)
	   	if busids.find("1")>-1:
	    		self.ConfigEthPort(self.port1,"10")
	    		if self.port1=="" or self.PingTest("192.168.10.2")!=5:
	    			testFlag=False
				self.PrintI("Ping test fail at %s" %self.port1)
	    	if busids.find("2")>-1:
	    		self.ConfigEthPort(self.port2,"10")
	    		if self.port2=="" or self.PingTest("192.168.10.2")!=5:
	    			testFlag=False
				self.PrintI("Ping test fail at %s" %self.port2)
	    	if busids.find("3")>-1:
	    		self.ConfigEthPort(self.port3,"10")
	    		if self.port3=="" or self.PingTest("192.168.10.2")!=5:
	    			testFlag=False
				self.PrintI("Ping test fail at %s" %self.port3)
	    if ipsegment=="20":
	    	if busids.find("0")>-1:
	    		self.ConfigEthPort(self.port0,"20")
	    		if self.port0=="" or self.PingTest("192.168.20.2")!=5:
	    			testFlag=False
				self.PrintI("Ping test fail at %s" %self.port0)
	   	if busids.find("1")>-1:
	    		self.ConfigEthPort(self.port1,"20")
	    		if self.port1=="" or self.PingTest("192.168.20.2")!=5:
	    			testFlag=False
				self.PrintI("Ping test fail at %s" %self.port1)
	    	if busids.find("2")>-1:
	    		self.ConfigEthPort(self.port2,"20")
	    		if self.port2=="" or self.PingTest("192.168.20.2")!=5:
	    			testFlag=False
				self.PrintI("Ping test fail at %s" %self.port2)
	    	if busids.find("3")>-1:
	    		self.ConfigEthPort(self.port3,"20")
	    		if self.port3=="" or self.PingTest("192.168.20.2")!=5:
	    			testFlag=False
				self.PrintI("Ping test fail at %s" %self.port3)
	    if testFlag==False:
		self.PrintF("FAILED : Ping test fail")
	    else:
		self.PrintI("PASSED: Ping test pass")
        except Exception, error:
            self.PrintI('ERROR: %s\n' % str(error))
        else:
	    pass
            #self.PrintI("Tester Chk => OK: Ethernet  loop back Verify")
    def FindEthDev(self):
        self.comm.SendReturn('ifconfig -a | grep eth | cut -d " " -f 1')
        line = self.comm.RecvTerminatedBy()
        eth_list = line.split()
	print eth_list
        for ethdev in eth_list:
            self.comm.SendReturn('ethtool -i ' + ethdev)
            line = self.comm.RecvTerminatedBy()
            if self.port0 != '' and self.port1 != '' and self.port2!='' and self.port3!='':
               break
            if line.find(self.busIds[0]) > 0:
		self.port0 = ethdev.replace(":","")
		continue	
            if line.find(self.busIds[1]) > 0:
		self.port1 = ethdev.replace(":","")
		continue	
            if line.find(self.busIds[2]) > 0:
		self.port2 = ethdev.replace(":","")
		continue	
            if line.find(self.busIds[3]) > 0:
		self.port3 = ethdev.replace(":","")
		continue	
    def ConfigEthPort(self,EthName,NetWorkSegment):
	if EthName=="":
		return
	if EthName==self.port0:
        	self.comm.SendReturn('ifconfig %s 192.168.%s.3/24 up' %(self.port0,NetWorkSegment))
        	result = self.comm.RecvTerminatedBy()
        	time.sleep(2)
		if self.port1!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port1)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
		if self.port2!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port2)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
		if self.port3!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port3)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
	if EthName==self.port1:
		if self.port0!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port0)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
        	self.comm.SendReturn('ifconfig %s 192.168.%s.3/24 up' %(self.port1,NetWorkSegment))
        	result = self.comm.RecvTerminatedBy()
        	time.sleep(2)
		if self.port2!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port2)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
		if self.port3!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port3)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
	if EthName==self.port2:
		if self.port0!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port0)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
		if self.port1!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port1)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
        	self.comm.SendReturn('ifconfig %s 192.168.%s.3/24 up' %(self.port2,NetWorkSegment))
        	result = self.comm.RecvTerminatedBy()
        	time.sleep(2)
		if self.port3!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port3)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
	if EthName==self.port3:
		if self.port0!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port0)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
		if self.port1!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port1)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
		if self.port2!="":
        		self.comm.SendReturn('ifconfig %s down' %self.port2)
        		result = self.comm.RecvTerminatedBy()
        		time.sleep(2)
        	self.comm.SendReturn('ifconfig %s 192.168.%s.3/24 up' %(self.port3,NetWorkSegment))
        	result = self.comm.RecvTerminatedBy()
        	time.sleep(2)
    def PingTest(self,Ip_Address):
        cmdStr = "ping -c 5 %s" % Ip_Address
        result = subprocess.Popen(cmdStr, shell=True, \
                                      stdout=subprocess.PIPE, \
                                      stderr=subprocess.PIPE)
        result.wait()
        line = result.communicate()[0]

        self.PrintI(line)
        pattern =r"(?P<receive_count>\d) received,"
        p = re.compile(pattern)
        matchCount = p.search(line)
        if matchCount != None:
            num = int(matchCount.group(1))
            return num
        else:
            return 0

    def CheckEth1GSpeed(self,ethport):

        #get the driver information of Ethernet port
        self.comm.SendReturn('ethtool -i %s' %ethport)
        result = self.comm.RecvTerminatedBy()
        #to theck the speed of the Ethernect port
        self.comm.SendReturn('ethtool  %s' %ethport)
        result = self.comm.RecvTerminatedBy()
        if result.find("1000Mb")<0:
		return False
	else:
		return True
                #raise Error(self.errCode[errorCodeStr], errorCodeStr)

    def EthernetLoopbackTest(self,portA,portB):
	
	#setp1 stop fire firewall
	#  commands:
	#	service iptables stop
	#	echo 0 > /selinux/enforce
        self.comm.SendReturn("service iptables stop")
	line = self.comm.RecvTerminatedBy()

        self.comm.SendReturn("echo 0 > /selinux/enforce")
	line = self.comm.RecvTerminatedBy()

	#
	#setp2 start fire firewall
	#  commands:
	#	service vsftpd start
        self.comm.SendReturn("service vsftpd start")
	line = self.comm.RecvTerminatedBy()

	#step3 excute loop back test
	#  commands:
	#	netloop-testtool -d1 eth0 -d2 eth1 -ftpuser root -ftppassword 111111 -ftpsize 100M -maxerror 1
	#  except string 
	#	All Passed 

        errorCodeStr = 'Ethernet__Loopback_Fail'
        self.comm.SendReturn("./netloop-testtool -d1 %s -d2 %s -ftpuser root -ftppassword 123456 -ftpsize 1G -maxerror 1" %(portA,portB))
	line = self.comm.RecvTerminatedBy()
	if line.find("All Passed")<0:
        	raise Error(self.errCode[errorCodeStr], errorCodeStr)

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option("-b", "--busindex", \
                      action="store", \
                      dest="busindex", \
                      default="", \
                      help="busindex for test,0,1,2,3")
    parser.add_option("-i", "--ipsegment", \
                      action="store", \
                      dest="ipsegment", \
                      default="", \
                      help="ipsegment for test")
    (options, args) = parser.parse_args()
    test = UTS_InterposeEthernetCheck()
    result = test.Start(options.busindex,options.ipsegment)
