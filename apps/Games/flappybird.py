from LCD_Lib import LCD
import framebuf
import random
import time
from keys import up, keyA, keyY

PIPE_WIDTH = 22
GAP_SIZE = 65
BIRD_X = 60
BIRD_SIZE = 16
SKY = 0xF49A

_BIRD_DATA = b'\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\xc2!\xc2!\xc2!\xc2!\xc2!\xc2!\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\xc2!\xc2!\xfe\xc7\xfe\xc7\xc2!\xff\xff\xff\xff\xff\xff\xc2!\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\xc2!\xfe\xc7\xfe\xc7\xfaG\xc2!\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc2!\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\xc2!\xfe\xc7\xfaG\xfaG\xfaG\xc2!?\xdd\xff\xff\xff\xff\xff\xff \x08\xff\xff\xc2!\x1f\xf8\x1f\xf8\xc2!\xfaG\xfaG\xfaG\xfaG\xfaG\xc2!?\xdd\xff\xff\xff\xff\xff\xff \x08\xff\xff\xc2!\x1f\xf8\x1f\xf8\xc2!\xc2!\xc2!\xc2!\xc2!\xfaG\xfaG\xc2!?\xdd\xff\xff\xff\xff\xff\xff\xff\xff\xc2!\x1f\xf8\xc2!\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc2!\xfaG\xfaG\xc2!\xc2!\xc2!\xc2!\xc2!\xc2!\x1f\xf8\xc2!\xfe\xc7\xff\xff\xff\xff\xff\xff\xfe\xc7\xc2!\xfaG\xfaG\xc2!\xa4-\xa4-\xa4-\xa4-\xa4-\xc2!\x1f\xf8\xc2!\xc2!\xc2!\xc2!\xc2!\xd4\x1f\xd4\x1f\xc2!\xa4-\xc2!\xc2!\xc2!\xc2!\xc2!\x1f\xf8\x1f\xf8\x1f\xf8\xc2!\xd4\x1f\xd4\x1f\xd4\x1f\xd4\x1f\xd4\x1f\xd4\x1f\xc2!\xa4-\xa4-\xa4-\xa4-\xc2!\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\xc2!\xc2!\xd4\x1f\xd4\x1f\xd4\x1f\xd4\x1f\xd4\x1f\xc2!\xc2!\xc2!\xc2!\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\xc2!\xc2!\xc2!\xc2!\xc2!\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8\x1f\xf8'

def load_in():
    LCD.fill(SKY)
    LCD.show()

def makepipe():
    # [x, gap_y, scored] — gap_y is the top of the opening
    return [240, random.randint(40, 150), False]

def movepipe(pipe, speed):
    pipe[0] -= speed

def run():
    
    bird_v = 0
    bird_y = 120
    GRAVITY = 0.6
    load_in()
    pipes = []
    PIPESPEED = 5
    flap_held = False
    dead = False
    score = 0

    bird_buf = bytearray(_BIRD_DATA)
    bird_fb = framebuf.FrameBuffer(bird_buf, 16, 16, framebuf.RGB565)

    while True:
        frame_start = time.ticks_ms()
        # Input
        pressing = keyA.value() == 0 or up.value() == 0
        if pressing and not flap_held:
            bird_v = -6
        flap_held = pressing

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
            pipecounter = 20
        
        for pipe in pipes:
            movepipe(pipe, PIPESPEED)
        pipes = [p for p in pipes if p[0] > -PIPE_WIDTH]

        # Score trigger — pipe fully passed the bird
        for pipe in pipes:
            if not pipe[2] and pipe[0] + PIPE_WIDTH < BIRD_X:
                pipe[2] = True
                score += 1

        # Collision detection
        bx1 = BIRD_X
        bx2 = BIRD_X + BIRD_SIZE
        by1 = int(bird_y)
        by2 = int(bird_y) + BIRD_SIZE

        if by1 < 0 or by2 > 240:
            dead = True

        for pipe in pipes:
            px1 = pipe[0]
            px2 = pipe[0] + PIPE_WIDTH
            gap_top = pipe[1]
            gap_bot = pipe[1] + GAP_SIZE
            overlaps_x = bx1 < px2 and bx2 > px1
            hits_top_pipe = by1 < gap_top
            hits_bot_pipe = by2 > gap_bot
            if overlaps_x and (hits_top_pipe or hits_bot_pipe):
                dead = True

        # Drawing
        LCD.fill(SKY)

        # draw birb
        LCD.blit(bird_fb, 60, int(bird_y), 0xF81F)

        for pipe in pipes:
            LCD.fill_rect(pipe[0], 0, PIPE_WIDTH, pipe[1], LCD.green)
            LCD.fill_rect(pipe[0], pipe[1] + GAP_SIZE, PIPE_WIDTH, 240 - pipe[1] - GAP_SIZE, LCD.green)

        LCD.show()

        elapsed = time.ticks_diff(time.ticks_ms(), frame_start)
        if elapsed < 50:
            time.sleep_ms(50 - elapsed)

        if dead == True:
            death_time = time.ticks_ms()
            while True:
                frame_start = time.ticks_ms()
                LCD.fill(0x0000)
                LCD.text(f"Score: {score}", 60, 40, LCD.green)
                LCD.show()

                if keyY.value() == 0:
                    return

                can_restart = time.ticks_diff(time.ticks_ms(), death_time) > 1000
                if can_restart and keyA.value() == 0:
                    bird_v = 0
                    bird_y = 120
                    load_in()
                    pipes = []
                    flap_held = False
                    dead = False
                    score = 0
                    break

                elapsed = time.ticks_diff(time.ticks_ms(), frame_start)
                if elapsed < 50:
                    time.sleep_ms(50 - elapsed)