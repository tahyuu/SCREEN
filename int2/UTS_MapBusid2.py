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
class UTS_MapBusid():
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
	    self.Mapping()
        try:
		pass
        except Exception, exception:
            self.comm.uts_format('Exception=%s' % exception,"f")
	
    def Mapping(self):
	
        self.comm.SendReturn("lspci | grep 1c36")
	line = self.comm.RecvTerminatedBy()
	busids = re.findall(r"\w{2}\:\w{2}\.",line)
	busids2=list(set(busids))
	print busids2
	k2c_list=[{"k2c_sn":"A716000163","slot_index":0},{"k2c_sn":"A715046639","slot_index":1},{"k2c_sn":"A71504663A","slot_index":2},{"k2c_sn":"A71504663B","slot_index":3}]
	mapping_list=[]
	
	for bus_id in busids2:
		k2c_info={}
        	self.comm.SendReturn("lspci -vvn -s %s" %bus_id)
		sub_line = self.comm.RecvTerminatedBy()
		for k2c in k2c_list:
			if sub_line.find(k2c["k2c_sn"])>=0:
				k2c_info["slot_index"]=k2c["slot_index"]
				k2c_info["k2c_sn"]=k2c["k2c_sn"]
				k2c_info["k2c_busid"]=bus_id.replace(".","")
				mapping_list.append(k2c_info)
				break
	if self.devicecount==len(mapping_list):
		print mapping_list
	elif self.devicecount>len(mapping_list):
		for i in range(self.devicecount):
			has=False
			for map in mapping_list:
				if i==map["slot_index"]:
					has=True
					break
			if not has:
				mapping_list.append({"k2c_sn":"","k2c_busid":"","slot_index":i})
			
		print mapping_list
		#mapping=lambda x:x["slot_index"]
		#print mapping
		#print "ERROR"
	self._fd = open("MappingIndex.py", "w+")
	self._fd.write("mapping_list=%s" %str(mapping_list))
	self._fd.close()
	print "#i PASSED"
		

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [option])")
    parser.add_option("-c", "--cardcount", \
                      action="store", \
                      dest="cardcount", \
                      default="4", \
                      help="card count")
    (options, args) = parser.parse_args()

    if len( args ) != 0:
        parser.error("wrong number of arguments")
        sys.exit(1)


    test = UTS_MapBusid(int(options.cardcount))
    result = test.Start()
