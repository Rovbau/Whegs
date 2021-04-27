from math import *
from Scanner3d import *

scan_data = [[[10.0, -3.6, 110], [10.0, -1.8, 106], [10.0, 0.0, 110], [10.0, 1.8, 108], [10.0, 3.6, 109]],
             [[11.0, -3.6, 110], [11.0, -1.8, 108], [11.0, 0.0, 109], [11.0, 1.8, 108], [11.0, 3.6, 111]],
             [[12.0, -3.6, 110], [12.0, -1.8, 107], [12.0, 0.0, 107], [12.0, 1.8, 110], [12.0, 3.6, 110]],
             [[13.0, -3.6, 109], [13.0, -1.8, 108], [13.0, 0.0, 108], [13.0, 1.8, 108], [13.0, 3.6, 105]],
             [[14.0, -3.6, 106], [14.0, -1.8, 106], [14.0, 0.0, 108], [14.0, 1.8, 108], [14.0, 3.6, 109]],
             [[15.0, -3.6, 111], [15.0, -1.8, 111], [15.0, 0.0, 114], [15.0, 1.8, 108], [15.0, 3.6, 111]]]

obstacles = dict()
heading = 1
pitch = 0
dist = 2

class Obstacles():
    def __init__(self):
        self.obstacles = dict()
        self.sensor_high = 150 #[mm]
        self.TRESHOLD = 1

    def calc_high(self, pitch, dist):
        z = self.sensor_high - (cos(radians(90 - pitch))*dist)
        return(z)

    def calc_slope(self, element1, element2):
        pitch1, _ , dist1 = element1
        pitch2, _ , dist2 = element2
        
        z1 = self.calc_high(pitch1, dist1)
        z2 = self.calc_high(pitch2, dist2)

        slope = (z1 - z2) / (dist1 - dist2 + 0.1) #+0.1 to prevent zero division
        return(slope)

    def detect_obstacles(self, scan_data):
        
        pitch = 0
        heading = 1
        dist = 2
        
        #iterate trough elements L->R
        for element in range(len(scan_data[0])):
            
            #Iterate trough line Up->Dwn
            for line in range(len(scan_data[0:-1])):
                
                #Find high slope in scans
                slope = self.calc_slope(scan_data[line][element], scan_data[line + 1][element])
                print(round(slope,2), scan_data[line][element], scan_data[line + 1][element])
                if abs(slope) > self.TRESHOLD:
                    #Add data to obstacles
                    if scan_data[line][element][heading] not in self.obstacles:
                        self.obstacles[scan_data[line][element][heading]] = scan_data[line][element]
                    else:
                        self.obstacles[scan_data[line][element][heading]].extend(scan_data[line][element])
        print("Dedect folowing Obst: ")
        for k in self.obstacles:
            print(k, self.obstacles[k])

scanner = Scanner()
scanner.init_3D_scan(min_pitch = 8,    max_pitch = 12,
                     min_heading = -9, max_heading = 9,)
scanner.do_3D_scan(2)
scan_data = scanner.get_scan_data()
print(scan_data)

obstacles = Obstacles()
obstacles.detect_obstacles(scan_data)



