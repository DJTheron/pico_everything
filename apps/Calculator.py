from LCD_Lib import LCD
import time
from keys import keyA, keyB, keyX, keyY, up, down, left, right

active_grid = [[0, 0, 0, 0],
               [0, 0, 0, 0],
               [0, 0, 0, 0],   
               [0, 0, 0, 0]]

x = 0
y = 0

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