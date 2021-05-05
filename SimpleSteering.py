#! python
# -*- coding: utf-8 -*-

from threading import Thread
from time import *
import sys
from Kompass import *
#import msvcrt
#import getch
import smbus
bus = smbus.SMBus(1)

class Manuell():
    def __init__(self):
        self.left = 255
        self.right = 255
        self.step = 50
        self.dir_left = 128
        self.dir_right = 128
        print("Init Manuell")
        
    def limit(self, value):
        if value >= 255:
            value = 255
        if value <= 0:
            value = 0
        return(value)
        
        
    def runManuell(self):
        
        while True:
            #comm = msvcrt.getch()
            comm = sys.stdin.read(2)
            #comm = getch.getch()
            comm = comm[0]
            #comm = input()
            #print("Taste: "+str(comm))

            if comm == "7":
                self.left -= self.step
            elif comm == "1":
                self.left += self.step
            elif comm == "9":
                self.right -= self.step
            elif comm == "3":
                self.right += self.step
            elif comm == "8":
                self.left -= self.step
                self.right -= self.step
            elif comm == "2":
                self.left += self.step
                self.right += self.step
            elif comm == "4":
                self.dir_left = 127
            elif comm == "6":
                self.dir_right = 127
            elif comm == "5":
                self.left = 255
                self.right = 255
                self.dir_left = 128
                self.dir_right = 128
            else:
                self.left = 255
                self.right = 255

            self.left = self.limit(self.left)
            self.right = self.limit(self.right)

    def getManuellCommand(self):
        return(self.left, self.right, self.dir_left, self.dir_right)

if __name__ == "__main__":

    man = Manuell()
    kompass = Kompass()

    ThreadEncoder=Thread(target=man.runManuell,args=())
    ThreadEncoder.daemon=True
    ThreadEncoder.start()

    while True:
        left, right, dir_left, dir_right = man.getManuellCommand()
        print ("Left: " +str(left) + " Right: " +str(right) +
               "    Dir_L: " + str(dir_left) + " Dir_R: " + str(dir_right))

        pitch = kompass.get_pitch()
        roll = kompass.get_roll()
        heading = kompass.get_heading()
        print("Pitch is: " + str(pitch))
        print("Roll is: " + str(roll))
        print("Heading is: " + str(heading))
        if abs(pitch) > 10 or abs(roll) > 10:
            left = 255
            right = 255
        bus.write_byte_data(0x19, dir_left, left)
        bus.write_byte_data(0x1A, dir_left, left)
        bus.write_byte_data(0x1B, dir_right, right)
        bus.write_byte_data(0x1C, dir_right, right)
        print(bus.read_byte_data(0x19,0x05))
        print(bus.read_byte_data(0x19,0x06))
             
#  bus.write_byte_data(0x1C, dir_right, right)
        sleep(3)


