#! python
# -*- coding: utf-8 -*-

from time import sleep
import RPi.GPIO as GPIO

class Pumper():
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        self.pumper_L = 38
        self.pumper_R = 40
        self.pumper_rear_L = 16
        self.pumper_rear_R = 18
        GPIO.setup(self.pumper_L,GPIO.IN)
        GPIO.setup(self.pumper_R,GPIO.IN)
        GPIO.setup(self.pumper_rear_L,GPIO.IN)
        GPIO.setup(self.pumper_rear_R,GPIO.IN)

        self.led = 36
        GPIO.setup(self.led,GPIO.OUT)

    def em_stop(self):
        if self.get_pumper_status() == (False, False, False, False):
            return(False)
        else:
            return(True)
        
    def get_pumper_status(self):
        L = GPIO.input(self.pumper_L)
        R = GPIO.input(self.pumper_R)
        rL = GPIO.input(self.pumper_rear_L)
        rR = GPIO.input(self.pumper_rear_R)
        return(bool(L), bool(R), bool(rL), bool(rR))

    def status_led(self, status):
        if status == "on":
            GPIO.output(self.led, 1)
        elif status == "off":
            GPIO.output(self.led, 0)
        else:
            print("Error: status must be 'on' or 'off'")

if __name__ == "__main__":
    pumper = Pumper()
    pumper.status_led("on")
    while True:
        print(pumper.em_stop())
        sleep(0.5)
        pumper.status_led("off")
