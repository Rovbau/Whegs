#! python
# -*- coding: utf-8 -*-

from Motion import *
from Manuell import *
from Kompass import *
from time import sleep
from SMBUSBatt import *
from Scanner3d import *

if __name__ == "__main__":

    man = Manuell()
    motion  = Motion()
    kompass = Kompass()
    batterie = SMBUSBatt()

    scanner = Scanner()

    start = time.time()
    scanner.init_3D_scan(min_pitch = 10,    max_pitch = 15,
                         min_heading = -15.0, max_heading = 15.0,)

    ThreadEncoder=Thread(target=man.runManuell,args=())
    ThreadEncoder.daemon=True
    ThreadEncoder.start()

    motion_error = False

    while True:
        steer, speed = man.getManuellCommand()

        if steer == 0 and speed == 0:
            motion_error = False
        
        if abs(kompass.get_pitch()) > 25 or abs(kompass.get_roll()) > 25:
            steer = 0
            speed = 0
            motion_error = True
            print("SLOPE Warning")
            
        print("Current: " + str(batterie.get_current()))
        
        if batterie.get_current() > 5000 or motion_error == True:
            steer = 0
            speed = 0
            motion_error = True
            print("CURRENT Error Stopping")


        scanner.do_3D_scan(1)

        if scanner.get_min_dist() < 100:
            print("Collision WARNING")
            print(scanner.get_scan_data())
        #    steer = 0
         #   speed = 0
          #  motion_error = True

        motion.set_motion(steer , speed * 0.7)
            
        sleep(0.5)
        
             

