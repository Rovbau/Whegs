#! python
# Programm ueberwacht gefaherlich Zustaende des Robo

from Kompass import *
from time import sleep
from SMBUSBatt import *

class Limits():
    def __init__(self, kompass, batterie):
        self.kompass = kompass
        self.batterie = batterie
        self.heading_old = None
        self.MAX_CURRENT = 5000
        self.MAX_SLOPE = 25
        
    def danger(self):         
        return([self.fuselage(), self.overcurrent(), self.not_turning()])
    
    def fuselage(self):
        if abs(self.kompass.get_pitch()) > self.MAX_SLOPE or abs(self.kompass.get_roll())  > self.MAX_SLOPE:
            return("Slope")
        else:
            return(False)

    def overcurrent(self):
        if self.batterie.get_current() > self.MAX_CURRENT:
            return("overcurrent")
        else:
            return(False)

    def not_turning(self):
        heading = self.kompass.get_heading()
        print(heading)
        if  heading == self.heading_old:
            status = "not_turning"
        else:
            status = False
        
        self.heading_old = heading
        return(status)
 
if __name__ == "__main__":

    kompass = Kompass()
    batterie = SMBUSBatt()

    limits  = Limits(kompass, batterie)
    print(limits.danger())
    print(limits.danger())

    
