#! python
# -*- coding: utf-8 -*-
# Programm Setzt PWM Signal für zwei Servos in PIC16F88

from time import sleep
import smbus
bus = smbus.SMBus(1)
import random


class Servo():
    def __init__(self, servo_corr1 = 35, servo_corr2 = 35):
        self.addr_pic = 0x19
        self.servo_corr1 = servo_corr1
        self.servo_corr2 = servo_corr2

    def set_servo_angle(self, servo_angle1 = 0, servo_angle2 = 0):
        servo_angle1 = 90 + self.servo_corr1 + servo_angle1 * (-1)
        servo_angle2 = 90 + self.servo_corr2 + servo_angle2 * (-1)
        #servo_angle1 = 35  #120mitte 225rechts 35links
        try:
            bus.write_byte_data(self.addr_pic, int(servo_angle1), int(servo_angle2))
        except:
            print("Servo not ready")


if __name__ == "__main__":
    y = 0
    servo = Servo()
    while True:
        value = int(raw_input("Value"))
        dir = int(raw_input("Dir"))
#    bus.write_byte_data(0x19, 128,value)
        #dir = 128
        #value = random.randrange(10,100)
        print(value)
        bus.write_byte_data(0x19,dir,value)
        bus.write_byte_data(0x1a,dir,value)
        bus.write_byte_data(0x1b,128,value+90)
        bus.write_byte_data(0x1c,128,value+90)
        sleep(1)
    
        #bus.write_byte_data(0x19, 10,10)
        #sleep(0.1)
        #x = bus.read_byte_data(0x1a, 0x01)
        print("Counting:")
        print(x)
        #y = y + x
	#if y > 6000:
        #print("d")
        #sleep(0.05)
        #     bus.write_byte_data(0x19, 255, 255)
        #sleep(1.11) #servo.set_servo_angle(40,20)
    sleep(5)
    for i in range(0,255):
        bus.write_byte_data(0x19,i, i)
        sleep(0.2)
        print(i)
    #servo.set_servo_angle(150,170)
    #sleep(5)
    #servo.set_servo_angle(230,250)
