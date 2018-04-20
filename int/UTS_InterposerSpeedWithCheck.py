#!/usr/bin/env python

import time
import re
import subprocess
from optparse import OptionParser

class Command():
    def __init__(self):
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

class UTS_InterposerSpeedWithCheck():
    section_str = "Section: PCIe Devices Link Speed and Width Check"
    def __init__(self):
	self.Int3_Storage1= ('18:00.0', '8', '8', 'Interpose1_Storage1_Ctrl')
	self.Int3_Storage2= ('18:00.1', '8', '8', 'Interpose1_Storage2_Ctrl')
	self.Int3_Ethernet= ('18:00.2', '8', '8', 'Interpose1_Ethernet_Ctrl')
	self.Int4_Storage1= ('19:00.0', '8', '8', 'Interpose2_Storage1_Ctrl')
	self.Int4_Storage2= ('19:00.1', '8', '8', 'Interpose2_Storage2_Ctrl')
	self.Int4_Ethernet= ('19:00.2', '8', '8', 'Interpose2_Ethernet_Ctrl')
	self.Int1_Storage1= ('af:00.0', '8', '8', 'Interpose3_Storage1_Ctrl')
	self.Int1_Storage2= ('af:00.1', '8', '8', 'Interpose3_Storage2_Ctrl')
	self.Int1_Ethernet= ('af:00.2', '8', '8', 'Interpose3_Ethernet_Ctrl')
	self.Int2_Storage1= ('b0:00.0', '8', '8', 'Interpose4_Storage1_Ctrl')
	self.Int2_Storage2= ('b0:00.1', '8', '8', 'Interpose4_Storage2_Ctrl')
	self.Int2_Ethernet= ('b0:00.2', '8', '8', 'Interpose4_Ethernet_Ctrl')
        self.LnkStaPatt = \
                r'LnkSta:\W+' + \
                r'Speed (?P<Speed>\d*[.]*\d)GT\/s,\W+' + \
                r'Width x(?P<Width>\d{1,2}),\W+'
        self.patternLnkSta = re.compile(self.LnkStaPatt)
	self.ErrorList=[]
	self.comm= Command()
    def PrintI(self,string):
	print "#i %s" %string
    def PrintF(self,string):
	print "#f %s" %string

    def Start(self,busid):
        try:
	    if busid.find("0")>-1:
	    	self.CheckPciSpeedWidth(self.Int1_Storage1)
	    	self.CheckPciSpeedWidth(self.Int1_Storage2)
	    	self.CheckPciSpeedWidth(self.Int1_Ethernet)
	    if busid.find("1")>-1:
	    	self.CheckPciSpeedWidth(self.Int2_Storage1)
	    	self.CheckPciSpeedWidth(self.Int2_Storage2)
	    	self.CheckPciSpeedWidth(self.Int2_Ethernet)
	    if busid.find("2")>-1:
	    	self.CheckPciSpeedWidth(self.Int3_Storage1)
	    	self.CheckPciSpeedWidth(self.Int3_Storage2)
	    	self.CheckPciSpeedWidth(self.Int3_Ethernet)
	    if busid.find("3")>-1:
	    	self.CheckPciSpeedWidth(self.Int4_Storage1)
	    	self.CheckPciSpeedWidth(self.Int4_Storage2)
	    	self.CheckPciSpeedWidth(self.Int4_Ethernet)
	    if len(self.ErrorList)==0:
            	self.PrintI('PASSED')
	    else:
            	self.PrintI('FAILED')
            #self.PrintI('PASSED')
        except Exception, exception:
            self.PrintF('Exception=%s' % exception)

    def CheckPciSpeedWidth(self, dev):
	self.PrintI('Subsection: ' + dev[3] + ' Speed and Width Check')
        commandStr = 'lspci -s ' + dev[0] + ' -vvn'
        self.comm.SendReturn(commandStr)
        result = self.comm.RecvTerminatedBy("ROOT>")
	m=None
	speed="0"
	width="0"
	try:
        	m = self.patternLnkSta.search(result)
        	speed = m.group('Speed')
        	width = m.group('Width')
	except:
		pass
		
        if m == None:
	    errCodeSpeedStr = dev[3] + '_Find_Fail'
            #raise Error(self.errCode[errCodeSpeedStr], errCodeSpeedStr)
	    self.ErrorList.append(errCodeSpeedStr)
	errCodeSpeedStr = dev[3] + '_Speed_Fail'
        if speed != dev[1]:
            self.PrintF("FAIL: %s PCIe link speed %s is not reached %s" % \
                        (dev[3], speed, dev[1]))
	    self.ErrorList.append(errCodeSpeedStr)
            #raise Error(self.errCode[errCodeSpeedStr], errCodeSpeedStr)
        else:
            self.PrintI("PASS: %s PCIe link speed %s" % \
                        (dev[3], speed))
	errCodeWidthStr = dev[3] + '_Width_Fail'
        if width != dev[2]:
            self.PrintF("FAIL: %s PCIe link Width %s is not %s" % \
                        (dev[3], width, dev[2]))
            #raise Error(self.errCode[errCodeWidthStr], errCodeWidthStr)
	    self.ErrorList.append(errCodeSpeedStr)
        else:
	    self.PrintI("PASS: %s PCIe link Width is %s" % \
			(dev[3], width))


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])")
    parser.add_option("-i", "--indexbus", \
                      action="store", \
                      dest="indexbus", \
                      default="indexbus", \
                      help="bus index for interposer card [0,1,2,3]")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
        parser.error("wrong number of arguments")
        sys.exit(1)

    test = UTS_InterposerSpeedWithCheck()
    result = test.Start(options.indexbus)
