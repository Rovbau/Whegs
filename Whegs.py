from Manuell import *
from Motion import *
from Kompass import *
from SMBUSBatt import *
from Scanner3d import *
from threading import Thread

class Whegs:

    def __init__(self):
        self.man = Manuell()
        self.motion  = Motion()
        self.kompass = Kompass()
        self.batterie = SMBUSBatt()
        self.scanner = Scanner()
        self.last_action = None
        self.ThreadEncoder = None

    def init(self):
        self.start = time.time()
        self.scanner.init_3D_scan(min_pitch = 10,    max_pitch = 15,
                         min_heading = -15.0, max_heading = 15.0,)

        self.ThreadEncoder = Thread(target=self.man.runManuell, args=(), daemon=True)
        self.ThreadEncoder.start()

    def get_status_data(self):
        return {
            "kompass_heading": self.kompass.get_heading(),
            "kompass_pitch": self.kompass.get_pitch(),
            "kompass_roll": self.kompass.get_roll(),
            "battery_current": self.batterie.get_current(),
            "last_action": self.last_action
        }

    def action(self, action):
        self.last_action = action

    def run(self):
        motion_error = False

        while True:
            steer, speed = self.man.getManuellCommand()

            if steer == 0 and speed == 0:
                motion_error = False
            
            if abs(self.kompass.get_pitch()) > 25 or abs(self.kompass.get_roll()) > 25:
                steer = 0
                speed = 0
                motion_error = True
                print("SLOPE Warning")
                
            print("Current: " + str(self.batterie.get_current()))
            
            if self.batterie.get_current() > 5000 or motion_error == True:
                steer = 0
                speed = 0
                motion_error = True
                print("CURRENT Error Stopping")


            self.scanner.do_3D_scan(1)

            if self.scanner.get_min_dist() < 100:
                print("Collision WARNING")
                print(self.scanner.get_scan_data())
            #    steer = 0
            #   speed = 0
            #  motion_error = True

            self.motion.set_motion(steer , speed * 0.7)
                
            sleep(0.5)
