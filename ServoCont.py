#! python
# -*- coding: utf-8 -*-
# Programm Setzt PWM Signal für zwei Servos in PIC16F88

from time import sleep
import smbus
bus = smbus.SMBus(1)

class Servo():
    def __init__(self, servo_corr1 = -20, servo_corr2 = -20):
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

    def get_analog(self):
        """Count pulse from Motor"""
        try:
            low = bus.read_byte_data(self.addr_pic, 0x07)  #Read PIC Register1 => CountsLowByte
            high = bus.read_byte_data(self.addr_pic, 0x08) #Read PIC Register1 => CountsHighByte
            analog = self.bits_to_int(low, high)          
        except:
            analog = 0
            print("Analog " +str(self.addr_pic) + " not ready")
        return (analog)

    def bits_to_int(self, low, high):
        value = (high << 8) + low
        if value > 32767:
            value = (65536 - value) * (-1)
        return(value)


if __name__ == "__main__":

    servo = Servo()

    servo.set_servo_angle(0)
    print("Servo to ...")
    sleep(3)  
    servo.set_servo_angle(10)
    print("Servo to ...")
    sleep(3)

    for i in range(10):
        print("Analog Value from PortA-4: " + str(servo.get_analog()))
        sleep(0.5)
