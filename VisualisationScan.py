from PIL import Image, ImageDraw
from math import atan
import random

class VisualisationScan():
    def __init__(self):
        self.IMAGESIZE = 600
        self.CENTER = self.IMAGESIZE / 2
        self.ZOOM = 0.8
        self.img = Image.new('RGB', (self.IMAGESIZE, self.IMAGESIZE), color = "lightgrey")
        self.img1 = ImageDraw.Draw(self.img)
        self.line_array = []


    def search_LSRegression(self, obstacles):
        """Find an straight line in obstacles[x , y] with least quare regression"""
        slope_old = 0
        average = 6
        count = 0
        self.line_array = []
        for i in range(len(obstacles)-3):  #Iterate trough obstacles 

            first_leg =  self.least_square_reg(obstacles[i: i+average])
            second_leg = self.least_square_reg(obstacles[i+3: i+average+3])

            #print(obstacles[i], 10  * abs(abs(first_leg) - abs(second_leg)))

            if abs(abs(first_leg) - abs(second_leg)) < 0.2:                    #Find two segments with +/- same slope
                count += 1 

                #if (obstacles[i][0] > 5000) or (obstacles[i][1] > 5000):
                 #   count = 0
                  #  break
                
                if count == 1:
                    first  = obstacles[i]
                if count > 5:                                   #If line is long enough append
                    self.line_array.append([i, obstacles[i]])

                    self.img1.line([   (first[0] * self.ZOOM) + self.CENTER, 
                                            (first[1] * self.ZOOM) + self.CENTER, 
                                            (obstacles[i][0] * self.ZOOM) + self.CENTER, 
                                            (obstacles[i][1] * self.ZOOM) + self.CENTER], width = 1, fill = "green")
            else:
                count = 0
        self.store_drawing()
        #print(self.line_array)

    def least_square_reg(self, points):
        # Total number of values
        number = len(points)
        # Mean X and Y
        means_xy = [sum(i) for i in zip(*points)]
        mean_x = means_xy[0] / number
        mean_y = means_xy[1] / number

        # Using the formula to calculate slope
        numer = 0
        denom = 0
        for i in range(number):
            numer += (points[i][0] - mean_x) * (points[i][1] - mean_y)
            denom += (points[i][0] - mean_x) ** 2
        slope = atan(numer / (denom + 0.001))
        y_intercept = mean_y - (slope * mean_x)
        return(slope)

    def search_line(self, obstacles):
        """Find an straight line in obstacles[x , y]"""
        slope_old = 0
        step = 4
        count = 0
        self.line_array = []
        for index, element in enumerate(obstacles[:-step:step]):  #Iterate trough obstcles with steps
            x1 = obstacles[index * step][0]
            x2 = obstacles[index * step + step][0]
            y1 = obstacles[index * step][1]
            y2 = obstacles[index * step + step][1]    
            slope = atan((y1 - y2 ) / (x1 - x2 + 0.1))              #Calc the slope 0°=0, 45°=0.78, 90=1.57, 135°=-0.78 ...
            #print(index , round(slope,2), element)

            if (x1 > 1000) or (y1 > 1000):
                break
            
            if abs(abs(slope) - abs(slope_old)) < 0.2:                    #Find two segments with +/- same slope
                count += 1
                if count == 1:
                    first_leg  = [x1, y1]
                if count > 10:                                   #If line is long enough append
                    self.line_array.append([index, element])

                    self.img1.line([   (first_leg[0] * self.ZOOM) + self.CENTER, 
                                            (first_leg[1] * self.ZOOM) + self.CENTER, 
                                            (element[0] * self.ZOOM) + self.CENTER, 
                                            (element[1] * self.ZOOM) + self.CENTER], width = 3, fill = "blue")
            else:
                count = 0
            slope_old = slope

        self.store_drawing()
        #print(self.line_array)

    def draw_scan(self, obstacles, position):
        """Draw all obstacles and robo position in a file"""
        #Overwrites existing Pixel with gray rectangle
        #self.img1.rectangle([0,0,self.IMAGESIZE, self.IMAGESIZE], fill = "lightgrey")

        color = random.choice(["red", "yellow", "maroon", "grey", "brown"])

        x, y, pose = position
        self.img1.rectangle([    (x * self.ZOOM) + self.CENTER, 
                                (y * self.ZOOM) + self.CENTER,
                                (x * self.ZOOM) + self.CENTER + 1 ,
                                (y * self.ZOOM) + self.CENTER + 1], fill = "green")

        for element in obstacles:
            
            self.img1.rectangle([   (element[0] * self.ZOOM) + self.CENTER, 
                                    (element[1] * self.ZOOM) + self.CENTER, 
                                    (element[0] * self.ZOOM) + self.CENTER + 2, 
                                    (element[1] * self.ZOOM) + self.CENTER + 2],  fill= color)
        self.store_drawing()

    def store_drawing(self):
        flipped = self.img.transpose(Image.FLIP_TOP_BOTTOM)
        flipped.save('pil_color.png')

