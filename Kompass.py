#!/usr/bin/env python
#-*- coding: utf-8 -*-

#import RPi.GPIO as GPIO
#GPIO.setwarnings(False)

import smbus
from time import *
bus = smbus.SMBus(1)

class Kompass():
    def __init__ (self):
        self.adresse = 0x61

    def get_pitch(self):
        try:
            data = bus.read_byte_data(self.adresse,0x04)
        except:
            print("Kompass not ready")
            return(None)
        if data > 127:
            data = (255 - data) * (-1)
        return(data)

    def get_roll(self):
        try:
            data = bus.read_byte_data(self.adresse,0x05)
        except:
            print("Kompass not ready")
            return(None)
        if data > 127:
            data = (255 - data) * (-1)
        return(data)

    def get_heading(self):
        """Returns KompassKurs"""
        kurs = 0
        #try:
        daten1 = bus.read_byte_data(self.adresse,0x02)
        daten2 = bus.read_byte_data(self.adresse,0x03)
        #except:
         #   print("Kompass not ready")
          #  return(None)
        kurs = (daten1<<8) + daten2
        kurs = kurs/10
        kurs = 360 - kurs
        return(kurs)

if __name__ == "__main__":

    kompass = Kompass()

    while True:
        print("Starte")
        print(kompass.get_heading())
        print(kompass.get_pitch())
        print(kompass.get_roll())
        sleep(1)

