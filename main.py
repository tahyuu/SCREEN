#!/usr/bin/env python
import os,  subprocess, time
from Log import *
import ConfigParser	
from optparse import OptionParser
import pexpect
import commands
import multiprocessing
from multiprocessing import Process, Value, Array
from screen import *
class TestEngine(multiprocessing.Process):
    def Init(self,i):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read("config.ini")
        self.debug=i
        self.debug=self.cf.get("DEBUG", "debug")
        self.RunList=[]
        self.scr=SCREEN(i)
        if self.debug=="True":
            pass
            self.serial_number=self.cf.get("DEBUG", "serial_number_%s" %i)
            self.bmc_mac=self.cf.get("DEBUG", "bmc_mac_%s" %i)
        else:
            self.scr.ScanData()
        self.scr.InitLog()
    def run(self):
        self.scr.Run2()
        return
    def GetIpaddres(self):
        self.scr.GetIpaddres()
        return
            
        
if __name__=="__main__":
    jobs = []
    num = Value('d', 0.0)
    for i in range(1,3):
        p = TestEngine()
        p.Init(i)
        jobs.append(p)
    for p in jobs:
        p.GetIpaddres()
    for p in jobs:
        p.start()
    for p in jobs:
        p.join()
    print "Test End"

