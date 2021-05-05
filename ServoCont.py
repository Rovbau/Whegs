#! python
# -*- coding: utf-8 -*-
# Programm Setzt PWM Signal für zwei Servos in PIC16F88

from time import sleep
import smbus
bus = smbus.SMBus(1)



class Servo():
    def __init__(self, servo_corr1 = 35, servo_corr2 = 35):
        self.addr_pic = 0x18
        self.servo_corr1 = servo_corr1
        self.servo_corr2 = servo_corr2

    def set_servo_angle(self, servo_angle1):
        servo_angle1 = 90 + self.servo_corr1 + servo_angle1 * (-1)
        #servo_angle2 = 90 + self.servo_corr2 + servo_angle2 * (-1)
        #servo_angle1 = 35  #120mitte 225rechts 35links
        try:
            bus.write_byte_data(self.addr_pic, int(servo_angle1), int(servo_angle1))
        except:
            print("Servo not ready")


if __name__ == "__main__":

    servo = Servo()
    servo.set_servo_angle(0,0)
    sleep(5)
    
    servo.set_servo_angle(1,1)
    sleep(5)
    servo.set_servo_angle(2,2)
    sleep(5)
    servo.set_servo_angle(3,3)
