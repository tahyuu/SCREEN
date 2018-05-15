#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,  subprocess, time
import  tty, termios
from Log import *
import ConfigParser	
from optparse import OptionParser
import pexpect
import commands
import multiprocessing
from multiprocessing import Process, Value, Array
from screen2 import *
class TestEngine(multiprocessing.Process):
    def Init(self,i,d,stoped):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read("config.ini")
        self.stoped=stoped
        self.debug=self.cf.get("DEBUG", "debug")
        self.RunList=[]
        self.ResultList=d
        self.scr=SCREEN(i)
        self.serial_number=self.scr.serial_number
        self.intermission=int(self.cf.get("MULTI","test_intermission"))
        self.startTime=""
        if self.debug=="True":
            self.scr.serial_number=self.cf.get("DEBUG", "serial_number_%s" %i)
            self.scr.bmc_mac=self.cf.get("DEBUG", "bmc_mac_%s" %i)
        else:
            self.scr.ScanData()
        self.scr.InitLog()
    def run(self):
        i=0
        while True:
            time.sleep(self.intermission)
            self.scr.Run2()
            self.scr.amb_sensores["serial_number"]=self.scr.serial_number
            self.scr.amb_sensores["test_start_time"]=self.scr.testStartTime
            self.scr.amb_sensores["test_index"]=i
            self.ResultList.append(self.scr.amb_sensores)
            i=i+1
            if self.stoped.value==1:
                break
    def SaveData(self):
        pass
        
    def GetIpaddres(self):
        self.scr.GetIpaddres()
        return
            
def stop_test(stop):
    print "stop"
    print 'press Q or ctrl+c to stop test'
    while True:
        fd=sys.stdin.fileno()
        old_settings=termios.tcgetattr(fd)
        #old_settings[3]= old_settings[3] & ~termios.ICANON & ~termios.ECHO  
        try:
            tty.setraw(fd)
            ch=sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  
            #print 'error'
        if ch=='q':
            print "test stoped!!"
            break
        elif ord(ch)==0x3:
            print "test stoped!!"
            break
        print 'press Q or ctrl+c to quit'
        #rate.sleep()
def Wait(seconds,stoped):
        count=0
        while (count < seconds):
            ncount = seconds - count
            sys.stdout.write("\r     the Program will stop in ------ %d s ------- " % ncount)
            sys.stdout.flush()
            time.sleep(1)
            count += 1
        stoped.value=1
        
        
if __name__=="__main__":
    mgr = multiprocessing.Manager()
    stoped = Value('d', 0.0)
    result_list = mgr.list()
    jobs = []
    for i in range(1,4):
        p = TestEngine()
        p.Init(i,result_list,stoped)
        jobs.append(p)
    for p in jobs:
        p.GetIpaddres()
    for p in jobs:
        p.start()
    p1 = Process(target=Wait, args=(30,stoped))
    p1.start()
    for p in jobs:
        p.join()
    write_str=""
    #to get SN list
    sn_list=[]
    index_list=[]
    for li in result_list:
        if sn_list.count(li["serial_number"])==0:
            sn_list.append(li["serial_number"])
        if index_list.count(li["test_index"])==0:
            index_list.append(li["test_index"])
    index_list.sort()
    for index in index_list:
        for sn in sn_list:
            for li in result_list:
                if li["test_index"]!=index:
                    continue
                if li["serial_number"]!=sn:
                    continue
                write_str=write_str+str(li["test_index"])+","
                write_str=write_str+str(li["serial_number"])+","
                write_str=write_str+str(li["test_start_time"])+","
                for amb_index in [0,1,4]:
                    write_str=write_str+str(li["amb%s_read_raw_data" %amb_index])+","
                    write_str=write_str+str(li["amb%s_read_temp" %amb_index])+","
        write_str=write_str.strip(",")+"\n"
    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    print "Test Log"
    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    print write_str.strip()
    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    log=Log()
    log.Open(datetime.now().strftime("%Y%m%d%H%M%S")+'.csv')
    log.PrintNoTime(write_str.strip())
    print "Test End"

