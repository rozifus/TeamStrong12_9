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

def nearborder(entity, dist, rect=None):
    # returns bool list for near [up, right, down, left]
    near = [False] * 4
    entity_size = entity._image.get_size()
    if rect == None: 
        rect = pygame.Rect(0,0,settings.DISPLAY_SIZE[0],
                               settings.DISPLAY_SIZE[1])
    if entity.rect.right + dist > rect.right:
        near[1] = True
    if entity.rect.x - dist < rect.x:
        near[3] = True
    if entity.rect.bottom + dist > rect.bottom:
        near[2] = True
    if entity.rect.y - dist < rect.y:
        near[0] = True
    return near

class Pothole(pygame.sprite.Sprite):
    def __init__(self, image, *groups, **kwargs):
        x = kwargs.get('x', settings.DISPLAY_SIZE[0])
        super(Pothole, self).__init__(*groups)
        self.rect = pygame.Rect(
            (x - image.get_width() / 2, settings.GROUND_HEIGHT-1),
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

class Ufo(pygame.sprite.Sprite):

    WIDTH = 3
    _image = pygame.transform.scale(
                pygame.image.load(filepath('ufo.png')),
                (60,24))

    def __init__(self, x, y, container, *groups):
        super(Ufo, self).__init__(*groups)
        self.rect = pygame.Rect(x, y, Ufo._image.get_size()[0], Ufo._image.get_size()[1] )
        self.image = Ufo._image 
        self.container = container
        self._accelx = 0.1 
        self._accely = 0.1 
        self._speedx = 2  
        self._speedy = 2

    def update(self):
        self.rect.move_ip(self._speedx, -self._speedy)

        near = nearborder(self, 80, self.container)
        if near[0]: 
            self._speedy -= self._accely
        if near[2]:
            self._speedy += self._accely
        if near[1]:
            self._speedx -= self._accelx
        if near[3]: 
            self._speedx += self._accelx
        if offscreen(*self.rect.topleft):
            self.kill()

class Car(pygame.sprite.Sprite):
    def __init__(self, image, groundy, *groups):
        super(Car, self).__init__(*groups)
        self._speed = 0
        self.image = image.convert_alpha()
        self.rect = pygame.Rect(
            (100, groundy), image.get_size())

        self._xspeed = 0
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
        self.rect.move_ip(self._xspeed, self._yspeed)
        if self.rect.bottom >= self._groundy:
            self._yspeed = 0
            self.rect.bottom = self._groundy
            self._jumping = False

def makepothole():
    return not random.randint(0, 100)

def main():
    """ your app starts here
    """
    pygame.init()

    screen = pygame.display.set_mode(settings.DISPLAY_SIZE)

    _bground = pygame.image.load(filepath('bground.png'))
    _car = pygame.image.load(filepath('patrol.png'))
    _pothole = pygame.image.load(filepath('pothole.png'))

    allsprites = pygame.sprite.Group()
    car = Car(_car, settings.GROUND_HEIGHT, allsprites)
    bground = pygame.transform.scale(_bground, settings.DISPLAY_SIZE)

    background = Background(bground, 
                    settings.DISPLAY_SIZE[0], settings.SCROLL_SPEED)

    clock = pygame.time.Clock()
    pygame.mixer.music.load(filepath('pink-summertime.mod'))
    pygame.mixer.music.play(-1)

    # groups
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    ufo = Ufo(100, 100, pygame.Rect(0,0, settings.DISPLAY_SIZE[0], 
                                    settings.DISPLAY_SIZE[1]-300), 
              enemies)
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
                    rect = car.rect
                    Bullet(rect.left, rect.top, 0, 10, bullets)
                    Bullet(rect.centerx, rect.centery, 10, 0, bullets)

        clock.tick(60)

        if makepothole():
            Pothole(_pothole, potholes)

        # blit first bit.
        screen.fill(settings.BLACK)
        background.render(screen)

        enemies.update()
        potholes.update()
        allsprites.update()
        bullets.update()

        allsprites.draw(screen)
        enemies.draw(screen)
        bullets.draw(screen)
        potholes.draw(screen)

        # check player dead conditions.
        if pygame.sprite.spritecollideany(car, potholes):
            car.kill()
            print "DED!"

        pygame.display.flip()
