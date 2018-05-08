#!/usr/bin/env python
import multiprocessing
import time

class Worker(multiprocessing.Process):
    def run(self):
        print "start %s" %self.name
        time.sleep(3)
        print 'In %s' % self.name
        return

if __name__ == '__main__':
    jobs = []
    for i in range(1,3):
        p = Worker()
        jobs.append(p)
        p.start()
    for j in jobs:
        j.join()
    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
