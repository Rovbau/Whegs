#! python
# -*- coding: utf-8 -*-

from Motion import *
from Manuell import *
from Kompass import *
from time import sleep

if __name__ == "__main__":

    man = Manuell()
    motion  = Motion()
    kompass = Kompass()
    

    ThreadEncoder=Thread(target=man.runManuell,args=())
    ThreadEncoder.daemon=True
    ThreadEncoder.start()

    while True:
        steer, speed = man.getManuellCommand()
        motion.set_motion(steer , speed * 0.7)
        if abs(kompass.get_pitch()) > 25 or abs(kompass.get_roll()) > 25:
            motion.set_motion(0, 0)
            print("SLOPE Warning")
        sleep(1)
        
             

