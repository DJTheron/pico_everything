import pygame
import random
import sys

SCREEN_SIZE = 240
PIPE_WIDTH = 22
GAP_SIZE = 65
PIPESPEED = 5
GRAVITY = 0.6
FPS = 20


def makepipe():
    return [240, random.randint(40, 150)]


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("Flappy Bird Test")
    clock = pygame.time.Clock()

    bird_img = pygame.image.load("apps/flappybird.png").convert_alpha()
    bird_img = pygame.transform.scale(bird_img, (16, 16))

    bird_y = 120.0
    bird_v = 0.0
    pipes = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_v = -6
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Physics — matches Pico exactly
        bird_y += bird_v + GRAVITY
        bird_v += 1

        # Pipes — matches Pico exactly
        if pipes == []:
            pipes.append(makepipe())
            pipecounter = 20

        pipecounter -= 1
        if pipecounter < 1:
            pipes.append(makepipe())
            pipecounter = 20

        for pipe in pipes:
            pipe[0] -= PIPESPEED
        pipes = [p for p in pipes if p[0] > -PIPE_WIDTH]

        # Drawing
        screen.fill((0, 0, 200))

        screen.blit(bird_img, (60, int(bird_y)))

        for pipe in pipes:
            pygame.draw.rect(screen, (0, 180, 0), (pipe[0], 0, PIPE_WIDTH, pipe[1]))
            pygame.draw.rect(screen, (0, 180, 0), (pipe[0], pipe[1] + GAP_SIZE, PIPE_WIDTH, 240 - pipe[1] - GAP_SIZE))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
