from Scanner3d import *



class Obstacles():
    def __init__(self):
        self.zeilen = 42
        self.spalten = 42
        self.sorted_list = [[0] * self.spalten for i in range(self.zeilen)]
        self.obstacle_array = [[0] * self.spalten for i in range(self.zeilen)]
        self.obstacles = [[]]

    def fill_array(self, scan_data):
        for element in scan_data:
            self.sorted_list[20+int(element[0]/1.8)][20+int(element[1]/1.8)] = element[2]
        return(self.sorted_list)
    
    def pretty_print(self, sorted_list):
        print("   "),
        for spalte, element in enumerate(sorted_list[0]):
            print("%3d" % spalte),
        print("\n")
        
        for zeile, line in enumerate(sorted_list):
            print(str(zeile) + ") "),
            for element in line:
                print("%3d" % element),
            print("\n")

    def get_obstacle_array(self):
        return(self.obstacle_array)

    def find_obstacles(self, sorted_list):
        for spalte in range(self.spalten):
            
            connect = False
            for zeile in range(self.zeilen - 1):
                next_to = (sorted_list[zeile][spalte] - sorted_list[zeile+1][spalte])
                
                if abs(next_to) < 5 and next_to != 0:
                    if connect == False:
                        self.obstacles.append(
                            [zeile, spalte, sorted_list[zeile+1][spalte]])
                        self.obstacle_array[zeile+1][spalte] = 888
                        connect = True
                    else:
                        self.obstacles[-1] = (
                            [self.obstacles[-1] , [zeile, spalte, sorted_list[zeile+1][spalte]]])
                        self.obstacle_array[zeile+1][spalte] = 888
                else:
                    connect = False
        return(self.obstacles)

if __name__ == "__main__":

    scanner = Scanner()
    obstacles = Obstacles()

    scanner.do_3D_scan(step = 150, min_heading = -36, max_heading = 36,
                                 min_pitch = -9.0,  max_pitch = 9.0)
    scan_data = scanner.get_scan_data()
    scanner.scanner_reset()

    #scan_data =[     [0, 0, 72], [0, 1.8, 73], [0, 3.6, 74], [0, 5.4, 75], [0, 7.2, 75],[0, 9.0, 76], [0, 10.8, 77], [-1.8, 10.8, 78], [-1.8, 9.0, 75],[-1.8, 7.2, 78], [-1.8, 5.4, 77], [-1.8, 3.6, 75], [-1.8, 1.8, 75],
             #   [-1.8, 0.0, 73], [-1.8, -1.8, 73], [-1.8, -3.6, 72], [-1.8, -5.4, 71],[-1.8, -7.2, 68], [-1.8, -9.0, 67], [-1.8, -10.8, 59],[-3.6, -10.8, 63], [-3.6, -9.0, 61], [-3.6, -7.2, 58],[-3.6, -5.4, 66], [-3.6, -3.6, 65], [-3.6, -1.8, 72],
              #  [-3.6, 0.0, 73], [-3.6, 1.8, 73], [-3.6, 3.6, 74], [-3.6, 5.4, 73]]

    sorted_list = obstacles.fill_array(scan_data)
    obstacles.pretty_print(sorted_list)

    print(obstacles.find_obstacles(sorted_list))

    obstacles.pretty_print(obstacles.get_obstacle_array())

    for  element in obstacles.obstacles[1:]:
        pos = scanner.get_scan_data()
        print(element)
        if len(element) < 3:
            element = element[0]
        scanner.stepper_heading.do_step(element[1]-6)
        scanner.stepper_pitch.do_step  (element[0]-6)
        sleep(1)
        scanner.stepper_heading.do_step(-1*(element[1]-6))
        scanner.stepper_pitch.do_step  (-1*(element[0]-6))
        sleep(1)



            
  
