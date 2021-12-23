#! python
# -*- coding: utf-8 -*-

from Avoid import *
from time import *


class Planer():
    def __init__(self, avoid, karte):
        self.avoid = avoid
        self.karte = karte
        self.wall_modus = False
        self.follow_left = False
        self.follow_right = False
        self.fixed_attraction = 0
        self.steering_output = 0
        self.goal_position = [3000,0]
        self.blocked_activ = False
        self.enter_blocked_time = 0
        self.command_list = []
        self.track_back = []
        self.aktual_command = 0

    def set_modus(self, x, y, pose, steer, speed, avoid_steering, max_left, max_right, em_stop):
        """Set Robot modus: wall or goal or blocked"""
        self.x = x
        self.y = y
        self.pose = pose
        self.steer = steer
        self.speed = speed
        self.avoid_steering = avoid_steering
        self.max_left = max_left
        self.max_right = max_right
   
        kurs_to_ziel = self.avoid.direction(x, y, self.goal_position[0], self.goal_position[1])
        self.kurs_diff = self.avoid.angle_diff(kurs_to_ziel, pose)
        self.last_commands()
           
        if em_stop == True or self.blocked_activ == True:
            self.modus_blocked()
            return(self.steering_output, self.speed)
        elif (abs(self.avoid_steering) > 0 and abs(self.kurs_diff) > 40) or self.wall_modus == True:
            self.modus_wall()
        elif self.wall_modus == False:
            self.modus_go_to_goal()
        
        return(self.steering_output, self.speed)

    def modus_blocked(self):
        """Follows the same path back(self.command_list), Set: steering_output / speed"""
        print("modus_blocked")              
        if self.blocked_activ == False:
            self.blocked_activ = True
            self.aktual_command = 0
            self.command_list.reverse()
            self.track_back = self.command_list[:]
            self.karte.updateHardObstacles()
        if self.track_back:
            self.aktual_command += 1      
            if self.aktual_command < len(self.track_back):
                self.steering_output = self.track_back[self.aktual_command][0] * (-1)
                self.speed = -1
            else:
                self.blocked_activ = False
                self.speed = 1
                self.track_back = []
                print("blocked_end")
                 
    def modus_go_to_goal(self):
        print("modus_go_to_goal")
        self.steering_output =  self.kurs_diff / 90 + self.avoid_steering

    def exit_wall_modus(self):
        """Exit Wall_modus if dist to goal is smaller as before"""
        dist = self.avoid.distance(self.x, self.y, self.goal_position[0], self.goal_position[1])
        if self.leaving_track_dist_to_goal - dist > 50:
            return(True)
        else:
            return(False)

    def modus_wall(self):
        """Follow wall left/right, until dist to goal is small as before"""
        if self.wall_modus == False:
            self.wall_modus = True
            self.leaving_track_dist_to_goal = self.avoid.distance(self.x, self.y, self.goal_position[0], self.goal_position[1])
            if self.kurs_diff <= 0:
                self.follow_left = False
                self.follow_right = True
                self.fixed_attraction = -0.7
            else:
                self.follow_left = True
                self.follow_right = False
                self.fixed_attraction = 0.7

        if self.follow_left:
            print("follow_left")
            self.steering_output = self.fixed_attraction + self.max_left
        if self.follow_right:
            print("follow_right")
            self.steering_output = self.fixed_attraction + self.max_right
        if self.exit_wall_modus():
            self.wall_modus = False
        return

    def last_commands(self):
        """pop first elements from list: to maintain length"""
        MAX_OBST_OBSERV = 15
        self.command_list.append([self.steer, self.speed])
        if len(self.command_list) > MAX_OBST_OBSERV:
            len_fifo = len(self.command_list) - MAX_OBST_OBSERV 
            del self.command_list[:len_fifo]      
        
    
if __name__ == "__main__":
    
    avoid = Avoid()
    avoid_steering, max_left, max_right = avoid.get_nearest_obst(0,0, 0, [[40,40],[100,10]])
    print(avoid.avoided_obst())
    planer = Planer(avoid)
    print(planer.set_modus(10, 10, 15, avoid_steering, max_left, max_right))
