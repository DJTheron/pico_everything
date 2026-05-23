from LCD_Lib import LCD
import framebuf
import time
from keys import up, keyA, keyY

def load_in():
    LCD.fill(LCD.blue)
    LCD.show()

def makepipe():
           # ycorner, xcorner, startingy, startingx
    return [20, 20, 60, 60]
    

def movepipe(pipe):
    pipe[3] += 5
    return pipe

def run():
    
    bird_v = 0
    bird_y = 120
    GRAVITY = 10
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
            bird_v = -20

            # Debounce
            while keyA.value() == 0 or up.value() == 0:
                pass
            time.sleep(0.001)

            if keyY.value() == 0:
                return
            
        # Fysics    
        bird_y += bird_v + GRAVITY
        bird_v -= 1

        if pipes == []:
            pipes.append(makepipe())
            pipecounter = 20
        
        if pipecounter < 1:
            pipes.append(makepipe())
        
        for pipe in pipes:
            movepipe(pipe)

        # Drawing
        LCD.fill(LCD.blue)

        # draw birb
        LCD.blit(bird_fb, 60, int(bird_y), 0xF81F)

        for pipe in pipes:
            LCD.fill_rect(pipe[0], pipe[1], pipe[2], pipe[3], LCD.green)


        LCD.show()

        elapsed = time.ticks_diff(time.ticks_ms(), frame_start)
        if elapsed < 50:
            time.sleep_ms(50 - elapsed)