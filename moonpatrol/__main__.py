import sys
import time
import random

import pygame

from data import load, filepath
import settings

JUMP = getattr(pygame, settings.JUMP)
SPEEDUP = getattr(pygame, settings.SPEEDUP)
SLOWDOWN = getattr(pygame, settings.SLOWDOWN)
QUIT = getattr(pygame, settings.QUIT)

def offscreen(x, y):
    maxx, maxy = settings.DISPLAY_SIZE
    return x > maxx or x < 0 or y > maxy or y < 0

class Pothole(pygame.sprite.Sprite):
    def __init__(self, image, *groups, **kwargs):
        x = kwargs.get('x', settings.DISPLAY_SIZE[0])
        super(Pothole, self).__init__(*groups)
        self.rect = pygame.Rect(
            (x - image.get_width() / 2, settings.GROUND_HEIGHT),
             image.get_size())
        self.image = pygame.transform.scale2x(image)

    def update(self):
        self.rect.move_ip(-settings.GROUND_SPEED, 0)
        if offscreen(*self.rect.center):
            self.kill()

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

class Bullet(pygame.sprite.Sprite):

    WIDTH = 3

    def __init__(self, x, y, speedx, speedy, *groups):
        super(Bullet, self).__init__(*groups)
        self.rect = pygame.Rect(x, y, x+speedx, y+speedy)
        self.image = pygame.Surface((speedx or self.WIDTH,
                                    speedy or self.WIDTH))
        pygame.draw.line(
            self.image,
            settings.BULLET_COLOUR,
            (0, 0), (speedx, speedy), self.WIDTH)
        self._speedx = speedx
        self._speedy = speedy

    def update(self):
        self.rect.move_ip(self._speedx, -self._speedy)
        if offscreen(*self.rect.topleft):
            self.kill()

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
        self._sounds = {
            'jump': pygame.mixer.Sound(filepath('jump.wav'))}

    def change_speed(self, direction):
        self._xspeed += direction * settings.BUGGY_SPEED
        self._xspeed = max(self._xspeed, -settings.BUGGY_SPEED)
        self._xspeed = min(self._xspeed, settings.BUGGY_SPEED)

    def jump(self, force=50):
        if not self._jumping:
            self._yspeed = -force
            self._jumping = True
            self._sounds['jump'].play()

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

def makepothole():
    return not random.randint(0, 10)

def main():
    """ your app starts here
    """
    pygame.init()

    screen = pygame.display.set_mode(settings.DISPLAY_SIZE)

    _bground = pygame.image.load(filepath('bground.png'))
    _car = pygame.image.load(filepath('patrol.png'))
    _pothole = pygame.image.load(filepath('pothole.png'))

    car = Car(_car, settings.GROUND_HEIGHT)
    bground = pygame.transform.scale(_bground, settings.DISPLAY_SIZE)

    background = Background(bground, 
                    settings.DISPLAY_SIZE[0], settings.SCROLL_SPEED)

    clock = pygame.time.Clock()
    pygame.mixer.music.load(filepath('pink-summertime.mod'))
    pygame.mixer.music.play(-1)

    # groups
    bullets = pygame.sprite.Group()
    potholes = pygame.sprite.Group()

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == JUMP: car.jump()
                if event.key == SPEEDUP: car.change_speed(1)
                if event.key == SLOWDOWN: car.change_speed(-1)
                if event.key == QUIT: sys.exit()
                if event.key == JUMP: 
                    Bullet(car._x, car._y, 0, 10, bullets)
                    Bullet(car._x, car._y, 10, 0, bullets)

        clock.tick(60)

        if makepothole():
            Pothole(_pothole, potholes)

        # blit first bit.
        screen.fill(settings.BLACK)
        background.render(screen)

        potholes.update()
        car.update()
        bullets.update()

        car.render(screen)
        bullets.draw(screen)
        potholes.draw(screen)

        pygame.display.flip()
