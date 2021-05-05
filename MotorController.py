#! python
# -*- coding: utf-8 -*-
# Programm setzt Motor speed via I2C

from time import sleep, time
import smbus
bus = smbus.SMBus(1)



class MotorController():
    def __init__(self, address):
        self.addr = address
        self.CountL = 0
        self.CountR = 0
        self.last_time = time()
        self.direction_old = 1
        
        print("Init MotorController " +str(self.addr))

    def bits_to_int(self, low, high):
        value = (high << 8) + low
        if value > 32767:
            value = (65536 - value) * (-1)
        return(value)

    def set_motor(self, speed, direction):
        """Set the motor speed and direction via i2c"""
        speed = 255 - speed * 255

        #if speed < 100: speed = 100      

        if self.direction_old != direction:
            self.direction_old = direction
            print(str(self.addr )+ "Change Direction")
            bus.write_byte_data(self.addr, int(direction), int(255))

        print("motor" + str(speed) + " " + str(direction))
        if direction == 1:
            direction = 127
        elif direction == -1:
            direction = 128
        else:
            print("Direction command fault")
        try:
            bus.write_byte_data(self.addr, int(direction), int(speed))
        except:
            print("Motor " +str(self.addr) + " not ready")

    def get_counts(self):
        """Count pulse from Motor"""
        try:
            low = bus.read_byte_data(self.addr,0x01)  #Read PIC Register1 => CountsLowByte
            high = bus.read_byte_data(self.addr,0x02) #Read PIC Register1 => CountsHighByte
            counts = self.bits_to_int(low, high)          
        except:
            counts = 0
            print("Counts " +str(self.addr) + " not ready")
        return (counts)

    def get_PWM(self):
        """Count pulse from Motor"""
        try:
            low = bus.read_byte_data(self.addr,0x05)  #Read PIC Register1 => CountsLowByte
            high = bus.read_byte_data(self.addr,0x06) #Read PIC Register1 => CountsHighByte
            PWM = self.bits_to_int(low, high)          
        except:
            PWM = 0
            print("PWM " +str(self.addr) + " not ready")
        return (PWM)

    def get_overcurrent(self):
        """clears L / R Counts"""
        try:
            low = bus.read_byte_data(self.addr,0x03)
            high = bus.read_byte_data(self.addr,0x04)
            overcurrent_value = self.bits_to_int(low, high)       
        except:
            overcurrent_value = 0
            print("Overcurrent " +str(self.addr) + " not ready")
        return (overcurrent_value)
    
    def clear_counts(self):
        """clears L / R Counts"""
        try:
            _ = bus.read_byte_data(self.addr,0x01)  #Dummy read to clear data
            _ = bus.read_byte_data(self.addr,0x02)
            self.counts = 0
            return (True)
        except:
            print("Counts " +str(self.addr) + " not cleared")
            return (False)


if __name__ == "__main__":

    motor_VL = MotorController(0x19)
    motor_VL.set_motor(speed = 255, direction = 1)
    print(motor_VL.get_counts())
    print(motor_VL.clear_counts())
    print(motor_VL.get_PWM())
    print(motor_VL.get_overcurrent())

