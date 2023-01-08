import serial
#import binascii
from operator import itemgetter
import math
from time import *


class Lidar_LD19:
    def __init__(self):
        self.ser = serial.Serial(port='/dev/ttyUSB0', baudrate=230400, timeout=5.0, bytesize=8, parity='N', stopbits=1)
        self.tmpString = ""
        self.angles = list()
        self.distances = list()
        self.full_scan_data = []
    
    def get_lidar_data(self):
        """Gets the data from the LD_19 Lidar, returns 360 scan_datapoins [angle, dist]"""

        loopFlag = True
        flag2c = False
        
        self.ser.flushInput()
        self.full_scan_data = []

        while loopFlag:
            b = self.ser.read()
            tmp_int = int.from_bytes(b, 'big')
            
            if (tmp_int == 0x54):
                self.tmpString +=  b.hex()+" "
                flag2c = True
                continue
            
            elif(tmp_int == 0x2c and flag2c):
                self.tmpString += b.hex()

                if(not len(self.tmpString[0:-5].replace(' ','')) == 90 ):
                    self.tmpString = ""
                    flag2c = False
                    continue

                lidar_data = self.CalcLidarData(self.tmpString[0:-5])
                self.full_scan_data.extend(lidar_data)
                self.tmpString = ""

                if len(self.full_scan_data) > 460:
                    self.full_scan_data.sort(key=itemgetter(0))
                    #print(self.full_scan_data)
                    loopFlag = False

            else:
                self.tmpString += b.hex()+" "           
            flag2c = False

        return(self.full_scan_data)

    def polar_to_cartesian(self, data):
        scan_cartesian = []
        for element in data:
            dx=int((element[1]*math.cos(math.radians(element[0]))))
            dy=int((element[1]*math.sin(math.radians(element[0]))))
            scan_cartesian.append([dx, dy])
        return(scan_cartesian)

    def CalcLidarData(self, data):
        data = data.replace(' ','')

        #Speed = int(data[2:4]+data[0:2],16)/100
        start_angle = float(int(data[6:8]+data[4:6],16))/100
        end_angle = float(int(data[-8:-6]+data[-10:-8],16))/100
        #TimeStamp = int(data[-4:-2]+data[-6:-4],16)
        #CS = int(data[-2:],16)

        partial_scan = []
  
        if(end_angle-start_angle > 0):
            angleStep = float(end_angle-start_angle)/(12)
        else:
            angleStep = float((end_angle+360)-start_angle)/(12)
          
        circle = lambda deg : deg - 360 if deg >= 360 else deg
        counter = 0
        for i in range(0,6*12,6): 
            dist = (int(data[8+i+2:8+i+4] + data[8+i:8+i+2],16))
            #confidence.append(int(data[8+i+4:8+i+6],16))
            angle = round((math.degrees(circle(angleStep*counter+start_angle)*math.pi/180.0)),1)
            partial_scan.append([angle, dist])
            counter += 1
       
        return (partial_scan)

if __name__ == "__main__":

    lidar = Lidar_LD19()
    data = lidar.get_lidar_data()
    print(data)