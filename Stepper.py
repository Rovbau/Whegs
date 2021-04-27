#! Python3

import RPi.GPIO as GPIO
import datetime as dt

from time import sleep, time, perf_counter
GPIO.setwarnings(False)


class Stepper():
    """Controls a Stepper Motor with the Modul A4988"""
    def __init__(self, name, angle_per_step, pin_dir, pin_step, actual):
        self.name = name
        self.angle_per_step = angle_per_step
        self.pin_dir = pin_dir
        self.pin_step = pin_step
        self.actual_steps = int(actual)
        self.last_step_time = time()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin_dir,GPIO.OUT)
        GPIO.setup(pin_step,GPIO.OUT)
        GPIO.output(pin_dir, False)
        GPIO.output(pin_step, False)

    def get_actual_angle(self):
        """Get the actual Motor Position in Degree"""
        return(self.actual_steps * self.angle_per_step)

    def set_actual_angle(self, actual_angle):
        """Set the actual Motor Position in Degree"""
        self.actual_steps = int(actual_angle / self.angle_per_step)
        
    def get_actual_steps(self):
        """Get the actual Motor Steps"""
        return(self.name, self.actual_steps)

    def set_actual_steps(self, actual_steps):
        """Set the actual Motor Steps"""
        self.actual_steps = int(actual_steps)
        
    def goto_angle(self, angle):
        """Set Motor to desired position. Input: angle"""
        steps = int(angle / self.angle_per_step)
        
        while steps != self.actual_steps:
            if steps >= self.actual_steps:
                self.do_step(1)
                self.actual_steps += 1
            else:
                self.do_step(-1)
                self.actual_steps -= 1
            
    def do_step(self, steps, speed = 0.007): #0.007
        """Do Motor Steps. +steps or -steps changes direction)"""
        if steps > 0:
            GPIO.output(self.pin_dir, True)
        elif steps < 0:
            GPIO.output(self.pin_dir, False)
        else:
            return
        
        for x in range(abs(steps)):
            GPIO.output(self.pin_step, False)
            if (perf_counter() - self.last_step_time) > speed:
                GPIO.output(self.pin_step, True)
            else:
                sleep(speed)
                GPIO.output(self.pin_step, True)
            self.last_step_time = perf_counter()
        self.last_step_time = perf_counter()

if __name__ == "__main__":
    
    stepper1 = Stepper("Heading", angle_per_step = 1.8, pin_dir = 35, pin_step = 37, actual=0)
    stepper1.set_actual_angle(45)
    stepper1.goto_angle(90)
    
    print(stepper1.get_actual_angle())

