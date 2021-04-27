import smbus
import time
import os
import atexit
import RPi.GPIO as GPIO

class SMBUSBatt():
    def __init__(self):        
        self.address = 0x0b
        self.alarms = []
        self.connect(1)

    def connect(self, bus):
        try:
            self.bus = smbus.SMBus(bus)
            time.sleep(0.5)
            return True
        except:
            print("Connection to SMBUS failed")
            return False

    def write_byte(self, register, value):
        self.bus.write_byte_data(self.address, register, value);

    def read_word(self, register):
        try:
            data = self.bus.read_word_data(self.address, register)
        except:
            data = None
        return data

    def get_voltage(self):
        """Returns Voltage in mV"""
        register = 0x09
        value = self.read_word(register)
        return (value)
    
    def get_current(self):
        """Returns Current in mA"""
        register = 0x0a
        value = self.read_word(register)
        try:
            value = 65635 - value
        except:
            print ("stoerung")
        return (value)
    
    def get_relative_charge(self):
        """Returns ChargeState in percent of full"""
        register = 0x0d
        value = self.read_word(register)
        return (value)

    def get_time_to_empty(self):
        """Returns Time to empty in min"""
        register = 0x11
        value = self.read_word(register)
        return (value)

    def get_time_to_full(self):
        """Returns Time to full in min"""
        register = 0x13
        value = self.read_word(register)
        return (value)

if __name__ == "__main__":

    batt = SMBUSBatt()
 
    while True:
        os.system("clear")
        print("Volage:  " + str(batt.get_voltage()))
        print("Current: " + str(batt.get_current()))
        print("State:   " + str(batt.get_relative_charge()))
        print("Empty in:" + str(batt.get_time_to_empty()))
        print("Full in: " + str(batt.get_time_to_full()))
        print("OS Time: " + str(time.asctime()))
        time.sleep(5)
        if str(batt.get_relative_charge()) > "80":
            print('\a')







      
