import sys
import time
import random

import pygame

def main():
    """ your app starts here
    """
    pygame.init()
    screen = pygame.display.set_mode((320, 240))
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        time.sleep(0.1)
        screen.fill((0, random.randint(1, 255), 0))
        pygame.display.flip()
