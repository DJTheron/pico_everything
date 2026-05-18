from LCD_Lib import LCD
import os
from time import sleep
from keys import keyY, left, right

images = os.listdir('images')
image = 0

def show_image(image):
    with open('images/' + images[image], 'rb') as f:
        LCD.buffer[:] = f.read()
    LCD.show()

def run():
    global image, images
    show_image(image)
    while True:
        if left.value() == 0:
            image += 1
            if image >= len(images):
                image = 0
            show_image(image)
            while left.value() == 0:
                pass
            sleep(0.05)
            
        elif right.value() == 0:
            image -= 1
            if image < 0:
                image = len(images) - 1
            show_image(image)
            while right.value() == 0:
                pass
            sleep(0.05)

        if keyY.value() == 0:
            while keyY.value() == 0:
                pass
            break