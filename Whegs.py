from Manuell import *
from Motion import *
from Kompass import *
from Avoid import *
from Planer import *
from SMBUSBatt import *
from Scanner3d import *
from threading import Thread
from Karte import *
import atexit

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
        self.last_action = None
        self.distance = None
        self.ThreadEncoder = None
        
        atexit.register(self.motion.set_motion, steer = 0, speed = 0)
        atexit.register(self.scanner.scanner_reset)

    def init(self):
        self.start = time.time()
        self.scanner.init_3D_scan(min_pitch = 0,    max_pitch = 0,
                         min_heading = -45.0, max_heading = 45.0,)
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
            steer, speed = self.man.getManuellCommand()

            heading = self.kompass.get_heading()
            deltaL = self.motion.motor_VL.get_counts() * (-1)
            deltaR = self.motion.motor_VR.get_counts()
            self.karte.updateRoboPos(deltaL, deltaR, heading)
            x, y, pose = self.karte.getRoboPos()
            print("Position: "+ str(x) + " "+ str(y) + " " + str(pose))

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
            
            if abs(self.kompass.get_pitch()) > 45 or abs(self.kompass.get_roll()) > 45:
                steer = 0
                speed = 0
                motion_error = True
                print("SLOPE Warning")
            
            if self.batterie.get_relative_charge() < 30:
                print("BATTERIE empty")
                         
            if (self.batterie.get_current() > 5000 and self.batterie.get_current() < 60000 )or motion_error == True:
                steer = 0
                speed = 0
                motion_error = True
                print("CURRENT Error Stopping")


            self.scanner.do_3D_scan(1)


            scan_data = self.scanner.get_scan_data()

            self.karte.updateObstacles(scan_data)
            obstacles = self.karte.getObstacles()
            
            avoid_steering, max_left, max_right = self.avoid.get_nearest_obst(x, y, pose, obstacles)
            print("Go")
            steering_output, speed = self.planer.set_modus(x, y, pose, steer, speed, avoid_steering, max_left, max_right, False)
            print(steering_output)
            steer = steering_output

            #if self.scanner.get_min_dist() < 90:
            #    print("Collision WARNING")
            #    print(self.scanner.get_min_dist())
            #    steer = -1
            #    self.distance = "TO NARROW MOVE BACKWARTS !"
            #else:
            #    self.distance = None

            self.motion.set_motion(steer , speed*0.7)
                
            sleep(0.5)
