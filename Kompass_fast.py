#!/usr/bin/env python
#-*- coding: utf-8 -*-

#import RPi.GPIO as GPIO
#GPIO.setwarnings(False)

# 6,7      Magnetometer X axis raw output, 16 bit signed integer with register 6 being the upper 8 bits
# 8,9      Magnetometer Y axis raw output, 16 bit signed integer with register 8 being the upper 8 bits
# 10,11    Magnetometer Z axis raw output, 16 bit signed integer with register 10 being the upper 8 bits

import smbus
from time import *
import math
bus = smbus.SMBus(1)

class Kompass():
    def __init__ (self):
        self.adresse = 0x61
        self.kompass_error_i2c = False

    def kompass_error(self):
        return(self.kompass_error_i2c)

    def read_byte(self, register):
        for i in range(2):
            try:
                data = bus.read_byte_data(self.adresse,register)
                kompass_error_i2c = False
                break
            except:
                print("Kompass not ready")
                kompass_error_i2c = True
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
            print("Kompass not ready - roll")
            return(None)
        if data > 127:
            data = (255 - data) * (-1)
        return(data)
    
    def get_raw_data(self):
        daten1 = self.read_byte(0x06)
        daten2 = self.read_byte(0x07)
        raw_x = (daten1<<8) + daten2
        if raw_x > 32767:
            raw_x = raw_x - 65536

        daten1 = self.read_byte(0x08)
        daten2 = self.read_byte(0x09)
        raw_y = (daten1<<8) + daten2
        if raw_y > 32767:
            raw_y = raw_y - 65536

        daten1 = self.read_byte(0x0A)
        daten2 = self.read_byte(0x0B)
        raw_z = (daten1<<8) + daten2
        if raw_z > 32767:
            raw_z = raw_z - 65536

        return(raw_x, raw_y, raw_z)

    def get_heading(self):
        """Returns KompassKurs"""
        kurs = 0

        daten1 = self.read_byte(0x02)
        daten2 = self.read_byte(0x03)

        kurs = (daten1<<8) + daten2
        kurs = kurs/10
        kurs = int(360 - kurs)
        return(kurs)

    def get_tilt_compensated_heading(self, mx, my, mz, roll_deg=0, pitch_deg=0):
        # 1. Winkel von Grad in Bogenmass (Radiant) umrechnen
        roll = math.radians(roll_deg)
        pitch = math.radians(pitch_deg)

        # 2. Neigungskompensierte Magnetfeldkomponenten (Xh, Yh) berechnen
        # Diese Formeln korrigieren die Achsen basierend auf der aktuellen Neigung
        xh = mx * math.cos(pitch) + mz * math.sin(pitch)
        yh = mx * math.sin(roll) * math.sin(pitch) + my * math.cos(roll) - mz * math.sin(roll) * math.cos(pitch)

        # 3. Kurs mit atan2 berechnen (liefert Wert zwischen -pi und pi)
        heading_rad = math.atan2(yh, xh)

        # 4. In Grad umrechnen und auf 0-360 Grad normalisieren
        heading_deg = math.degrees(heading_rad)
        if heading_deg < 0:
            heading_deg += 360
            
        return heading_deg




if __name__ == "__main__":

    kompass = Kompass()
    print("Starte")

    while True:
        start_time = time()
        print("----------")
        print("Heading: " +str(kompass.get_heading()))
        print("Pitch: "   +str(kompass.get_pitch()))
        print("Roll: "    +str(kompass.get_roll()))
        x, y, z = kompass.get_raw_data()
        print("raw_x: " + str(x) + " raw_y: " + str(y) + " raw_z: " + str(z))
        heading = kompass.get_tilt_compensated_heading(x, y, z, 0, 0)
        print("Heading raw: " + str(heading))
        
        sleep(1.05)
        print("Dauer: " + str(time() - start_time) + " Sekunden")
