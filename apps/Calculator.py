#from LCD_Lib import LCD
import time
#from keys import keyA, keyB, keyX, keyY, up, down, left, right

# use the same idea to make a universal qwerty keyboard, with a cursor/ thing that highlights it yeah, and thats a universal keyboard lib for things like chatbot app and the messaging app

active_grid = [[0, 0, 0, 0],
               [0, 0, 0, 0],
               [0, 0, 0, 0],   
               [0, 0, 0, 0]]

display_grid = [["7", "8", "9", "+"],
                ["4", "5", "6", "*"],
                ["1", "2", "3", "-"],   
                ["0", ".", "AC", "/"]]
x = 0
y = 0

def rendergrid():
    active_grid[y][x] = 1
    print(active_grid)

def load_in():
    LCD.fill(0x0000)
    LCD.show()

def run():
    load_in()
    while True:
        if up.value() == 0:
            if y == 4:
                continue
            else:
                y += 1
            while up.value() == 0:
                pass
            time.sleep(0.05)    

        if down.value() == 0:
                if y == 0:
                    continue
                else:
                    y -= 1
                while down.value() == 0:
                    pass
                time.sleep(0.05)  
                
        if left.value() == 0:
            if x == 0:
                continue
            else:
                x -= 1
            while left.value() == 0:
                pass
            time.sleep(0.05)  
            
        if right.value() == 0:
            if x == 4:
                continue
            else:
                x += 1
            while right.value() == 0:
                pass
            time.sleep(0.05)
        
rendergrid()