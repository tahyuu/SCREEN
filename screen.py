#!/usr/bin/env python
import os,  subprocess, time
from Log import *
import ConfigParser	
from optparse import OptionParser
import pexpect
import commands
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

class CREEN():
    def __init__(self):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read("config.ini")
        self.PROMPT = ">"
        self.bc=bcolors()
        self.mac_re="[0-9A-Fa-f]{12}$"
        self.sn_re="\w{9}$"
        self.temp_re="^(\-|\+)?\d+(\.\d+)?$"
        self.ip_re="((25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))"
        self.dhcp_server=self.cf.get("DHCP", "dhcp_server")
        self.bmc_username=self.cf.get("BMC", "bmc_user_name")
        self.bmc_password=self.cf.get("BMC", "bmc_password")
        self.bmc_ip=""
        self.bmc_mac=""
        self.serial_number=""
        self.bmc_command_header="ipmitool -I lanplus -H %s -U %s -P %s %s"
        self.pass_qut=self.cf.get("CHECK", "pass_margin")
        self.bmc_ip_get_type=self.cf.get("BMC", "bmc_ip_get_type")
        
        self.PASS = '\n \
***************************************************\n \
  #########       ##        #########   #########  \n \
  ##      ##    ##  ##     ##          ##          \n \
  ##      ##   ##    ##    ##          ##          \n \
  #########   ## #### ##    ########    ########   \n \
  ##          ##      ##           ##          ##  \n \
  ##          ##      ##           ##          ##  \n \
  ##          ##      ##   #########   #########   \n \
***************************************************\n'

        self.FAIL = '\n \
***************************************************\n \
  ##########      ##         ######    ##          \n \
  ##            ##  ##         ##      ##          \n \
  ##           ##    ##        ##      ##          \n \
  ########    ## #### ##       ##      ##          \n \
  ##          ##      ##       ##      ##          \n \
  ##          ##      ##       ##      ##          \n \
  ##          ##      ##     ######    #########   \n \
***************************************************\n'
        self.log=Log()
    def SendReturn(self, cmdAsciiStr):
        self.f = subprocess.Popen(cmdAsciiStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        tmp = "Send = "+cmdAsciiStr
        #print tmp
        self.log.Print(tmp)
    def RecvTerminatedBy(self, *prompt_ptr):
        if len(prompt_ptr) == 0:
            prompt = self.PROMPT
        else:
            prompt = prompt_ptr[0]
        #print 'Rece = '
        self.log.Print("Rece = ")
        stdout = ''
        while self.f.poll() == None:
            stdout_line = self.f.stdout.readline()
            stdout = stdout + stdout_line
            if stdout_line != '':
                #print stdout_line,
                self.log.PrintNoTime(stdout_line.rstrip())
        else:
            stdout_lines = self.f.stdout.read()
            stdout = stdout + stdout_lines
            if stdout_lines != '':
                #print stdout_lines,
                self.log.PrintNoTime(stdout_lines[0:-1])

        if stdout != '':
            return stdout
            #print stdout_lines,
        else:
            stderr = self.f.stderr.read()
            #print stderr,
            self.log.PrintNoTime(stderr.rstrip())
            return stderr
    def PingHost(self,host):
        #step 1 ping dhcp server
        self.ping_wait=30
        while True:
            backinfo = commands.getstatusoutput('ping -c 2 -w %s %s'%(self.ping_wait,host))
            print backinfo[1]
            if backinfo[1].find(", 0% packet loss")<0:
                print self.bc.BGFAIL("make sure you can ping %s.\n" %(host))
                #sys.exit(0)
            else:
                break
    def GetDHCPIPAddress(self):
        #step 1 copy dhcp.release
        command ="scp -rq dhcp@%s:dhcpd.leases /u2/utssrc/SCREEN/dhcpd.leases" %self.dhcp_server
        child = pexpect.spawn(command)
        index = child.expect(["(?i)password", pexpect.EOF, pexpect.TIMEOUT])
        child.sendline("dhcp")
        child.read()
        
        #step 2 get ipaddress from dhcp release
        command="list_dhcp_leases --lease dhcpd.leases | grep -i '%s'" %self.bmc_mac
        self.SendReturn(command)
        str_ipaddr =self.RecvTerminatedBy()
        p = re.compile(self.ip_re)
        m = p.search(str_ipaddr)
        if m:
            self.bmc_ip=m.group()
            return True
        else:
            print self.bc.BGFAIL("can't find mac [%s] in dhcp.release will try later." %(self.bmc_mac))
            return False
        
    def Run(self):
        ########################################
        #to create test log and ask SN and MAC
        ########################################
        home_dir = "//u2//utssrc//SCREEN"
        self.testDate = datetime.now().strftime("%Y/%m/%d")
        serial_number=""
        bmc_mac=""
        while True:
            serial_number = raw_input("Please Input Serial Number : ")
            p = re.compile(self.sn_re)
            if p.match(serial_number):
                self.serial_number=serial_number
                break
        if self.bmc_ip_get_type=="0":
            while True:
                bmc_mac = raw_input("  Please Input MAC Address : ")
                p = re.compile(self.mac_re)
                if p.match(bmc_mac):
                    self.bmc_mac=":".join(re.findall("[0-9a-fA-F]{2}",bmc_mac))
                    break
        else:
            while True:
                bmc_ipaddress = raw_input("Please Input MAC IP Address : ")
                p = re.compile(self.ip_re)
                if p.match(bmc_ipaddress):
                    self.bmc_ip=bmc_ipaddress 
                    break
        self.log_filename = serial_number + \
         '-' + datetime.now().strftime("%Y%m%d%H%M%S") + '.log'
        self.log.Open(home_dir + '//FTLog//TMP//' + self.log_filename)
        self.log.PrintNoTime('')
        self.log.PrintNoTime('#########################################################')
        self.log.PrintNoTime('Station : SCREEN')
        self.log.PrintNoTime('Date    : ' + self.testDate)
        self.log.PrintNoTime('SN      : %s' %self.serial_number)
        self.log.PrintNoTime('BMC MAC : %s' %self.bmc_mac)
        self.log.PrintNoTime('#########################################################')
        self.log.PrintNoTime('')
        ########################################
        #to get dchp ipaddress for current mac
        ########################################
        if self.bmc_ip_get_type=="0":
            self.PingHost(self.dhcp_server)
            while True:
                if self.GetDHCPIPAddress():
                    break
                else:
                    time.sleep(5)
        else:
            self.PingHost(self.bmc_ip)
        self.ErrorList=[]
        ########################################
        #to get  check AMB Temperature
        ########################################
        self.AMBTest(0) 
        self.AMBTest(1) 
        self.AMBTest(4)
        if len(self.ErrorList)==0:
            self.log.PrintNoTime("")
            self.log.PrintNoTime("")
            self.log.Print("********************************************************")
            self.log.Print("ALL PASSED")
            self.log.Print("********************************************************")
            print self.bc.BGPASS(self.PASS)
            movePASS='mv ' + home_dir + '/FTLog/TMP/' + self.log_filename + \
                   ' ' + home_dir + '/FTLog/PASS/' + self.log_filename
            print self.bc.BGPASS(home_dir + '/FTLog/PASS/' + self.log_filename)
            os.system(movePASS)
        else:
            self.log.PrintNoTime("")
            self.log.PrintNoTime("")
            self.log.Print("********************************************************")
            self.log.Print("Test FAILED. %s HAS/HAVE ERROR" %(",".join(self.ErrorList)))
            self.log.Print("********************************************************")
            print self.bc.BGFAIL(self.FAIL)
            moveFAIL='mv ' + home_dir + '/FTLog/TMP/' + self.log_filename + \
                   ' ' + home_dir + '/FTLog/FAIL/' + self.log_filename
            self.bc.BGFAIL(home_dir + '/FTLog/FAIL/' + self.log_filename)
            os.system(moveFAIL)
            

    def AMBTest(self,amb_index):
        #commmand for get AMB0 
        if amb_index==0:
            amb_address="92"
        elif amb_index==1:
            amb_address="94"
        elif amb_index==4:
            amb_address="90"
        else:
            return False
            self.log.Print("wrong AMB index, it should be 0,1,4")
        self.log.PrintNoTime("")
        self.log.PrintNoTime("")
        self.log.Print("********************************************************")
        self.log.Print("AMB_%s test section" %amb_index)
        self.log.Print("********************************************************")
        amb_cmd="raw 0x06 0x52 0x0d 0x%s 0x02 0x00" %amb_address
        while True:
            str_amb_temp= raw_input("Please input AMB %s Sensor Temperature : " %amb_index)
            p = re.compile("^(\-|\+)?\d+(\.\d+)?$")
            if p.match(str_amb_temp):
                break

        command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,amb_cmd)
        self.SendReturn(command)
        test=self.RecvTerminatedBy().strip()
        real_temp=float(int(test.replace(" ","")[:3],16))/16
        self.log.Print("SYS_AMB_TEMP_%s raw data is[ %s ]; temperature in IC is [ %s degrees C ]; temperature sensor read value is [%s degrees C]" %(amb_index,test,real_temp,str_amb_temp))
        amb_temp=float(str_amb_temp)
        if amb_temp-int(self.pass_qut) < real_temp and real_temp<amb_temp+int(self.pass_qut):
            self.log.Print("SYS_AMB_TEMP_%s temperature [ %s degrees C] is in range [ %s degrees C,%s degrees C]" %(amb_index,real_temp,amb_temp-int(self.pass_qut),amb_temp+int(self.pass_qut)))
            self.log.Print("AMB_%s test PASSED" %amb_index)
            print self.bc.BGPASS("PASSED: SYS_AMB_TEMP_%s temperature [ %s degrees C] is in range [ %s degrees C,%s degrees C]" %(amb_index,real_temp,amb_temp-int(self.pass_qut),amb_temp+int(self.pass_qut)))
            return True
        else:
            self.log.Print("SYS_AMB_TEMP_%s temperature [ %s degrees C] is out of range [ %s degrees C,%s degrees C]" %(amb_index,real_temp,amb_temp-int(self.pass_qut),amb_temp+int(self.pass_qut)))
            self.log.Print("AMB_%s test FAILED" %amb_index)
            self.ErrorList.append("SYS_AMB_TEMP_%s" %amb_index)
            print self.bc.BGFAIL("FAILED: SYS_AMB_TEMP_%s temperature [ %s degrees C] is out of range [ %s degrees C,%s degrees C]" %(amb_index,real_temp,amb_temp-int(self.pass_qut),amb_temp+int(self.pass_qut)))
            return False
        
if __name__=="__main__":
    cre=CREEN()
    cre.log.Open("test.log")
    #cre.GetDHCPIPAddress()
    #cre.Run()
    while True:
        cre.Run()
