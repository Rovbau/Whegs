#! python
# -*- coding: utf-8 -*-

from time import sleep, time
from Stepper import *
from Lidar import *
from ServoCont import *
from math import *

class Scanner():
    def __init__(self):
        self.heading_step_size = 1.8
        self.pitch_step_size = 2.0
        self.stepper_heading = Stepper("Heading", angle_per_step = self.heading_step_size,
                                        pin_dir = 35, pin_step = 37, actual=0)
        self.servo_pitch  = Servo()    
        self.lidar = Lidar()
        self.actual_steps = 0
        self.heading = 0
        self.pitch = 0
        self.line_direction = "CCW"
        self.vertical_direction = "DOWN"
        self.local_data = []
        self.scan_data = []
        self.init_done = False

    def init_3D_scan(self, min_pitch, max_pitch, min_heading, max_heading, ):
        """Set the Stepper init values (no mechanical movement)"""
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        self.min_heading = min_heading
        self.max_heading = max_heading
        
        self.servo_pitch.set_servo_angle(self.min_pitch)
        self.pitch = self.min_pitch
        
        self.stepper_heading.set_actual_angle(self.min_heading)
        self.heading = self.min_heading

        #Stabilise
        sleep(0.2)
        self.init_done = True


    def do_3D_scan(self, step = 1 ):
        """Do a 3D Scan for maximal Stepper-Steps. INPUT: INT step, angle-limits"""
        if not self.init_done:
            print("Scanner3d Init nessesary!")

        while True:
            if self.actual_steps >= step:
                break
            
            self.actual_steps += 1

            self.line_scan(self.min_heading, self.max_heading)

            #sleep(1)
            
            if self.vertical_direction == "UP":
                self.pitch -= self.pitch_step_size
                self.servo_pitch.set_servo_angle(servo_angle1 = self.pitch)
            else:
                self.pitch += self.pitch_step_size
                self.servo_pitch.set_servo_angle(servo_angle1 = self.pitch)
                
            if (self.pitch <= self.min_pitch):
                self.vertical_direction = "DOWN"
            if (self.pitch >= self.max_pitch):
                self.vertical_direction = "UP"          
        self.actual_steps = 0            
                
    def line_scan(self, min_heading, max_heading):
        """Do a LIDAR - Scan one line, Maximal for total step"""

        while True:
            dist = self.lidar.get_distance()    # zero if LIDAR error
            print(dist)
            #sleep(2)
            self.local_data.append([self.pitch, self.heading, dist])
            
            if self.line_direction == "CCW":
                if self.heading  < self.max_heading:
                    self.heading = round(self.heading + self.heading_step_size, 4)
                    self.stepper_heading.goto_angle(self.heading)
                else:
                    self.line_direction = "CW"
                    self.scan_data.append(self.local_data)
                    self.local_data = []
                    return
            else:
                if self.heading  > self.min_heading:
                    self.heading = round(self.heading - self.heading_step_size, 4)
                    self.stepper_heading.goto_angle(self.heading)
                else:
                    self.line_direction = "CCW"
                    self.scan_data.append(list(reversed(self.local_data)))
                    self.local_data = []
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
        self.servo_pitch.do_step  (int((-1) * self.pitch / 1.8 ))
        self.heading = 0
        self.pitch = 0
        self.line_direction = "CCW"
        self.vertical_direction = "DOWN"
       
        
if __name__ == "__main__":
    scanner = Scanner()
    count = 0
    start = time.time()
    scanner.init_3D_scan(min_pitch = 10,    max_pitch = 15,
                         min_heading = -25.4, max_heading = 25.4,)
    scanner.do_3D_scan(60)
    print(scanner.get_scan_data())
    for i in scanner.get_scan_data():
            print(i)
            if i == "Lidar not Write":
                count += 1
    #scanner.do_3D_scan(2)
    #print(scanner.get_scan_data())
    print("Scan takes: " +str(time.time()-start) +" sec")
    print(count)


