#!/usr/bin/env python

import time
import re
import subprocess
from optparse import OptionParser
from MappingIndex import *


class Command():
    def __init__(self):
	pass

    def SendReturn(self, cmdAsciiStr):
        self.f = subprocess.Popen(cmdAsciiStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	#tmp = "Send = "+cmdAsciiStr
	#print tmp
	self.PROMPT="root >"
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
class UTS_NvmeCheck():
    section_str = "Section: NVME Check"
    def __init__(self,devicecount):
	self.pci_buses=["af:00","b0:00","18:00","19:00"]
	self.testIndex=""
	self.bus_id=""
        self.devicesPatt =  r'Disk\s+(?P<Name>/dev/\w+):'
        self.patternDevices = re.compile(self.devicesPatt)
	self.comm= Command()
	self.devicecount=int(devicecount)
    def Start(self):
	if True:
	    if self.FindNVMEDevices():
            	self.comm.uts_format('NVME Check PASS',"i")
	    else:
            	self.comm.uts_format('NVME Check FAIL',"i")
        try:
		pass
        except Exception, exception:
            self.comm.uts_format('Exception=%s' % exception,"f")
	
    def FindNVMEDevices(self):
	for mp in mapping_list:
		if mp["slot_index"]==int(self.testIndex):
			self.bus_id=mp["k2c_busid"]
       	self.comm.SendReturn("fdisk -l | grep nvme")
	line = self.comm.RecvTerminatedBy()
	devices = re.findall(r"/dev/\w+",line)
	nvme_driver_count=0
	for device in devices:
        	self.comm.SendReturn("udevadm info  --query=all --name=%s" %device)
		sub_line = self.comm.RecvTerminatedBy()
		if sub_line.find("0000:%s.0/nvme" %self.bus_id)>=0:
			nvme_driver_count=nvme_driver_count+1
		if sub_line.find("0000:%s.1/nvme" %self.bus_id)>=0:
			nvme_driver_count=nvme_driver_count+1

	if nvme_driver_count==2:
		print "#i find 2 nvme for %s" %self.bus_id
		return True 
	else:
		print "#i can't find 2 nvme for %s" %self.bus_id
		return False
	
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])")
    parser.add_option("-c", "--cardcount", \
                      action="store", \
                      dest="cardcount", \
                      default="4", \
                      help="card count")
    parser.add_option("-i", "--testindex", \
                      action="store", \
                      dest="testindex", \
                      default="0", \
                      help="testindex")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
        parser.error("wrong number of arguments")
        sys.exit(1)


    test = UTS_NvmeCheck(int(options.cardcount))
    test.testIndex=str(options.testindex)
    print "#i XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    print "#i current index is %s" %options.testindex
    print "#i XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    result = test.Start()
