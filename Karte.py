#!/usr/bin/env python
#-*- coding: utf-8 -*-

from math import sin,cos,radians,degrees,sqrt,pi
from copy import deepcopy
import time
import pickle

class Karte():
    def __init__(self):
        self.RoboPosY= 0
        self.RoboPosX= 0
        self.RoboPath=[]
        self.globalObstaclesList=[]
        self.globalHardObstaclesList = []
        self.global_kurs= 0
        self.kompassOld=0
        self.timeold=0

    def updateObstacles(self, obstacles):
        """Obstacles werden in Karte eingetragen"""
        global_obs = self.calcGlobalObstaclePosition(obstacles)
        self.globalObstaclesList.extend(global_obs)
    
    def updateHardObstacles(self):
        """Obstacles von Pumper eintragen"""
        global_obs = self.calcGlobalObstaclePosition([[10, 20],[10, 0],[10, -20]])
        self.globalHardObstaclesList.extend(global_obs)

    def calcGlobalObstaclePosition(self, obstacles):
        """Calc the global position of every local Obstacle, Returns list"""       
        global_obstacle_list = []
        for obstacle in obstacles:            
            #Wandeln Winkeldaten für Globalberechnung: -90zu+90 und +90zu-90 0=0
            #ScanList[i][0]=degrees(asin(sin(radians(ScanList[i][0])+radians(180))))

            Dx = obstacle[0]
            Dy = obstacle[1]

            #Drehmatrix für X, Returns Global Hindernis Position
            X=(Dx*cos(radians(self.global_kurs))+Dy*(-sin(radians(self.global_kurs))))+self.RoboPosX
            #Drehmatrix für Y, Returns Global Hindernis Position
            Y=(Dx*sin(radians(self.global_kurs))+Dy*(cos(radians(self.global_kurs))))+self.RoboPosY

            global_obstacle_list.append([int(X),int(Y)])
        return(global_obstacle_list)

    def updateRoboPos(self,deltaL,deltaR,KompassCourse=None):
        """Update Robo Position auf Karte"""
        #RoboSchwerpunkt bis Rad cm
        Radstand= 35.0
        countsRadGross= 1440

        #Werte Uebernehmen: Counts in (cm) umrechnen
        deltaL=deltaL*((28.6*pi)/countsRadGross)           #(Radumfang)/counts
        deltaR=deltaR*((28.6*pi)/countsRadGross)           #(Radumfang)/counts
        WinkelDiff=degrees((deltaR-deltaL)/Radstand)      #Raddist/Radstandbreite
        
        self.global_kurs=self.global_kurs+WinkelDiff        #Global Kurs anhand Weg berechnen
        if self.global_kurs>360:
            self.global_kurs=self.global_kurs-360
        if self.global_kurs<0:
            self.global_kurs=360-abs(self.global_kurs)            
        global_kurs_radiant=radians(self.global_kurs)
        #Uncomment following if you use Compass
        global_kurs_radiant = radians(KompassCourse)
        self.global_kurs = degrees(global_kurs_radiant)
        #global_kurs_radiant=0
        #self.global_kurs=KompassCourse                           

        if deltaL != deltaR:
            da=(deltaR-deltaL)/Radstand     #Drehwinkel in  [rad]
            ds=(deltaL+deltaR)/2            #Mittler Strecke von L und R

            #delta X und Y berechnen nach einer Kurve Dx->Waagerecht Dy->senkrecht
            dx=(ds/da)*(cos((pi/2)+global_kurs_radiant-da)+cos(global_kurs_radiant-(pi/2)))
            dy=(ds/da)*(sin((pi/2)+global_kurs_radiant-da)+sin(global_kurs_radiant-(pi/2)))
                       
            #Position des Robo auf Karte updaten
            self.drehmatrix(dx,dy)
        else:       
            dx=deltaR*cos(global_kurs_radiant)
            dy=deltaL*sin(global_kurs_radiant)

            #Position des Robo auf Karte updaten
            self.drehmatrix(dx,dy)

    def drehmatrix(self,dx,dy):
        self.RoboPosX=self.RoboPosX+dx
        self.RoboPosY=self.RoboPosY+dy
        
    def saveRoboPath(self):
        """Pickel Robos Path every Xsec."""
        if time.time()-self.timeold > 2:          
            self.RoboPath.append([round(self.RoboPosX,1),round(self.RoboPosY,1)])
            self.timeold = time.time()

    def getRoboPos(self):
        """returns RoboPos X,Y,pose"""
        return(round(self.RoboPosX,1),round(self.RoboPosY,1),round(self.global_kurs,2))

    def setRoboPos(self,x,y):
        """Set Robo Position zb bei Start"""
        self.RoboPosX=x
        self.RoboPosY=y
    
    def getRoboPath(self):
        """returns RoboPath X,Y"""
        return(self.RoboPath)

    def getObstacles(self):
        """return latest Obstacles and clears obstacles"""
        ausgabeObstacle = self.globalObstaclesList + self.globalHardObstaclesList
        self.globalObstaclesList = []
        return(ausgabeObstacle)

    def getZielkurs(self):
        """return Zielkurs 0-360"""
        return(0)
    
    def getPumperStatus(self):
        """return Stosstangen status"""
        return(self.pumperL,self.pumperR)

if __name__ == "__main__":

    karte=Karte()
    
    Obstacles=[[60,60],[50,50],[0,130],[0,140]]

    karte.updateObstacles(Obstacles)
    #print(karte.getObstacles())

    deltaL=50
    deltaR=0
    KompassCourse=0
    karte.updateRoboPos(deltaL,deltaR,KompassCourse)
    print(karte.getRoboPos())
    
    deltaL=660
    deltaR=660
    KompassCourse=0
    karte.updateRoboPos(deltaL,deltaR,KompassCourse)  
    print(karte.getRoboPos())
    
    print(karte.getRoboPath())


