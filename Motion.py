#! python
# -*- coding: utf-8 -*-
# Program steuert Roboter Motion via 4xMotorController
# Steer Links = +1 Rechts = -1
# Speed Vor = +1 Retour = -1

from MotorController import *
from time import *

class Motion():
    def __init__(self):
        self.em_stop = False
        self.motor_VL = MotorController(0x19)
        self.motor_VR = MotorController(0x1B)
        self.motor_HL = MotorController(0x1A)
        self.motor_HR = MotorController(0x1C)

        self.settings_VL = 0,0
        self.settings_VR = 0,0
        self.settings_HL = 0,0
        self.settings_HR = 0,0

        self.speed = 0
    
    def set_motion(self, steer, speed):
        """Set the 4 Motors speed and direction according steer, speed values"""
        steer = max(min(1.0,steer), -1.0)
        self.speed = max(min(1.0,speed), -1.0)
        
        if abs(steer) < 0.1:        #settings_xy is motorspeed, direction
            self.settings_VL = 1, 1
            self.settings_VR = 1, 1
            self.settings_HL = 1, 1
            self.settings_HR = 1, 1
        elif steer > 0 and steer < 0.7:    
            self.settings_VL = 1 - steer, 1
            self.settings_VR = 1, 1
            self.settings_HL = 1 - steer, 1
            self.settings_HR = 1, 1
        elif steer >= 0.7:
            self.settings_VL = 1, -1
            self.settings_VR = 1, 1
            self.settings_HL = 1, -1
            self.settings_HR = 1, 1 
        elif steer < 0 and steer > -0.7:    
            self.settings_VL = 1, 1
            self.settings_VR = 1 - abs(steer) , 1
            self.settings_HL = 1, 1
            self.settings_HR = 1 - abs(steer), 1
        elif steer <= -0.7:
            self.settings_VL = 1, 1
            self.settings_VR = 1, -1
            self.settings_HL = 1, 1
            self.settings_HR = 1, -1
        else:
            print("Error parsing speed Value")

        self.set_motorcontroller(self.motor_VL, self.settings_VL)
        self.set_motorcontroller(self.motor_VR, self.settings_VR)
        self.set_motorcontroller(self.motor_HL, self.settings_HL)
        self.set_motorcontroller(self.motor_HR, self.settings_HR)


    def set_motorcontroller(self, motor, settings):
        speed, direction = settings
        speed = speed  * self.speed
        if speed < 0:
            direction = direction * (-1)
        motor.set_motor(speed, direction)

    def stop(self, em_stop):
        self.em_stop = em_stop
        if self.em_stop == True:
            print("Error: EM-Stop Motor")
            
    def print_motion(self):
        print("%s %9.2f %9.2f" %("Motion: ",self.steer, self.speed))



if __name__ == "__main__":

    motion  = Motion()


    for i in range(10):
        print("Setting is: " + str(i / 10))
        motion.set_motion(i / 10 , 0.5)
        print()
        sleep(1)

    motion.set_motion(0,1)

##    print("Straigt")
##    motion.set_motion(0,1)
##    sleep(3)
##    print("Hard Right")
##    motion.set_motion(-0.6,1)
##    sleep(3)
##    print("Straigt")
##    motion.set_motion(0,1)
##    sleep(3)
##    print("Hard Left")
##    motion.set_motion(0.6,1)
##    sleep(3)
##    print("Straigt")
##    motion.set_motion(0,1)
##    sleep(3)
    


