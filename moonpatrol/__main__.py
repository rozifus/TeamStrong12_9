import sys
import time
import random

import pygame
from pygame.transform import scale2x, scale
from pygame.image import load

from data import filepath
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

    _pothole00 = scale2x(load(filepath('pothole00.png')))
    _pothole01 = scale2x(load(filepath('pothole01.png')))
    _potholes = [_pothole00,_pothole01]

    def __init__(self, x, *groups, **kwargs):
        super(Pothole, self).__init__(*groups)
        self.image = self._potholes[random.randint(0,len(self._potholes)-1)]
        self.rect = pygame.Rect( (x, settings.GROUND_HEIGHT-1), 
                                 self.image.get_size() )

    def update(self):
        self.rect.move_ip(-settings.GROUND_SPEED, 0)
        if offscreen(*self.rect.center):
            self.kill()

class Background(object):

    def __init__(self, images, maxx, y, scrollspeed, randomize=False):
        if not isinstance(images, list): images = [images]

        self._scrollspeed = scrollspeed
        self._randomize = randomize
        self._maxx = maxx
        self._images = images
        # image map is list of [image_index, image_location]
        self._image_map = [[0,0],] 
        self._y = y

    def render(self, screen):
        # move all images left and blit
        for im in self._image_map:
            im[1] -= self._scrollspeed
            screen.blit(self._images[im[0]], (im[1],self._y))
        # while there are not enough images on screen
        while(self._image_map[-1][1] < self._maxx):
            # get info for the last image
            last = self._image_map[-1]
            # if we're going random pick a random new image
            if self._randomize: 
                next_image = random.randint(0, len(self._images)-1)
            # otherwise get the next image in our _images list
            else: next_image = (last[0]+1) % len(self._images)
            # place the next image at the end of the last image
            self._image_map.append(
                    [ next_image, 
                      last[1]+self._images[last[0]].get_size()[0] ] )
        # if the first image has moved off screen, pop it!
        if self._image_map[0][1] + \
           self._images[self._image_map[0][0]].get_size()[0] < 0:
                self._image_map.pop(0)

class Bullet(pygame.sprite.Sprite):

    WIDTH = 3

    def __init__(self, x, y, speedx, speedy, *groups):
        super(Bullet, self).__init__(*groups)
        width, height = speedx or self.WIDTH, speedy or self.WIDTH
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height))
        pygame.draw.line(
            self.image,
            settings.BULLET_COLOUR,
            (0, 0), (speedx, speedy), self.WIDTH)
        self._speedx = speedx
        self._speedy = speedy
        self._distancex = 0

    def update(self):
        self.rect.move_ip(self._speedx, -self._speedy)
        self._distancex += self._speedx
        outofrange = self._distancex > settings.BUGGY_BULLET_RANGE
        if offscreen(*self.rect.topleft) or outofrange:
            self.kill()

class Ufo(pygame.sprite.Sprite):

    _image = scale(load(filepath('ufo.png')), (60,24))

    def __init__(self, x, y, container, *groups):
        super(Ufo, self).__init__(*groups)
        width, height = self._image.get_size()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self._image 
        self.container = container
        self._accelx = 0.1 
        self._accely = 0.1 
        self._speedx = 2  
        self._speedy = 2
        self._sounds = {
            'dead': pygame.mixer.Sound(filepath('explosion.wav'))}

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

class Bomb(pygame.sprite.Sprite):

    _image = scale2x(load(filepath('bomb.png')))

    def __init__(self, x, y, *groups):
        super(Bomb, self).__init__(*groups)
        width, height = self._image.get_size()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self._image 
        self._speedx = 0  
        self._speedy = 0 
        self._sounds = {
            'dead': pygame.mixer.Sound(filepath('explosion.wav'))}

    def update(self):
        self._speedy += settings.GRAVITY
        self.rect.move_ip(self._speedx, self._speedy)

class Car(pygame.sprite.Sprite):


    def __init__(self, images, groundy, *groups):
        super(Car, self).__init__(*groups)
        self._speed = 0
        if not isinstance(images, list): images = [images]
        self.images = images
        self.image = self.images[0] 
        self.current_image = 0
        self.image_clock = 0
        self.rect = pygame.Rect(
            (100, groundy), images[0].get_size())

        self._xspeed = 0
        self._yspeed = 0
        self._groundy = groundy

        self._jumping = False
        self._sounds = {
            'dead': pygame.mixer.Sound(filepath('buggy-hit.wav')),
            'jump': pygame.mixer.Sound(filepath('jump.wav'))}

    def reset(self):
        """
        The car has died, reset its state.
        """
        self._xspeed = 0
        self._yspeed = 0
        self._jumping = False
        self.rect.left = 100
        self.rect.bottom = self._groundy

    def change_speed(self, direction):
        self._xspeed += direction * settings.BUGGY_SPEED
        self._xspeed = max(self._xspeed, -settings.BUGGY_SPEED)
        self._xspeed = min(self._xspeed, settings.BUGGY_SPEED)

    def jump(self, force=settings.BUGGY_JUMP_FORCE):
        if not self._jumping:
            self._yspeed = -force
            self._jumping = True
            self._sounds['jump'].play()

    def update(self):
        self.image_clock += 1
        if self.image_clock >= settings.BUGGY_ANIM_TIME:
            self.image_clock = 0
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]

        self._yspeed += settings.GRAVITY
        self._xspeed -= settings.BUGGY_FRICTION
        self.rect.move_ip(self._xspeed, self._yspeed)
        if self.rect.bottom >= self._groundy:
            self._yspeed = 0
            self.rect.bottom = self._groundy
            self._jumping = False

