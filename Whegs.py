import time
import os
import atexit
from Manuell import *
from Motion import *
from Kompass import *
from Avoid import *
from Planer import *
from SMBUSBatt import *
from Scanner3d import *
from Pumper import *
from threading import Thread
from Karte import *
from Bug import *
from MotorDataLogger import *
from VisualisationScan import *

class Whegs:
    def __init__(self):
        self.man = Manuell()
        self.motion  = Motion()
        self.kompass = Kompass()
        self.batterie = SMBUSBatt()
        self.scanner = Scanner()
        self.karte = Karte()
        self.avoid = Avoid()
        self.planer = Planer(self.avoid, self.karte)
        self.pumper = Pumper()
        self.visualisationScan = VisualisationScan()
        self.bug = Bug()
        self.motorDataLogger = MotorDataLogger(self.motion, "motor_data_log.txt")
        self.last_action = None
        self.distance = None
        self.ThreadEncoder = None
        
        atexit.register(self.motion.set_motion, steer = 0, speed = 0)
        atexit.register(self.scanner.scanner_reset)
        atexit.register(self.motorDataLogger.close_file)

    def init(self):
        self.start = time()
        self.scanner.init_3D_scan(min_pitch = 0,    max_pitch = 0, min_heading = -40.0, max_heading = 40.0,)
        self.ThreadEncoder = Thread(target=self.man.runManuell, args=(), daemon=True)
        self.ThreadEncoder.start()

    def get_status_data(self):
        return {
            "kompass_heading": self.kompass.get_heading(),
            "kompass_pitch": self.kompass.get_pitch(),
            "kompass_roll": self.kompass.get_roll(),
            "battery_current": self.batterie.get_current(),
            "last_action": self.last_action,
            "motion Error": self.distance
        }

    def action(self, action):
        self.last_action = action

    def run(self):
        motion_error = False

        while True:
            self.pumper.status_led("on")

            steer, speed = self.man.getManuellCommand()
            while steer == 10 and speed == 10:
                self.motion.set_motion(0,0)
                steer, speed = self.man.getManuellCommand()
                self.scanner.scanner_reset()
                sleep(1)
            
            if self.last_action == "stop":
                steer = 0
                speed = 0
            elif self.last_action == "right":
                steer = -1
                speed = 0.5
            elif self.last_action == "left":
                steer = 1
                speed = 0.5
            elif self.last_action == "back":
                steer = 0
                speed = -0.5
            elif self.last_action == "forward":
                steer = 0
                speed = 0.5
            else:
                steer, speed = self.man.getManuellCommand()

            if steer == 0 and speed == 0:
                motion_error = False
            
            if abs(self.kompass.get_pitch()) > 40 or abs(self.kompass.get_roll()) > 40:
                steer = 0
                speed = 0
                motion_error = True
                print("SLOPE Warning")
            
            if self.batterie.get_relative_charge() < 30:
                print("BATTERY empty")
                         
            current = self.batterie.get_current()
            if ( 6000 < current < 65000) or motion_error == True:
                steer = 0
                speed = 0
                motion_error = True
                print("CURRENT Error Stopping : " + str(current) + str("mA"))

            if self.scanner.get_min_dist() < 60:
                self.distance = "TO NARROW MOVE BACKWARTS !"
            else:
                self.distance = None

            #Store the Motor data for all 4 motors
            #self.motorDataLogger.store(current)

            deltaL = self.motion.motor_VL.get_counts()
            deltaR = self.motion.motor_VR.get_counts()
            heading = self.kompass.get_heading()
            print(deltaL, deltaR)
            self.karte.updateRoboPos(deltaL * (-1), deltaR, heading)
            x, y, pose = self.karte.getRoboPos()

            self.scanner.do_3D_scan(1)         
            scan_data = self.scanner.get_scan_data()
            #print(scan_data)

            self.karte.updateObstacles(scan_data)
            obstacles = self.karte.getObstacles()
            print(obstacles)
            self.visualisationScan.draw_scan(obstacles, [x, y, pose] )
            self.visualisationScan.search_line(obstacles)

            front, left , right = self.bug.analyse(scan_data)
            #steer, speed_korr = self.bug.modus(front, left, right)
            steer, speed_korr = self.bug.modus_sinus(front, left, right, heading)

            print("Heading:" +str(heading))
            print("Left : " + str(self.bug.left) + "  Dist: " + str(self.bug.left_min))
            print("Front: " + str(self.bug.front)+ "  Dist: " + str(self.bug.front_min))
            print("Right: " + str(self.bug.right)+ "  Dist: " + str(self.bug.right_min))
            print("Current: " + str(current))
            print("Steer: " + str(steer) + "  Speed_korr: " + str(speed_korr))
            print("Position: " +str(x) + " " + str(y) + " " + str(pose)) 
                 
            #avoid_steering, max_left, max_right = self.avoid.get_nearest_obst(x, y, pose, obstacles)
            #steering_output, speed = self.planer.set_modus(x, y, pose, steer, speed, avoid_steering, max_left, max_right, False)
            #steer = steering_output * 0.5
            #print("Avoid_Steering: " + str(avoid_steering))
            #rint("Steering_Output: " + str(steering_output) + "  max_left: " + str(max_left) + "  max_right: " + str(max_right))
            #print("Avoid_Obst: " +str(self.avoid.avoided_obst()))
            #print("Position: "+ str(x) + " "+ str(y) + " " + str(pose))
            #print("Steer: " +str(steer))

            self.motion.set_motion(steer  , min(speed * speed_korr  , 0.7)) 
            self.pumper.status_led("off")
            sleep(0.2)
            #os.system('clear')
