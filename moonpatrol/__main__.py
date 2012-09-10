import sys
import time
import random

import pygame

from data import load, filepath
import settings

JUMP = getattr(pygame, settings.JUMP)
SPEEDUP = getattr(pygame, settings.SPEEDUP)
SLOWDOWN = getattr(pygame, settings.SLOWDOWN)

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

class Car(object):
    def __init__(self, image, groundy):
        self._speed = 0
        self._image = image.convert_alpha()
        self._x = 100
        self._xspeed = 0
        self._y = groundy
        self._yspeed = 0
        self._groundy = groundy
        self._jumping = False

    def change_speed(self, direction):
        self._xspeed += direction
        self._xspeed = max(self._xspeed, -1)
        self._xspeed = min(self._xspeed, 1)

    def jump(self, force=50):
        if not self._jumping:
            self._yspeed = -force
            self._jumping = True

    def update(self):
        self._yspeed += settings.GRAVITY
        self._y += self._yspeed
        if self._y >= self._groundy:
            self._yspeed = 0
            self._y = self._groundy
            self._jumping = False

        self._x += self._xspeed

    def render(self, screen):
        screen.blit(self._image, (self._x, self._y))

def main():
    """ your app starts here
    """
    pygame.init()

    screen = pygame.display.set_mode(settings.DISPLAY_SIZE)
    _bground = pygame.image.load(filepath('bground.png'))
    _car = pygame.image.load(filepath('patrol.png'))
    car = Car(_car, 400)
    bground = pygame.transform.scale(_bground, settings.DISPLAY_SIZE)

    background = Background(bground, 
                    settings.DISPLAY_SIZE[0], settings.SCROLL_SPEED)

    clock = pygame.time.Clock()
    pygame.mixer.music.load(filepath('summertime.ogg'))
    pygame.mixer.music.play(-1)

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == JUMP: car.jump()
                if event.key == SPEEDUP: car.change_speed(1)
                if event.key == SLOWDOWN: car.change_speed(-1)

        clock.tick(60)
        # blit first bit.
        screen.fill(settings.BLACK)
        background.render(screen)
        car.update()
        car.render(screen)
        pygame.display.flip()
