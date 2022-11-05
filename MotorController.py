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
        speed = 255 - abs(speed) * 255

        if speed > 255 or speed < 0:
            print("MotorController Speed value failed")

        #Set Motor to Stop before direction change
        if self.direction_old != direction:
            self.direction_old = direction
            try:
                bus.write_byte_data(self.addr, int(direction), int(255))
                sleep(0.05)
            except:
                print("Motor " + str(self.addr) + "not ready")

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
            overcurrent_value = self.bits_to_int(low, high) # 1 == NO over_current
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
    motor_VR = MotorController(0x1B)
    motor_HL = MotorController(0x1A)
    motor_HR = MotorController(0x1C)

    #Go Robo go
    motor_VL.set_motor(speed = 100, direction = 1)   
    motor_VR.set_motor(speed = 80, direction = 1)   
    motor_HL.set_motor(speed = 100, direction = 1)   
    motor_HR.set_motor(speed = 120, direction = 1)

    sleep(20)

    #Stopping @ speed = 0
    motor_VL.set_motor(speed = 0, direction = 1)
    motor_VR.set_motor(speed = 0, direction = 1)
    motor_HL.set_motor(speed = 0, direction = 1)
    motor_HR.set_motor(speed = 0, direction = 1)

    print("Counts VL: " + str(motor_VL.get_counts()))
    print("Clear  VL: " + str(motor_VL.clear_counts()))
    print("PWM    VL: " + str(motor_VL.get_PWM()))
    print("OverCurVL: " + str(motor_VL.get_overcurrent()))
        
