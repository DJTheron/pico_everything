from LCD_Lib import LCD
import framebuf
import random
import time
from keys import up, keyA, keyY

PIPE_WIDTH = 22
GAP_SIZE = 65

def load_in():
    LCD.fill(LCD.blue)
    LCD.show()

def makepipe():
    # [x, gap_y] — gap_y is the top of the opening
    return [240, random.randint(40, 150)]

def movepipe(pipe, speed):
    pipe[0] -= speed

def run():
    
    bird_v = 0
    bird_y = 120
    GRAVITY = 0.5
    load_in()
    pipes = []
    PIPESPEED = 5

    # bird sprite
    with open("flappybird.bin", "rb") as f:
        bird_buf = bytearray(f.read())
    bird_fb = framebuf.FrameBuffer(bird_buf, 16, 16, framebuf.RGB565)

    while True:
        frame_start = time.ticks_ms()
        # Input
        if keyA.value() == 0 or up.value() == 0:
            bird_v = -8

            # Debounce
            while keyA.value() == 0 or up.value() == 0:
                pass
            time.sleep(0.001)

        if keyY.value() == 0:
            return
            
        # Fysics    
        bird_y += bird_v + GRAVITY
        bird_v += 1

        if pipes == []:
            pipes.append(makepipe())
            pipecounter = 20

        pipecounter -= 1
        
        if pipecounter < 1:
            pipes.append(makepipe())
            pipecounter = 40
        
        for pipe in pipes:
            movepipe(pipe, PIPESPEED)
        pipes = [p for p in pipes if p[0] > -PIPE_WIDTH]


        # Drawing
        LCD.fill(LCD.blue)

        # draw birb
        LCD.blit(bird_fb, 60, int(bird_y), 0xF81F)

        for pipe in pipes:
            LCD.fill_rect(pipe[0], 0, PIPE_WIDTH, pipe[1], LCD.green)
            LCD.fill_rect(pipe[0], pipe[1] + GAP_SIZE, PIPE_WIDTH, 240 - pipe[1] - GAP_SIZE, LCD.green)


        LCD.show()

        elapsed = time.ticks_diff(time.ticks_ms(), frame_start)
        if elapsed < 50:
            time.sleep_ms(50 - elapsed)