def makepothole(potholes):
    if not random.randint(0, 500):
        placepothole(settings.DISPLAY_SIZE[0], potholes)

def placepothole(x, potholes):
    Pothole(x, potholes)

class GameState(object):

    def __init__(self):
        self._initialtime = time.time()
        self.time = 0
        self.points = 0
        self.lives = 3
        self._distance = 0

    def update(self):
        self.time = (time.time() - self._initialtime)

    @property
    def distance(self):
        return self._distance / 100

    def incdist(self):
        self._distance += 1

    def incpoint(self):
        self.points += 1

def makebomb(x, y, bombs):
    if not random.randint(0, settings.UFO_BOMB_CHANCE):
        bomb = Bomb(x, y, bombs)

def makeenemy(enemies):
    if not random.randint(0, 50):
        width, height = settings.DISPLAY_SIZE
        ufo = Ufo(random.randint(50, 200), 100,
                  pygame.Rect(0,0, width, height - 300),
                  enemies)

def makehud(time, points, lives, distance):
    surf = pygame.Surface((350, 90))
    surf.fill((200, 114, 53))
    font = makehud.font
    time = font.render('TIME\t%d' % int(time), False, settings.HUD_TEXT)
    points = font.render('POINT\t%d' % int(points), False, settings.HUD_TEXT)
    lives = font.render('LIVES\t%d' % int(lives), False, settings.HUD_TEXT)
    distance = font.render('DIST\t%s' % ('|'*distance), False, settings.HUD_TEXT)
    surf.blit(time, (5, 10))
    surf.blit(points, (5, 40))
    surf.blit(lives, (5, 70))
    surf.blit(distance, (150, 40))
    return surf

def main():
    """ your app starts here
    """
    pygame.init()

    screen = pygame.display.set_mode(settings.DISPLAY_SIZE)

    _starfield = pygame.transform.scale(load(filepath('starfield.png')),
                                        (settings.DISPLAY_SIZE)).convert()
    _bground = load(filepath('mountains2.png')).convert_alpha()
    _terrain00 = scale2x(load(filepath('terrain00.png'))).convert_alpha()
    _terrain01 = scale2x(load(filepath('terrain01.png'))).convert_alpha()
    _midground = scale2x(load(filepath('mountains00.png'))).convert_alpha()
    _car0 = scale2x(load(filepath('rover00.png'))).convert_alpha()
    _car1 = scale2x(load(filepath('rover01.png'))).convert_alpha()
    _car2 = scale2x(load(filepath('rover02.png'))).convert_alpha()
    _car3 = scale2x(load(filepath('rover03.png'))).convert_alpha()

    allsprites = pygame.sprite.Group()
    car = Car([_car0,_car1,_car2,_car3], settings.GROUND_HEIGHT, allsprites)
    bground = pygame.transform.scale(_bground, settings.DISPLAY_SIZE)

    starfield = Background(_starfield, 
                    settings.DISPLAY_SIZE[0], 0, 0)
    background = Background(bground, 
                    settings.DISPLAY_SIZE[0], 100,
                    settings.SCROLL_SPEED)
    
    ground = Background([_terrain00, _terrain01],
                        settings.DISPLAY_SIZE[0],
                        settings.GROUND_HEIGHT,
                        settings.GROUND_SPEED)
    midground = Background(_midground,
                        settings.DISPLAY_SIZE[0], 200,
                        settings.SCROLL_SPEED + 1)

    clock = pygame.time.Clock()
    pygame.mixer.music.load(filepath('pink-summertime.mod'))
    pygame.mixer.music.play(-1)

    # groups
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    ufos = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    potholes = pygame.sprite.Group()
    bgrounds = [starfield, background, midground, ground]

    _font = pygame.font.Font(filepath('amiga4ever.ttf'), 16)
    makehud.font = _font

    gs = GameState()

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
                if event.key == pygame.K_p:
                    import pdb;pdb.set_trace()

        clock.tick(60)

        makepothole(potholes)
        makeenemy(enemies)

        # blit first bit.
        [b.render(screen) for b in bgrounds]

        gs.update();gs.incdist()
        enemies.update()
        potholes.update()
        bombs.update()
        allsprites.update()
        bullets.update()

        allsprites.draw(screen)
        enemies.draw(screen)
        bullets.draw(screen)
        potholes.draw(screen)
        bombs.draw(screen)

        # check player dead conditions.
        if pygame.sprite.spritecollideany(car, potholes):
            # ok player is dead, time to restart the level.
            potholes.empty()
            enemies.empty()
            bullets.empty()
            car.reset()
            car._sounds['dead'].play()
            gs.lives -= 1
            gs._distance = 0

        # check enemy dead conditions.
        collided = pygame.sprite.groupcollide(
                        bullets, enemies, True, True)

        for ufos in collided.values():
            for ufo in ufos:
                ufo._sounds['dead'].play()
                gs.incpoint()

        for ufo in enemies:
            makebomb(ufo.rect.x + ufo.rect.width/2, ufo.rect.bottom, bombs)

        for bomb in bombs:
            if bomb.rect.bottom - 5 > settings.GROUND_HEIGHT:
                placepothole(bomb.rect.x + bomb.rect.width/2, potholes)
                bomb.kill()
        # HUD display.
        hud = makehud(
            time=gs.time,
            points=gs.points,
            lives=gs.lives,
            distance=gs.distance)

        screen.blit(hud, (100, 500))

        pygame.display.flip()
