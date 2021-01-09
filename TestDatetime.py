import os
from time import time, clock, sleep
sleep(1.02)
print(time())
sleep(0.005)
print(time())
from datetime import timedelta

import datetime as dt

n1=dt.datetime.now()
sleep(10.000)
#for i in range(100):
 #   pass
n2=dt.datetime.now()
print((n2-n1).microseconds)
print((n2-n1))
d = timedelta(microseconds = 500)
if n2-n1 > d:
    print("lahm")

