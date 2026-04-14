import time
import os
from termcolor import colored
import atexit
from Manuell import *
from Motion import *
from Kompass import *
from Avoid import *
from Planer import *
from SMBUSBatt import *
from Lidar_LD19 import *
from ServoCont import *
from Pumper import *
from threading import Thread
from Karte import *
from Bug import *
from MotorDataLogger import *
from VisualisationScan import *
from IterativeScan_LD19 import *
from tabulate import tabulate
from collections import OrderedDict

class Whegs:
    def __init__(self):
        self.man = Manuell()
        self.motion  = Motion()
        self.kompass = Kompass()
        self.batterie = SMBUSBatt()
        self.lidar_LD19 = Lidar_LD19()
        self.servo = Servo()
        self.karte = Karte()
        self.avoid = Avoid()
        self.planer = Planer(self.avoid, self.karte)
        self.pumper = Pumper()
        self.visualisationScan = VisualisationScan()
        self.bug = Bug()
        self.motorDataLogger = MotorDataLogger(self.motion, "motor_data_log.txt")
        self.last_action = None
        self.distance = None
        self.ThreadEncoder = None
        self.logging_all_data = {}
        
        atexit.register(self.motion.set_motion, steer = 0, speed = 0)
        atexit.register(self.motorDataLogger.close_file)
        atexit.register(self.pickle_data, self.logging_all_data)

    def init(self):
        self.start = time()
        self.ThreadEncoder = Thread(target=self.man.runManuell, args=(), daemon=True)
        self.ThreadEncoder.start()

    def pickle_data(self, dat):
        with open("logging_scan_file_1.pkl", "wb") as filing:
            pickle.dump(dat, filing)    

    def get_status_data(self):
        return {
            "kompass_heading": self.kompass.get_heading(),
            "kompass_pitch": self.kompass.get_pitch(),
            "kompass_roll": self.kompass.get_roll(),
            "battery_current": self.batterie.get_current(),
            "last_action": self.last_action,
            "motion Error": self.distance
        }

    def action(self, action):
        self.last_action = action

    def run(self):
        motion_error = False
        loop_time = 0
        scan_old = []
        logging_tabulate = []
        x_scan, y_scan, pose_scan = 0, 0, 0
        x_summ, y_summ, pose_summ = 0, 0, 0
        aktual_data_this_loop = {}
        loop_count = 0

        while True:
            self.pumper.status_led("on")

            steer, speed = self.man.getManuellCommand()

            while (steer == 10 and speed == 10):
                self.motion.set_motion(0,0)
                steer, speed = self.man.getManuellCommand()

                # Logging Table View                
                with open("logging_tabulate.log", "w") as logging:
                    print(tabulate(logging_tabulate, headers="keys", tablefmt="github"), file = logging)
                    logging.flush()
                sleep(5)
            
            # if self.last_action == "stop":
            #     steer = 0
            #     speed = 0
            # elif self.last_action == "right":
            #     steer = -1
            #     speed = 1
            # elif self.last_action == "left":
            #     steer = 1
            #     speed = 1
            # elif self.last_action == "back":
            #     steer = 0
            #     speed = -1
            # elif self.last_action == "forward":
            #     steer = 0
            #     speed = 1
            # else:
            #     steer, speed = self.man.getManuellCommand()

            if abs(self.kompass.get_pitch()) > 20 or abs(self.kompass.get_roll()) > 20:
                steer = 0
                speed = 0
                motion_error = True
                print("SLOPE Warning")
            
            if self.batterie.get_relative_charge() < 30:
                print("BATTERY empty")
                         
            current = self.batterie.get_current()
            if ( 6000 < current < 65000):
                steer = 0
                speed = 0
                motion_error = True
                print("CURRENT Error Stopping : " + str(current) + str("mA"))

            if motion_error == True:
                print("MOTION Error") 
                self.motion.set_motion(0,0)
                sleep(5)

            # Store the Motor data for all 4 motors
            #self.motorDataLogger.store(current)

            # Get Robo position
            deltaL = self.motion.motor_VL.get_counts()
            deltaR = self.motion.motor_VR.get_counts()
            heading = self.kompass.get_heading()
            self.karte.updateRoboPos(deltaL * (-1), deltaR, heading)
            x, y, pose = self.karte.getRoboPos()

            # Get LIDAR data about 450 datapoints per scan
            scan_data = self.lidar_LD19.get_lidar_data()

            # Update Map with obstacles
            self.karte.updateObstacles(scan_data)
            obstacles = self.karte.getObstacles()
            
            # Draw a Map with obstacles and Robo-Position
            #self.visualisationScan.search_LSRegression(obstacles)
            #self.visualisationScan.draw_scan(obstacles, [x, y, pose] )

            # Bug.analyse return Free or Blocked
            front, left , right = self.bug.analyse(scan_data)
            #Bug.getminimum_dist return the minimum distance for front, left and right
            min_front, min_left, min_right = self.bug.get_minimum_dist()

            # Set the Robo to state: wall left, wall richt, blocked or go_to_goal
            steer, speed = self.planer.set_modus(x, y, heading, 0, 1, 200/min_front, 100/min_left, 100/min_right, False)
 
            # Bug: avoid obstacles depending on dist to obstacles and heading to goal
            #steer, speed_korr = self.bug.modus_sinus(front, left, right, heading)

            # Print Robo Status
            print(colored("Robo-X : " + str(x) + "  Robo-Y : " + str(y) + "  Robo-Pose : "  + str(pose), "green"))
            print(f"Kompass-Heading: {heading}")
            print(f"Left : {self.bug.left:^10}  Dist: {self.bug.left_min:>10.2f}")
            print(f"Front: {self.bug.front:^10}  Dist: {self.bug.front_min:>10.2f}")
            print(f"Right: {self.bug.right:^10}  Dist: {self.bug.right_min:>10.2f}")

            print("Steer: " + str(steer) + "  Speed: " + str(speed))
                 
            # Avoid Steering force depending on the nearest obstacle, the distance and the angle to the obstacle
            #avoid_steering, max_left, max_right = self.avoid.get_nearest_obst(x, y, pose, obstacles)
            #steering_output, speed = self.planer.set_modus(x, y, pose, steer, speed, avoid_steering, max_left, max_right, False)
            #steer = steering_output * 0.5
            #print("Avoid_Steering: " + str(avoid_steering))
            #rint("Steering_Output: " + str(steering_output) + "  max_left: " + str(max_left) + "  max_right: " + str(max_right))

            # Get the rear axle position for Ackermann steering
            rear_axle_position = self.servo.get_analog()

            #Robo Moves
            self.motion.set_motion_ackermann_steering(steer, speed * 0.5, rear_axle_position) 

            #Stop if I2c failed
            if self.motion.motor_VL.get_motor_error() or \
                    self.motion.motor_VR.get_motor_error() or \
                    self.motion.motor_HL.get_motor_error() or \
                    self.motion.motor_HR.get_motor_error() or \
                    self.kompass.kompass_error_i2c:
                print("MOTION Error detected")
                self.motion.set_motion(0,0)
                sleep(5)

            self.pumper.status_led("off")

            #Logging Scan Data while running
            if speed != 0:
                loop_count += 1           
                aktual_data_this_loop = {   "scan_data": scan_data,
                                            "x": x,
                                            "y": y,
                                            "pose": pose,
                                            "steer": steer,
                                            "speed": speed,
                                            "front": front,
                                            "left": left,
                                            "right": right
                                        }
                #Make new Dict for each loop
                self.logging_all_data[loop_count] = aktual_data_this_loop
 
            #Logging with tabulate
            current_time = strftime("%H:%M:%S", localtime())
            logging_tabulate.append(OrderedDict([("Time",current_time),
                                                 ("Steer",steer), ("Speed", speed), 
                                                 ("Front", front), ("Left", left), ("Right", right),
                                                 ("X",x),("Y",y), ("Pose",pose), 
                                                 ("Axle-Pos",rear_axle_position), ("Current",current)]))

            print (colored('*** Loop time = ' + str(round(time() - loop_time,2)) + " ***", 'red', attrs=["bold"]))
            loop_time = time()
            
            sleep(1.05)

            #print('\033[9F\033[2k', end='')
            #os.system('clear')

if __name__ == '__main__':

    # Run the Robo main loop
    whegs = Whegs()    
    whegs.init()
    whegs.run()
