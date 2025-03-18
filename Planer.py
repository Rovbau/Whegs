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
        self.recovery_path = [[0, -1]]*10
        self.position_recovery = 0
        self.recovery_modus = False

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

        # if em_stop == True or self.blocked_activ == True:
        #     self.modus_blocked()
        #     return(self.steering_output, self.speed)
        
        if (self.avoid_steering > 4) or (self.max_left > 4) or (self.max_right > 4) or (self.recovery_modus == True):
            self.recovery()
        elif (abs(self.avoid_steering) > 2)  or self.wall_modus == True:       #and abs(self.kurs_diff) > 40)
            self.modus_wall()
        elif self.wall_modus == False:
            self.modus_go_to_goal()
        
        return(self.steering_output, self.speed)
    
    def recovery(self):
        """ Recovery if distances are to close. Backwards until recovery_dist is reached """
        if self.recovery_modus == False:
            self.recovery_modus = True
            self.recovery_position = [self.x, self.y]
         
        self.steering_output, self.speed = [0, -1]
            
        recovery_dist = self.avoid.distance(self.x, self.y, self.recovery_position[0], self.recovery_position[1])
        print("Recovery " +str(self.steering_output) + " " +str(self.speed) + " " +str(recovery_dist))

        if recovery_dist > 0.5:
            self.recovery_modus = False
        sleep(1)


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
        """Go to goal. Steer to Goal. Avoids obstacles left + right"""
        print("modus_go_to_goal")
        self.steering_output =  (self.kurs_diff / 90) + self.max_left + (self.max_right * (-1))

    def exit_wall_modus(self):
        """Exit Wall_modus if dist to goal is smaller as before"""
        dist = self.avoid.distance(self.x, self.y, self.goal_position[0], self.goal_position[1])
        print("Goal is neared as before:" +str(round(self.leaving_track_dist_to_goal - dist, 3)))
        if self.leaving_track_dist_to_goal - dist > (+0.2):
            return(True)
        else:
            return(False)

    def modus_wall(self):
        """Follow wall left/right, until dist to goal is small as before"""
        if self.wall_modus == False:
            self.wall_modus = True
            self.leaving_track_dist_to_goal = self.avoid.distance(self.x, self.y, self.goal_position[0], self.goal_position[1])
            if  self.max_right < self.max_left:    #self.kurs_diff <= 0:
                self.follow_left = False
                self.follow_right = True
                self.fixed_attraction = -0.7
            else:
                self.follow_left = True
                self.follow_right = False
                self.fixed_attraction = 0.7

        if self.follow_left:
            # Wall is on the right side of the robot
            print("follow_left")
            self.steering_output = self.fixed_attraction + (self.max_right * (-1)) + (self.avoid_steering * (-1))
        if self.follow_right:
            # Wall is on the left side of the robot
            print("follow_right")
            self.steering_output = self.fixed_attraction + self.max_left + self.avoid_steering
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
