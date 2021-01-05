import RPi.GPIO as GPIO
from time import sleep, time
GPIO.setwarnings(False)
#import datetime as dt

class Stepper():
    """Controls a Stepper Motor with the Modul A4988"""
    def __init__(self, name, mm_per_step, pin_dir, pin_step, actual):
        self.name = name
        self.mm_per_step = mm_per_step
        self.pin_dir = pin_dir
        self.pin_step = pin_step
        self.actual_steps = int(actual)
        self.last_step_time = time()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin_dir,GPIO.OUT)
        GPIO.setup(pin_step,GPIO.OUT)
        GPIO.output(pin_dir, False)
        GPIO.output(pin_step, False)

    def get_actual_steps(self):
        """Get the actual Motor Position"""
        return(self.name, self.actual_steps)

    def set_actual_steps(self, actual_steps):
        """Set the actual Motor Position"""
        self.actual_steps = actual_steps
        
    def goto_pos(self, lenght):
        """Set Motor to desired position. Input: lentht[mm]"""
        steps = int(lenght / self.mm_per_step)
        
        while steps != self.actual_steps:
            if steps >= self.actual_steps:
                self.do_step(1)
                self.actual_steps += 1
            else:
                self.do_step(-1)
                self.actual_steps -= 1
            
    def do_step(self, steps, speed = 0.01):
        """Do Motor Steps. +steps or -steps changes direction)"""
        if steps > 0:
            GPIO.output(self.pin_dir, True)
        elif steps < 0:
            GPIO.output(self.pin_dir, False)
        else:
            return
        
        for x in range(abs(steps)):
            GPIO.output(self.pin_step, False)
            if (time() - self.last_step_time) > speed:
                GPIO.output(self.pin_step, True)
            else:
                sleep(speed) #sleep must be >0.01s because of acurency x.xx
                GPIO.output(self.pin_step, True)
            self.last_step_time = time()
        self.last_step_time = time()

if __name__ == "__main__":
    
    stepper1 = Stepper("Left", mm_per_step = 0.10, pin_dir = 35, pin_step = 37, actual=0)
    stepper1.do_step(-20)
    stepper1.do_step(20)
    print(stepper1.get_actual_steps())

    #stepper2 = Stepper("Right", mm_per_step = 0.10, pin_dir = 31, pin_step = 33, actual = 0)
    #stepper2.goto_pos(-200)

    
