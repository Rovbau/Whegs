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

    def read_byte(self, register):
        for i in range(2):
            try:
                data = bus.read_byte_data(self.adresse,register)
                break
            except:
                print("Kompass not ready")
                data = None
        return(data)

    def get_pitch(self):
        data = self.read_byte(0x04)

        if data > 127:
            data = (255 - data) * (-1)
        return(data)

    def get_roll(self):
        try:
            data = self.read_byte(0x05)
        except:
            print("Kompass not ready")
            return(None)
        if data > 127:
            data = (255 - data) * (-1)
        return(data)

    def get_heading(self):
        """Returns KompassKurs"""
        kurs = 0

        daten1 = self.read_byte(0x02)
        daten2 = self.read_byte(0x03)

        kurs = (daten1<<8) + daten2
        kurs = kurs/10
        kurs = int(360 - kurs)
        return(kurs)

if __name__ == "__main__":

    kompass = Kompass()
    print("Starte")

    while True:
        print("Heading: " +str(kompass.get_heading()))
        print("Pitch: "   +str(kompass.get_pitch()))
        print("Roll: "    +str(kompass.get_roll()))
        sleep(1)

