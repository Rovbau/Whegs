

class Bug():
    def __init__(self):
        self.MIN_DIST = 250
        self.front = "free"
        self.left  = "free"
        self.right = "free"
        self.speed = 1
        self.LOW_SPEED = 0.3
        self.new_goal = 1
        self.goal_heading_old = 1

    def angle_diff(self, soll, ist):
        """get angle between two angles in range -180/180 """
        angle = (soll-ist)
        if angle > 180:
            angle = angle - 360
        if angle < -180:
            angle = 360 + angle
        return(angle)

    def analyse(self, scan_data):
        """Analyse Scan an find free space"""
        #last_scan = scan_data[-1]
        last_scan = scan_data

        self.front = "free"
        self.left  = "free"
        self.right = "free"
        self.front_min = 99999
        self.left_min  = 99999
        self.right_min = 99999
        self.speed = 0.5
       
        for point in last_scan:
            pitch, heading, dist = point
            
            #Straight +/-15° @ dist = 90 -> 50cm free-space
            if (340 < heading <= 360) or (0 <= heading < 20) :
                if dist < self.MIN_DIST:
                    self.front = "blocked"
                    self.speed = self.LOW_SPEED
                    self.front_min = min(self.front_min, dist)       #0.1
            #Left           
            if  (280 < heading) and (heading < 330):
                if dist < self.MIN_DIST:
                    self.left = "blocked"
                    self.speed = self.LOW_SPEED
                    self.left_min = min(self.left_min, dist)
            #Right
            if (30 < heading) and (heading < 80):
                if dist < self.MIN_DIST:
                    self.right = "blocked"
                    self.speed = self.LOW_SPEED
                    self.right_min = min(self.right_min, dist)

        return(self.front, self.left, self.right)
    
    def get_minimum_dist(self):
        return (self.front_min, self.left_min,self.right_min)


    def modus_sinus(self, front, left, right, heading):
        "avoid obstacles depending on dist to obstacles. and heading to goal"

        goal_heading = self.angle_diff(0, heading)
        if goal_heading >= 0:
            self.new_goal = -1
        else:
            self.new_goal = 1

        print("goal_heading: " + str(goal_heading))

        if self.left == "free" and self.right == "free" and self.front == "free":
            lock = False
        else:
            lock = True

        if lock == False:
            self.new_goal = goal_heading
            self.goal_heading_old = goal_heading

        #print("new_goal: " + str(self.new_goal))
        #(goal_heading * (-1)/50)

        head = (goal_heading/500)
        min_L = (20 / self.left_min)
        min_R = (-20 / self.right_min)
        min_F = (20 / self.front_min)

        print("head:" +str (head))
        print("min_L:" +str (min_L))
        print("min_F:" +str (min_F))
        print("min_R:" +str (min_R))
        steer = (head + min_L  + min_R + min_F) * 50   

        return(round(steer, 2), round(self.speed, 2))


    def modus(self, front, left, right):
        steer = 0

        if front == "free" and left == "blocked" and right == "blocked":
            steer = 1           #(self.right_min - self.left_min) * 0.05
        elif front == "blocked" and left == "free" and right == "free":
            steer = 1
        elif front == "blocked"  and left == "blocked":
            steer = 1
        elif front == "blocked" and  right == "blocked":
            steer = -1
        else:
            steer = 0
            print("DECISION NOT DEFINED")
        return(round(steer, 2), round(self.speed, 2))
        
                



if __name__ == "__main__":

    bug = Bug()

    scan_data = [[0, -90.0, 100], [0, 0.0, 59], [0, 18.2, 59]]
    front, left, right = bug.analyse(scan_data)
    steer = bug.modus(front, left, right)
    print(bug.left)
    print(bug.front)
    print(bug.right)
    print(steer)