if __name__ == "__main__":
    obstacles = [[190, 82], [191, 81], [195, 83], [198, 83], [203, 85], [207, 86], [208, 85], [214, 87], [219, 88], [223, 90], [227, 90], [229, 89], [234, 90], [244, 94], [245, 92], [255, 95], [263, 97], [265, 95], [268, 94], [267, 90], [265, 86], [265, 83], [268, 81], [266, 77], [266, 75], [265, 72], [266, 69], [267, 67], [268, 64], [267, 62], [268, 59], [269, 56], [269, 54], [270, 51], [270, 49], [271, 46], [270, 44], [271, 41], [272, 39], [271, 36], [271, 34], [271, 31], [273, 29], [272, 26], [274, 24], [277, 23], [276, 21], [276, 18], [277, 16], [277, 13], [279, 11], [279, 8], [280, 6], [281, 3], [281, 0], [281, -1], [281, -4], [284, -7], [284, -10], [286, -12], [289, -15], [287, -17], [294, -22], [294, -25], [286, -26], [282, -28], [282, -31], [283, -34], [286, -37], [288, -40], [286, -43], [286, -46], [287, -49], [287, -53], [287, -55], [302, -63], [302, -67], [302, -70], [304, -75], [304, -78], [305, -82], [306, -87], [309, -92], [307, -95], [203, -40], [203, -42], [198, -41], [198, -43], [197, -44], [193, -43], [192, -44]]
    praell_obs = [[-170, -80], [-172, -78], [-178, -77], [-182, -76], [-184, -73], [-187, -71], [-264, -124], [-268, -122], [-276, -121], [-278, -116], [-284, -113], [-289, -111], [-292, -107], [-297, -103], [-301, -100], [-75, 31], [-76, 32], [-73, 35], [-74, 35], [-73, 37], [-75, 37], [-75, 39], [-77, 39], [-80, 38], [-110, 29], [-279, -29], [-222, -4], [-112, 33], [-94, 41], [-96, 42], [-100, 43], [-103, 44], [-106, 44], [-107, 45], [-109, 47], [-112, 48], [-116, 49], [-121, 50], [-122, 52], [-127, 52], [-131, 54], [-135, 56], [-140, 57], [-144, 59], [-147, 62], [-165, 62], [-270, 63], [-268, 67], [-266, 71], [-158, 71], [-157, 74], [-261, 83], [-260, 87], [-259, 90], [-258, 94], [-256, 98], [-254, 102], [-253, 105], [-250, 109], [-250, 112], [-249, 116], [-205, 111], [-95, 88], [-54, 80], [-52, 80], [-52, 80], [-52, 81], [-55, 83], [-57, 84], [-233, 148], [-233, 152], [-231, 155], [-228, 158], [-228, 162], [-227, 165], [-136, 128], [-106, 115], [-105, 116], [-222, 181], [-220, 185], [-220, 188], [-220, 193], [-218, 196], [-216, 200], [-214, 203], [-213, 207], [-213, 211], [-212, 215], [-136, 163], [-134, 165]]
    
    visualisationScan = VisualisationScan()
    visualisationScan.draw_scan(praell_obs, [0,0,0])
    visualisationScan.search_LSRegression(praell_obs)

    #visualisationScan.search_line(obstacles)
    #print(visualisationScan.line_array)

    