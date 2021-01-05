#! python
# -*- coding: utf-8 -*-

from time import sleep, time
from Stepper import *
from Lidar import *
from math import *

class Scanner():
    def __init__(self):
        self.stepper_heading = Stepper("Heading", mm_per_step = 1,
                                    pin_dir = 35, pin_step = 37, actual=0)
        self.stepper_pitch = Stepper("Pitch", mm_per_step = 1,
                                    pin_dir = 31, pin_step = 33, actual=0)
        self.lidar = Lidar()
        self.actual_steps = 0
        self.heading = 0
        self.pitch = 0
        self.line_direction = "CCW"
        self.vertical_direction = "DOWN"
        self.scan_data = []

    def do_3D_scan(self, step = 1, min_heading = -90, max_heading = 90,
                                   min_pitch = -1.8, max_pitch = 1.8):
        """Do a 3D Scan for maximal Stepper-Steps. INPUT: INT step, angle-limits""" 
        self.step = step
        
        while True:
            
            self.line_scan(min_heading, max_heading)
            print("line")

            if self.actual_steps >= self.step:
                break

            if self.vertical_direction == "UP":
                self.pitch = round(self.pitch + 1.8, 2)
                self.stepper_pitch.do_step(+1)
            else:
                self.pitch = round(self.pitch - 1.8, 2)
                self.stepper_pitch.do_step(-1)
                
            if (self.pitch >= max_pitch):
                self.vertical_direction = "DOWN"
            if (self.pitch <= min_pitch):
                self.vertical_direction = "UP"          
        self.actual_steps = 0            
                
    def line_scan(self, min_heading, max_heading):
        """Do a LIDAR - Scan one line, Maximal for total step"""
        while self.actual_steps < self.step:      
            self.actual_steps += 1

            dist = self.lidar.get_distance()    # zero if LIDAR error

            if dist > 10:
                self.scan_data.append([self.pitch, self.heading, dist])

            if self.line_direction == "CCW":
                if self.heading  < max_heading:
                    self.heading = round(self.heading + 1.8, 2)
                    self.stepper_heading.do_step(+1)
                else:
                    self.line_direction = "CW"
                    return
            else:
                if self.heading  > min_heading:
                    self.heading = round(self.heading - 1.8, 2)
                    self.stepper_heading.do_step(-1)
                else:
                    self.line_direction = "CCW"
                    return

    def polar_to_kartesian(self, dist, winkel):
        """returns aus Dist und Winkel Dx,Dy"""
        dx=int((dist*cos(radians(winkel))))
        dy=int((dist*sin(radians(winkel))))
        return(dx,dy)

    def get_scan_data(self):
        """RETURNS: LIST scan_data[pitch, heading, distance], clears data after"""
        data = self.scan_data
        self.scan_data = []
        return (data)

    def scanner_reset(self):
        """Move Steppers to init Pos. resets heading, pitch"""
        self.stepper_heading.do_step(int((-1) * self.heading / 1.8 ))
        self.stepper_pitch.do_step  (int((-1) * self.pitch / 1.8 ))
        self.heading = 0
        self.pitch = 0
        self.line_direction = "CCW"
        self.vertical_direction = "DOWN"
       
        
if __name__ == "__main__":
    scanner = Scanner()

    start = time.time()
    
    scanner.do_3D_scan(step = 180)
    (scanner.get_scan_data())
    scanner.scanner_reset()

    print("Scan takes: " +str(time.time()-start) +" sec")


