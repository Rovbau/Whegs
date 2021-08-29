from Manuell import *
from Motion import *
from Kompass import *
from SMBUSBatt import *
from Scanner3d import *
from threading import Thread
import atexit



class Whegs:

    def __init__(self):
        self.man = Manuell()
        self.motion  = Motion()
        self.kompass = Kompass()
        self.batterie = SMBUSBatt()
        self.scanner = Scanner()
        self.last_action = None
        self.distance = None
        self.ThreadEncoder = None
        
        atexit.register(self.motion.set_motion, steer = 0, speed = 0)

    def init(self):
        self.start = time.time()
        self.scanner.init_3D_scan(min_pitch = 0,    max_pitch = 0,
                         min_heading = 20.0, max_heading = -20.0,)

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

            if self.last_action == "stop":
                print("stopping")
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
                steer = 0
                speed = 0
                print("Can't get control action")



            if steer == 0 and speed == 0:
                motion_error = False
            
            if abs(self.kompass.get_pitch()) > 20 or abs(self.kompass.get_roll()) > 20:
                steer = 0
                speed = 0
                motion_error = True
                print("SLOPE Warning")
                
            
            if (self.batterie.get_current() > 5000 and self.batterie.get_current() < 60000 )or motion_error == True:
                steer = 0
                speed = 0
                motion_error = True
                print("CURRENT Error Stopping")


            self.scanner.do_3D_scan(1)

            self.scanner.min_heading = 180
            self.scanner.max_heading = 200

            if self.scanner.get_min_dist() < 30:
                print("Collision WARNING")
                print(self.scanner.get_min_dist())
                if speed > 0:
                    speed = 0
                steer = 0
                self.distance = "TO NARROW MOVE BACKWARTS !"
            else:
                self.distance = None

            self.motion.set_motion(steer , speed*0.7)
                
            sleep(0.5)
