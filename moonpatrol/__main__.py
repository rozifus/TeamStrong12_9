import sys
import time
import random

import pygame

from data import load, filepath
import settings

class Background(object):

    def __init__(self, image, maxx, scrollspeed):
        self._scrollspeed = settings.SCROLL_SPEED
        self._maxx = maxx
        self._image = image
        self._x1 = 0
        self._x2 = maxx

    def render(self, screen):

        # update first and second positions.
        self._x1 -= self._scrollspeed
        self._x2 -= self._scrollspeed
        if self._x1 <= -self._maxx:
            self._x1 = self._maxx
        if self._x2 <= -self._maxx:
            self._x2 = self._maxx

        # blit second part.
        screen.blit(self._image, (self._x1, 0))
        screen.blit(self._image, (self._x2, 0))

def main():
    """ your app starts here
    """
    pygame.init()

    screen = pygame.display.set_mode(settings.DISPLAY_SIZE)
    _bground = pygame.image.load(filepath('bground.png'))
    _car = pygame.image.load(filepath('patrol.png'))
    car = _car.convert_alpha()
    bground = pygame.transform.scale(_bground, settings.DISPLAY_SIZE)

    background = Background(bground, 
                    settings.DISPLAY_SIZE[0], settings.SCROLL_SPEED)

    clock = pygame.time.Clock()
    carx = 0

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        clock.tick(60)
        # blit first bit.
        screen.fill(settings.BLACK)
        background.render(screen)
        screen.blit(car, (carx, 400))
        carx += 1
        pygame.display.flip()
