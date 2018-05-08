#!/usr/bin/env python
import time
import sys
count = 0
while (count < 10):
    ncount = 10 - count
    sys.stdout.write("\r%d " % ncount)
    sys.stdout.flush()
    time.sleep(1)
    count += 1
