import sys
import time
import random

import pygame

import settings

def main():
    """ your app starts here
    """
    pygame.init()
    screen = pygame.display.set_mode(settings.DISPLAY_SIZE)
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        time.sleep(0.1)
        screen.fill((0, random.randint(*settings.BACKGROUND_FLICKER), 0))
        pygame.display.flip()
