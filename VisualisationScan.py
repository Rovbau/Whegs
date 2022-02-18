from PIL import Image, ImageDraw
from math import atan
import random

class VisualisationScan():
    def __init__(self):
        self.IMAGESIZE = 600
        self.CENTER = self.IMAGESIZE / 2
        self.ZOOM = 0.5
        self.img = Image.new('RGB', (self.IMAGESIZE, self.IMAGESIZE), color = "lightgrey")
        self.img1 = ImageDraw.Draw(self.img)
        self.line_array = []

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
            print(index , round(slope,2), element)

            if (x1 > 1000) or (y1 > 1000):
                break
            
            if abs(abs(slope) - abs(slope_old)) < 0.2:                    #Find two segments with +/- same slope
                count += 1
                if count == 1:
                    first_leg  = [x1, y1]
                if count > 3:                                   #If line is long enough append
                    self.line_array.append([index, element])

                    self.img1.line([   (first_leg[0] * self.ZOOM) + self.CENTER, 
                                            (first_leg[1] * self.ZOOM) + self.CENTER, 
                                            (element[0] * self.ZOOM) + self.CENTER, 
                                            (element[1] * self.ZOOM) + self.CENTER], width = 3, fill = "blue")
            else:
                count = 0
            slope_old = slope

        self.store_drawing()
        print(self.line_array)

    def draw_scan(self, obstacles, position):
        """Draw all obstacles and robo position in a file"""
        #Overwrites existing Pixel with gray rectangle
        #self.img1.rectangle([0,0,self.IMAGESIZE, self.IMAGESIZE], fill = "lightgrey")

        color = random.choice(["red", "green", "maroon", "grey", "brown"])

        x, y, pose = position
        self.img1.rectangle([    (x * self.ZOOM) + self.CENTER, 
                                (y * self.ZOOM) + self.CENTER,
                                (x * self.ZOOM) + self.CENTER + 1 ,
                                (y * self.ZOOM) + self.CENTER + 1], fill = "green")

        for element in obstacles[::5]:
            
            self.img1.rectangle([   (element[0] * self.ZOOM) + self.CENTER, 
                                    (element[1] * self.ZOOM) + self.CENTER, 
                                    (element[0] * self.ZOOM) + self.CENTER + 1, 
                                    (element[1] * self.ZOOM) + self.CENTER + 1],  fill= color)

    def store_drawing(self):
        flipped = self.img.transpose(Image.FLIP_TOP_BOTTOM)
        flipped.save('pil_color.png')

if __name__ == "__main__":
    obstacles = [[190, 82], [191, 81], [195, 83], [198, 83], [203, 85], [207, 86], [208, 85], [214, 87], [219, 88], [223, 90], [227, 90], [229, 89], [234, 90], [244, 94], [245, 92], [255, 95], [263, 97], [265, 95], [268, 94], [267, 90], [265, 86], [265, 83], [268, 81], [266, 77], [266, 75], [265, 72], [266, 69], [267, 67], [268, 64], [267, 62], [268, 59], [269, 56], [269, 54], [270, 51], [270, 49], [271, 46], [270, 44], [271, 41], [272, 39], [271, 36], [271, 34], [271, 31], [273, 29], [272, 26], [274, 24], [277, 23], [276, 21], [276, 18], [277, 16], [277, 13], [279, 11], [279, 8], [280, 6], [281, 3], [281, 0], [281, -1], [281, -4], [284, -7], [284, -10], [286, -12], [289, -15], [287, -17], [294, -22], [294, -25], [286, -26], [282, -28], [282, -31], [283, -34], [286, -37], [288, -40], [286, -43], [286, -46], [287, -49], [287, -53], [287, -55], [302, -63], [302, -67], [302, -70], [304, -75], [304, -78], [305, -82], [306, -87], [309, -92], [307, -95], [203, -40], [203, -42], [198, -41], [198, -43], [197, -44], [193, -43], [192, -44]]
    visualisationScan = VisualisationScan()
    visualisationScan.draw_scan(obstacles, [0,0,0])
    visualisationScan.search_line(obstacles)
    print(visualisationScan.line_array)