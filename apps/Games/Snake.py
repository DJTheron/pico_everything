from LCD_Lib import LCD
import time
from keys import up, down, left, right, keyY

GRID_SIZE = 15

def run():
    snake = [[2,7],[1,7],[0,7]]
    dir = [1,0]

    # input
    if up.value() == 0:
        dir = [0,-1]
    elif down.value() == 0:
        dir = [0,1]
    elif right.value() == 0:
        dir = [1,0]
    elif left.value() == 0:
        dir = [-1,0]

    # fysics

    # move snake
    for i in range(snake):
        snake[i][0] += dir[0]
        snake[i][1] += dir[1]

    # drawing