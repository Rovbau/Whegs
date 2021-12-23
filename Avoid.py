#! python
# -*- coding: utf-8 -*-

from math import sqrt, exp, pi, degrees, radians, atan2, atan, cos

class Avoid():
    def __init__(self):
        self.TRESHOLD = 0.2
        self.MAX_OBST_OBSERV = 200
        self.obst_fifo = []
        self.colision_obst = []
        self.avoided_obstacles = []

    def get_nearest_obst(self, robo_pos_x, robo_pos_y, pose, obstacles):
        """return INT importanceForce to nearest obstacle, force depends on dist AND angle"""
        self.robo_pos_x = robo_pos_x
        self.robo_pos_y = robo_pos_y
        self.pose = pose
        max_left = 0
        max_right = 0
        max_overall = 0
        avoid_steering = 0
        self.obst_fifo.extend(obstacles)
        self.limit_fifo_lengh()
        self.colision_obst = self.colision_analysis(self.obst_fifo)
        nearest_obst = []
        
        for obstacle in self.colision_obst:
            dist = self.distance(self.robo_pos_x, self.robo_pos_y , obstacle[0], obstacle[1])
            importance = self.calc_force(dist, obstacle[2])
            if abs(importance) > self.TRESHOLD:
                if importance < 0 and importance < max_left:
                   max_left =  importance
                if importance > 0 and importance > max_right:
                   max_right =  importance
                if abs(importance) > max_overall: 
                    max_overall = abs(importance)
                    avoid_steering = importance
                    kurs_diff_to_obst = obstacle[2]
                    nearest_obst = obstacle
        if nearest_obst:
            self.avoided_obstacles.append(nearest_obst)
        return(avoid_steering, max_left, max_right)

    def colision_analysis(self, obstacles):
        """return list of obstacles[x,y,kurs_diff] witch are in +/- SCAN_ANGLE"""
        SCAN_ANGLE = 50
        self.colision_obst = []
        for obstacle in obstacles:
            kurs_to_obst = self.direction(self.robo_pos_x, self.robo_pos_y, obstacle[0], obstacle[1])
            kurs_diff = self.angle_diff(self.pose, kurs_to_obst)
            if  abs(kurs_diff) < SCAN_ANGLE:
                self.colision_obst.append([obstacle[0], obstacle[1], kurs_diff])
        return (self.colision_obst)

    def direction(self, x1, y1, x2, y2):
        """get angle between P1/P2 in range 0-360"""
        dx, dy = (x2 - x1, y2 - y1)
        kurs = degrees(atan2(dy,dx))
        if kurs < 0:
            kurs = 180 + (180 - abs(kurs))
        return(kurs)

    def distance(self, x1, y1, x2, y2):
        """return INT, distance between two Object"""
        dist = sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))
        return(dist)
    
    def limit_fifo_lengh(self):
        """pop first elements from list: obst_fifo to maintain length"""
        if len(self.obst_fifo) > self.MAX_OBST_OBSERV:
            len_fifo = len(self.obst_fifo) - self.MAX_OBST_OBSERV 
            del self.obst_fifo[:len_fifo]

    def calc_force(self, dist, kurs_diff):
        """return INT avoidance_force , higher if dist shorter, higher if kurs_diff smaller"""
        avoid_force = exp(-(dist-70)*0.07)    #50 norm.
        angle_force = cos(radians(kurs_diff))
        if kurs_diff < 0:
            avoid_force = abs(avoid_force) * (-1)
        else:
            avoid_force = abs(avoid_force)          
        importance = avoid_force
        return(importance)

    def angle_diff(self, soll, ist):
        """get angle between two angles in range -180/180 """
        angle = (soll-ist)
        if angle > 180:
            angle = angle - 360
        if angle < -180:
            angle = 360 + angle
        return(angle)

    def avoided_obst(self):
        """return LIST of all avoides obstacles[x,y] since last call"""
        liste = self.avoided_obstacles
        self.avoided_obstacles = []
        return(liste)
        


if __name__ == "__main__":
    avoid = Avoid()
    robo_pos_x = 0
    robo_pos_y = 0
    pose       = 0
    obstacles = [[70,10],[70,-10], [80,-20]]

    print(avoid.get_nearest_obst(robo_pos_x, robo_pos_y, pose, obstacles))
    print(avoid.avoided_obst())



