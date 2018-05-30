#!/usr/bin/env python 
# -*- coding: utf-8 -*-
from multiprocessing import Process
import  os  
import  sys
import  tty, termios
import time    


def fun():
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
            print "shutdown!"
            break
        elif ord(ch)==0x3:
            print "shutdown"
            break
        print 'press Q or ctrl+c to quit'
        #rate.sleep()
if __name__ == '__main__':
    p = Process(target=fun)
    p.start()
    p.join()
