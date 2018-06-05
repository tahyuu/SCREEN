#!/usr/bin/env python
import os,  subprocess, time
from Log import *
import ConfigParser	
from optparse import OptionParser
import pexpect
import commands
import random
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

class SCREEN():
    def __init__(self,index):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read("config.ini")
        self.PROMPT = ">"
        self.bc=bcolors()
        self.home_dir = os.getcwd()
        self.testIndex=index
        self.mac_re="[0-9A-Fa-f]{12}$"
        self.sn_re="\w{9}$"
        self.temp_re="^(\-|\+)?\d+(\.\d+)?$"
        self.ip_re="((25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))"
        self.dhcp_server=self.cf.get("DHCP", "dhcp_server")
        self.dhcp_leases_root=self.cf.get("DHCP", "dhcp_leases_root")
        self.dhcp_username=self.cf.get("DHCP", "dhcp_user_name")
        self.dhcp_password=self.cf.get("DHCP", "dhcp_password")
        self.bmc_username=self.cf.get("BMC", "bmc_user_name")
        self.bmc_password=self.cf.get("BMC", "bmc_password")
        self.wait_time=int(self.cf.get("CHECK", "wait_time"))
        self.input_temp_high=float(self.cf.get("CHECK", "input_temp_high"))
        self.input_temp_low=float(self.cf.get("CHECK", "input_temp_low"))
        self.bmc_ip=""
        self.bmc_mac=""
        self.serial_number=""
        self.bmc_command_header="ipmitool -I lanplus -H %s -U %s -P %s %s"
        self.pass_qut=self.cf.get("CHECK", "pass_margin")
        self.bmc_ip_get_type=self.cf.get("BMC", "bmc_ip_get_type")
        self.amb_sensores={}
        self.fru_update_status="FAIL"
        
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
        #self.f = subprocess.Popen(cmdAsciiStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.f = subprocess.Popen(cmdAsciiStr, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        tmp = "Send = %s" %cmdAsciiStr
        #self.log.Print(tmp)
    def RecvTerminatedBy(self,timeout=3):
        t_beginning = time.time()
        seconds_passed = 0
        while True:
            if self.f.poll() is not None:
                break
            seconds_passed = time.time() - t_beginning
            if timeout and seconds_passed > timeout:
                self.f.terminate()
                print "Communicate timeout!!!!"
            time.sleep(0.01)
        return self.f.stdout.read()

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
        command ="scp -rq -o StrictHostKeyChecking=no %s@%s:%s dhcpd.leases" %(self.dhcp_username,self.dhcp_server,self.dhcp_leases_root)
        child = pexpect.spawn(command)
        index = child.expect(["(?i)password", pexpect.EOF, pexpect.TIMEOUT])
        child.sendline("%s" %self.dhcp_password)
        child.read()
       
        #step 2 get ipaddress from dhcp release
        command="./list_dhcp_leases --lease dhcpd.leases | grep -i '%s'" %self.bmc_mac
	print command
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
        
    def ScanData(self):
        ########################################
        #to create test log and ask SN and MAC
        ########################################
        while True:
            self.serial_number = raw_input("[Slot %s] Please Input Serial Number : " %self.testIndex)
            p = re.compile(self.sn_re)
            if p.match(self.serial_number):
                break
        if self.bmc_ip_get_type=="0":
            while True:
                self.bmc_mac = raw_input("[Slot %s]  Please Input MAC Address : " %self.testIndex).replace(":","")
                p = re.compile(self.mac_re)
                if p.match(self.bmc_mac):
                    self.bmc_mac=":".join(re.findall("[0-9a-fA-F]{2}",self.bmc_mac))
                    break
        else:
            while True:
                self.bmc_ip= raw_input("Please Input MAC IP Address : ")
                p = re.compile(self.ip_re)
                if p.match(self.bmc_ip):
                    break
    def InitLog(self):
        self.testDate = datetime.now().strftime("%Y/%m/%d")
        self.testStartTime = datetime.now().strftime("%Y/%m/%d %H:%M")
        self.log_filename = self.serial_number + \
         '-' + datetime.now().strftime("%Y%m%d%H%M%S") + '.log'
        self.log.Open(self.home_dir + '//FTLog//TMP//' + self.log_filename)
        self.log.PrintNoTime('')
        self.log.PrintNoTime('#########################################################')
        self.log.PrintNoTime('Station : SCREEN')
        self.log.PrintNoTime('Date    : ' + self.testDate)
        self.log.PrintNoTime('SN      : %s' %self.serial_number)
        self.log.PrintNoTime('BMC MAC : %s' %self.bmc_mac)
        self.log.PrintNoTime('#########################################################')
        self.log.PrintNoTime('')
    def GetIpaddres(self):
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
    def Run(self):
        ########################################
        #to get  check AMB Temperature
        ########################################
        self.UpdateFru()
        self.AMBTest(0,True) 
        self.AMBTest(1,True) 
        self.AMBTest(4,True)
        if len(self.ErrorList)==0:
            self.testStatus=True
            self.log.PrintNoTime("")
            self.log.PrintNoTime("")
            self.log.Print("********************************************************")
            self.log.Print("ALL PASSED")
            self.log.Print("********************************************************")
            print self.bc.BGPASS(self.PASS)
            movePASS='mv ' + self.home_dir + '/FTLog/TMP/' + self.log_filename + \
                   ' ' + self.home_dir + '/FTLog/PASS/' + self.log_filename
            print self.bc.BGPASS(self.home_dir + '/FTLog/PASS/' + self.log_filename)
            os.system(movePASS)
        else:
            self.testStatus=False
            self.log.PrintNoTime("")
            self.log.PrintNoTime("")
            self.log.Print("********************************************************")
            self.log.Print("Test FAILED. %s HAS/HAVE ERROR" %(",".join(self.ErrorList)))
            self.log.Print("********************************************************")
            print self.bc.BGFAIL(self.FAIL)
            moveFAIL='mv ' + self.home_dir + '/FTLog/TMP/' + self.log_filename + \
                   ' ' + self.home_dir + '/FTLog/FAIL/' + self.log_filename
            self.bc.BGFAIL(self.home_dir + '/FTLog/FAIL/' + self.log_filename)
            print self.bc.BGFAIL(self.home_dir + '/FTLog/FAIL/' + self.log_filename)
            os.system(moveFAIL)
    def Run2(self):
        #self.UpdateFru()
        self.AMBTest(0,False) 
        time.sleep(random.uniform(0,0.1))
        self.AMBTest(1,False) 
        time.sleep(random.uniform(0,0.1))
        self.AMBTest(4,False)
    def Wait(self,seconds):
        count=0
        while (count < seconds):
            ncount = seconds - count
            sys.stdout.write("\r            %d " % ncount)
            sys.stdout.flush()
            time.sleep(1)
            count += 1
        while True:
            yes_no= raw_input("\nDo you want to start test[y/n]? : ")
            if str.upper(yes_no)=="Y" or str.upper(yes_no)=="YES":
                break
            else:
                pass
            
    def UpdateFru(self):
        #update fru
        fru_update_cmd="fru edit 0 field b 3 MP-00033236-010"
        update_command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,fru_update_cmd)
        for i in range(5):
            time.sleep(5)
            self.SendReturn(update_command)
            line=self.RecvTerminatedBy()
            self.log.Print(line)
            #check fru
            fru_update_cmd="fru"
            check_command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,fru_update_cmd)
            self.SendReturn(check_command)
            line=self.RecvTerminatedBy()
            self.log.Print(line)
            if line.find("Board Part Number     : MP-00033236-010")>=0:
                self.log.Print("update FRU sucess")
                self.fru_update_status="PASS"
                break
            else:
                self.log.Print("update FRU failed")

    def AMBTest(self,amb_index,askInput):
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
        if askInput:
            while True:
                str_amb_temp= raw_input("Please input AMB %s Sensor Temperature : " %amb_index)
                p = re.compile("^(\-|\+)?\d+(\.\d+)?$")
                if p.match(str_amb_temp):
		    if float(str_amb_temp)<=self.input_temp_high and self.input_temp_low<=float(str_amb_temp):
                    	break
		    else:
            	    	print self.bc.BGFAIL("input temp not in range [%s, %s]" %(self.input_temp_low,self.input_temp_high))
		else:
            	    print self.bc.BGFAIL("please input correct digital")
        else:
            str_amb_temp="30"

        test=""
        i=0
        while i<5:
            command=self.bmc_command_header %(self.bmc_ip,self.bmc_username,self.bmc_password,amb_cmd)
            self.SendReturn(command)
            test=self.RecvTerminatedBy().strip()
            if test.find("Communicate timeout")>=0:
                continue
            else:
                break
        try:
            real_temp=float(int(test.replace(" ","")[:3],16))/16
        except:
            real_temp="NA"
            test="NA"
        self.amb_sensores["amb%s_read_raw_data" %amb_index]=test
        self.amb_sensores["amb%s_read_temp" %amb_index]=real_temp
        self.amb_sensores["amb%s_real_temp" %amb_index]=str_amb_temp
        if not askInput:
            return True
        self.log.Print("SYS_AMB_TEMP_%s raw data is[ %s ]; temperature in IC is [ %s degrees C ]; temperature sensor read value is [%s degrees C]" %(amb_index,test,real_temp,str_amb_temp))
        amb_temp=float(str_amb_temp)
        if amb_temp-int(self.pass_qut) <= real_temp and real_temp<=amb_temp+int(self.pass_qut):
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
    while True:
        cre=SCREEN(1)
        cre.ScanData()
        cre.Wait(cre.wait_time)
        cre.InitLog()
        cre.GetIpaddres()
        cre.Run()
        write_str=""
        #write_str="serial_number,amb_0_ic_raw,amb_0_ic_read_temp,amb_0_ic_real_temp,amb_0_differ,amb_1_ic_raw,amb_1_ic_read_temp,amb_1__ic_real_temp,amb_1_differ,amb_4_ic_raw,amb_4_ic_read_temp,amb_4_ic_real_temp,amb_4_differ\n"
        write_str=write_str+cre.testStartTime+","
        write_str=write_str+cre.serial_number+","
        for amb_index in [0,1,4]:
            write_str=write_str+str(cre.amb_sensores["amb%s_read_raw_data" %amb_index])+","
            write_str=write_str+str(cre.amb_sensores["amb%s_read_temp" %amb_index])+","
            write_str=write_str+str(cre.amb_sensores["amb%s_real_temp" %amb_index])+","
            write_str=write_str+str(float(cre.amb_sensores["amb%s_real_temp" %amb_index])-float(cre.amb_sensores["amb%s_read_temp" %amb_index]))+","
        write_str=write_str+(cre.testStatus and "pass" or "fail")
        log=Log()
        log.Open3('data.csv')
        log.PrintNoTime(write_str.strip(","))
            
