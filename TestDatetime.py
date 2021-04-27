from time import time, clock, sleep
from datetime import timedelta
import RPi.GPIO as GPIO
import datetime as dt

GPIO.setmode(GPIO.BOARD)
GPIO.setup(37,GPIO.OUT)

GPIO.output(37, False)
d = timedelta(microseconds = 200)
#print(perf_counter())
print(time())
while True:
##    n2=dt.datetime.now()
##    while (dt.datetime.now() - n2) < d:
##        pass
    sleep(0.005)
    GPIO.output(37, True)
    sleep(0.1)
    GPIO.output(37, False)


