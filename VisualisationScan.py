from PIL import Image, ImageDraw
     


class VisualisationScan():
    def __init__(self):
        IMAGESIZE = 300
        self.CENTER = IMAGESIZE / 2
        self.ZOOM = 0.5
        self.img = Image.new('RGB', (IMAGESIZE, IMAGESIZE), color = "lightgrey")
        self.img1 = ImageDraw.Draw(self.img)

    def draw_scan(self, obstacles, position):
        self.img1.rectangle([0,0,300,300], fill = "lightgrey")
        x, y, pose = position
        self.img1.rectangle([    (x * self.ZOOM) + self.CENTER, 
                                (y * self.ZOOM) + self.CENTER,
                                (x * self.ZOOM) + self.CENTER + 1 ,
                                (y * self.ZOOM) + self.CENTER + 1], fill = "green")

        for element in obstacles:
            self.img1.rectangle([   (element[0] * self.ZOOM) + self.CENTER, 
                                    (element[1] * self.ZOOM) + self.CENTER, 
                                    (element[0] * self.ZOOM) + self.CENTER + 1, 
                                    (element[1] * self.ZOOM) + self.CENTER + 1], fill = "red")

        self.store_drawing()

    def store_drawing(self):
        flipped = self.img.transpose(Image.FLIP_TOP_BOTTOM)
        flipped.save('pil_color.png')

