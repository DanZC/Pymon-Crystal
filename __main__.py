music_dir = 'Music/'
me_dir = 'ME/'
sound_dir = 'Sounds/'
map_dir = 'Maps/'
spr_dir = 'Sprites/'
ui_dir = 'UI/'

import random

import pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=40960)
music = pygame.mixer.music
pygame.font.init()
Time = pygame.time
clock = pygame.time.Clock()

import pygame.midi

import math
import time
from time import time
import engine
import project
from pytmx.util_pygame import load_pygame
import sys
import types
import asyncio

game_title = ''
# game_icon = pygame.image.load('icon.png')

red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
yellow = (255, 255, 0)
white = (255, 255, 255)
black = (0, 0, 0)

display_width = 320
display_height = 288

resolution_factor = 1

block_size = 32

fps = 30

KEY_A = False
KEY_A_DOWN = False
KEY_B = False
KEY_START = False
KEY_UP = False
KEY_DOWN = False
KEY_LEFT = False
KEY_RIGHT = False

DIR_LEFT = 0
DIR_RIGHT = 1
DIR_UP = 2
DIR_DOWN = 3

print('Setting up...')


class GameData:
    def __init__(self):
        self.vars = []
        for x in range(100):
            self.vars.append(0)
        self.flags = []
        for x in range(100):
            self.flags.append(False)


class SaveData:
    def __init__(self):
        self.player = player.data
        self.game = gameData
    def sync(self):
        self.player = player.data
        self.game = gameData
    def export(self,file_path):
        pass


class AnimatedTile:
    def __init__(self, loc, images):
        #print('new tile at ',loc[0],' ',loc[1])
        self.x = loc[0]
        self.y = loc[1]
        self.gidlist = images
        self.images = []
        for gid in self.gidlist:
            self.images.append(map.get_tile_image_by_gid(gid))
        self.frame = 0
        self.pause = 2
        self.max_frame = len(images) - 1

    def draw(self):
        self.pause -= 1
        if self.pause <= 0:
            if self.frame == self.max_frame:
                self.frame = 0
            else:
                self.frame += 1
            self.pause = 2
        gameDisplay.blit(self.images[self.frame],(self.x - cam.x, self.y - cam.y))


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.center_on_player = True
        self.width = display_width
        self.height = display_height

    def realign(self):
        self.x = ((player.x - (display_width / 2)) / 32.0) * 32.0
        self.y = ((player.y - (display_height / 2)) / 32.0) * 32.0

    def set_pos(self, x=0, y=0):
        self.x = x
        self.y = y

    def draw(self):
        if 'tile_border' in map.properties:
            gameDisplay.blit(map_base, ((-64*6)-cam.x, (-64*6)-cam.y))
        else:
            gameDisplay.fill(black)


class ScreenCover:
    def __init__(self):
        self.color = white
        self.alpha = 255
        obj_list.append(self)

    def draw(self):
        color_alpha = (self.color[0],self.color[1],self.color[2],self.alpha)
        pygame.draw.rect(gameDisplay, color_alpha,[0,0, display_width, display_height])



class Player:
    def __init__(self):
        self.data = engine.PlayerData()
        self.layer = 0
        self.x = block_size * 10
        self.y = block_size * 8
        self.move_speed = 4
        self.dir = DIR_DOWN
        self.dest_x = self.x
        self.dest_y = self.y
        self.isMoving = False
        self.isBusy = False
        self.step = 0
        self.spr_f = pygame.image.load('Player/Male/Gold.png')
        self.spr_down = pygame.transform.chop(pygame.transform.chop(self.spr_f, (32,0,0,0)), (32,32,128,128))
        self.spr_down_s0 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,32,0)), (32,32,128,128))
        self.spr_down_s1 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,96,0)), (32,32,128,128))
        self.spr_left = pygame.transform.chop(pygame.transform.chop(self.spr_f, (32,0,0,32)), (32,32,128,128))
        self.spr_left_s0 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,32,32)), (32, 32, 128, 128))
        self.spr_left_s1 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,96,32)), (32, 32, 128, 128))
        self.spr_right = pygame.transform.chop(pygame.transform.chop(self.spr_f, (32,0,0,64)), (32,32,128,128))
        self.spr_right_s0 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,32,64)), (32, 32, 128, 128))
        self.spr_right_s1 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,96,64)), (32, 32, 128, 128))
        self.spr_up = pygame.transform.chop(pygame.transform.chop(self.spr_f, (32,0,0,96)), (32,32,128,128))
        self.spr_up_s0 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0, 0,32,96)), (32,32,128,128))
        self.spr_up_s1 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0, 0,96,96)), (32,32,128,128))
        self.sprite = self.spr_left_s0

    def move(self, x=0, y=0):
        self.dest_x = self.x + (block_size * x)
        self.dest_y = self.y + (block_size * y)
        self.isMoving = True
        self.step += 1
        if self.step > 1:
            self.step = 0

    def update(self):
        if self.x % block_size == 0 and self.y % block_size == 0:
            if self.x == self.dest_x and self.y == self.dest_y:
                if KEY_UP:
                    self.dir = DIR_UP
                    if get_tile_walkable(self.x,self.y - block_size, self.layer):
                        self.move(0, -1)
                elif KEY_DOWN:
                    self.dir = DIR_DOWN
                    if get_tile_walkable(self.x, self.y + block_size, self.layer):
                        self.move(0, 1)
                elif KEY_LEFT:
                    self.dir = DIR_LEFT
                    if get_tile_walkable(self.x - block_size, self.y, self.layer):
                        self.move(-1, 0)
                elif KEY_RIGHT:
                    self.dir = DIR_RIGHT
                    if get_tile_walkable(self.x + block_size, self.y, self.layer):
                        self.move(1, 0)
                if KEY_A_DOWN:
                    if self.dir == DIR_UP and not self.isBusy:
                        for obj in obj_list:
                            if obj.y == self.y - block_size and obj.x == self.x:
                                self.isBusy = True
                                obj.interact()
                    elif self.dir == DIR_DOWN and not self.isBusy:
                        for obj in obj_list:
                            if obj.y == self.y + block_size and obj.x == self.x:
                                self.isBusy = True
                                obj.interact()
                    elif self.dir == DIR_LEFT and not self.isBusy:
                        for obj in obj_list:
                            if obj.x == self.x - block_size and obj.y == self.y:
                                self.isBusy = True
                                obj.interact()
                    elif self.dir == DIR_RIGHT and not self.isBusy:
                        for obj in obj_list:
                            if obj.x == self.x + block_size and obj.y == self.y:
                                self.isBusy = True
                                obj.interact()
        if self.dest_x > self.x:
            self.x += self.move_speed
        elif self.dest_x < self.x:
            self.x -= self.move_speed
        if self.dest_y > self.y:
            self.y += self.move_speed
        elif self.dest_y < self.y:
            self.y -= self.move_speed
        if (self.x == self.dest_x and self.y == self.dest_y) and self.isMoving:
            on_enter_tile(self.x / 32, self.y / 32)
            self.isMoving = False

    def draw(self):
        if self.dir == DIR_LEFT:
            if (self.x % block_size > self.move_speed) and (self.x % block_size < block_size - self.move_speed):
                if self.step == 0:
                    self.sprite = self.spr_left_s0
                else:
                    self.sprite = self.spr_left_s1
            else:
                self.sprite = self.spr_left
        elif self.dir == DIR_RIGHT:
            if (self.x % block_size > self.move_speed) and (self.x % block_size < block_size - self.move_speed):
                if self.step == 0:
                    self.sprite = self.spr_right_s0
                else:
                    self.sprite = self.spr_right_s1
            else:
                self.sprite = self.spr_right
        elif self.dir == DIR_UP:
            if (self.y % block_size > self.move_speed) and (self.y % block_size < block_size - self.move_speed):
                if self.step == 0:
                    self.sprite = self.spr_up_s0
                else:
                    self.sprite = self.spr_up_s1
            else:
                self.sprite = self.spr_up
        elif self.dir == DIR_DOWN:
            if (self.y % block_size > self.move_speed) and (self.y % block_size < block_size - self.move_speed):
                if self.step == 0:
                    self.sprite = self.spr_down_s0
                else:
                    self.sprite = self.spr_down_s1
            else:
                self.sprite = self.spr_down
        gameDisplay.blit(self.sprite, ((self.x - cam.x) , (self.y - cam.y) - 8))
        #pygame.draw.rect(gameDisplay, red, [self.x - cam.x, self.y - cam.y, block_size, block_size])


class NPC:
    def __init__(self, x, y, img='char_ 44_D.png', direction = DIR_DOWN, mv_pattern = engine.mv_pattern_stationary):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.move_speed = 2
        self.mv_pattern = mv_pattern
        self.dir = direction
        self.radius = 3
        self.isMoving = False
        self.dest_x = self.x
        self.dest_y = self.y
        self.step = 0
        self.type = "npc"
        self.spr_f = pygame.image.load(spr_dir + img)
        self.spr_down = pygame.transform.chop(pygame.transform.chop(self.spr_f, (32,0,0,0)), (32,32,128,128))
        self.spr_down_s0 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,32,0)), (32,32,128,128))
        self.spr_down_s1 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,96,0)), (32,32,128,128))
        self.spr_left = pygame.transform.chop(pygame.transform.chop(self.spr_f, (32,0,0,32)), (32,32,128,128))
        self.spr_left_s0 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,32,32)), (32, 32, 128, 128))
        self.spr_left_s1 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,96,32)), (32, 32, 128, 128))
        self.spr_right = pygame.transform.chop(pygame.transform.chop(self.spr_f, (32,0,0,64)), (32,32,128,128))
        self.spr_right_s0 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,32,64)), (32, 32, 128, 128))
        self.spr_right_s1 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0,0,96,64)), (32, 32, 128, 128))
        self.spr_up = pygame.transform.chop(pygame.transform.chop(self.spr_f, (32,0,0,96)), (32,32,128,128))
        self.spr_up_s0 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0, 0,32,96)), (32,32,128,128))
        self.spr_up_s1 = pygame.transform.chop(pygame.transform.chop(self.spr_f, (0, 0,96,96)), (32,32,128,128))
        self.sprite = self.spr_down
        self.m = None
        #

    def update(self):
        if self.mv_pattern != engine.mv_pattern_stationary:
            if self.mv_pattern == engine.mv_pattern_walk:
                if self.x % block_size == 0 and self.y % block_size == 0:
                    if self.x == self.dest_x and self.y == self.dest_y:
                        n = random.randrange(0,768)
                        if n <= 3:
                            self.dir = DIR_UP
                            if (self.y - block_size) >= self.start_y - (self.radius * block_size):
                                if get_tile_walkable(self.x, self.y - block_size):
                                    self.move(0, -1)
                        elif n <= 6:
                            self.dir = DIR_DOWN
                            if (self.y + block_size) <= self.start_y + (self.radius * block_size):
                                if get_tile_walkable(self.x, self.y + block_size):
                                    self.move(0, 1)
                        elif n <= 9:
                            self.dir = DIR_LEFT
                            if (self.x - block_size) >= self.start_x - (self.radius * block_size):
                                if get_tile_walkable(self.x - block_size, self.y):
                                    self.move(-1,0)
                        elif n <= 12:
                            self.dir = DIR_RIGHT
                            if (self.x + block_size) <= self.start_x + (self.radius * block_size):
                                if get_tile_walkable(self.x + block_size, self.y):
                                    self.move(1,0)
                        else:
                            pass
            elif self.mv_pattern == engine.mv_pattern_look:
                n = random.randrange(0,768)
                if n <= 3:
                    self.dir = DIR_UP
                elif n <= 6:
                    self.dir = DIR_DOWN
                elif n <= 9:
                    self.dir = DIR_LEFT
                elif n <= 12:
                    self.dir = DIR_RIGHT
                else:
                    pass
        if self.dest_x > self.x:
            self.x += self.move_speed
        elif self.dest_x < self.x:
            self.x -= self.move_speed
        if self.dest_y > self.y:
            self.y += self.move_speed
        elif self.dest_y < self.y:
            self.y -= self.move_speed
        if self.x == self.dest_x and self.y == self.dest_y:
            self.isMoving = False

    def move(self, x=0, y=0):
        self.dest_x = self.x + (block_size * x)
        self.dest_y = self.y + (block_size * y)
        self.isMoving = True
        self.step += 1
        if self.step > 1:
            self.step = 0

    def interact(self):
        player.isBusy = False

    def draw(self):
        if self.dir == DIR_LEFT:
            if (self.x % block_size > self.move_speed) and (self.x % block_size < block_size - self.move_speed):
                if self.step == 0:
                    self.sprite = self.spr_left_s0
                else:
                    self.sprite = self.spr_left_s1
            else:
                self.sprite = self.spr_left
        elif self.dir == DIR_RIGHT:
            if (self.x % block_size > self.move_speed) and (self.x % block_size < block_size - self.move_speed):
                if self.step == 0:
                    self.sprite = self.spr_right_s0
                else:
                    self.sprite = self.spr_right_s1
            else:
                self.sprite = self.spr_right
        elif self.dir == DIR_UP:
            if (self.y % block_size > self.move_speed) and (self.y % block_size < block_size - self.move_speed):
                if self.step == 0:
                    self.sprite = self.spr_up_s0
                else:
                    self.sprite = self.spr_up_s1
            else:
                self.sprite = self.spr_up
        elif self.dir == DIR_DOWN:
            if (self.y % block_size > self.move_speed) and (self.y % block_size < block_size - self.move_speed):
                if self.step == 0:
                    self.sprite = self.spr_down_s0
                else:
                    self.sprite = self.spr_down_s1
            else:
                self.sprite = self.spr_down
        gameDisplay.blit(self.sprite, (self.x - cam.x, (self.y - cam.y) - 8))
        #pygame.draw.rect(gameDisplay, green, [self.x - cam.x, self.y - cam.y, block_size, block_size])


class Door:
    def __init__(self, x, y, dest_map, dest_x, dest_y, warp_type, width = block_size, height = block_size):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.dest_map = dest_map
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.warp_type = warp_type

    def interact(self):
        pass

    @asyncio.coroutine
    def warp(self):
        project.se_list[1].play()
        asyncio.sleep(0.05)

        asyncio.sleep(0.05)
        asyncio.sleep(0.05)
        engine.warp(self.dest_map, self.dest_x, self.dest_y)
        asyncio.sleep(0.05)
        asyncio.sleep(0.05)

    def draw(self):
        pass

    def inside_box(self, x, y):
        if ((x >= self.x) and (x < self.x + self.width)) and ((y >= self.y) and (y < self.y + self.height)):
            return True
        return False


class Signpost:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.type = "signpost"

    def interact(self):
        global inEvent
        inEvent = True
        print('start event')
        loop.run_until_complete(engine.show_text(self.text))
        print('event is done')
        player.isBusy = False
        inEvent = False

    def update(self):
        pass

    def draw(self):
        pass


class BerryTree:
    def __init__(self, x, y, berry):
        self.x = x
        self.y = y
        self.berry = berry
        self.type = "berrytree"

    def interact(self):
        global inEvent
        inEvent = True
        loop.run_until_complete(engine.show_text(project.str_list['berry_tree']))
        player.isBusy = False
        inEvent = False

    def update(self):
        pass

    def draw(self):
        pass


def on_enter_tile(x, y):
    for obj in obj_list:
        if obj.type == "door":
            if obj.inside_box(x*block_size,y*block_size):
                loop.run_until_complete(obj.warp())


def get_tile_walkable(x,y,layer=1):
    if (x / block_size < 0 or x / block_size >= map.width) or (y / block_size < 0 or y / block_size >= map.height):
        return False
    if (player.x == x and player.y == y) or (player.dest_x == x and player.dest_y == y):
        return False
    for obj in obj_list:
        if obj.type == "npc":
            if (obj.x == x and obj.y == y) or (obj.dest_x == x and obj.dest_y == y):
                return False
    props = map.get_tile_properties(x / block_size, y / block_size, 1)
    if 'isWalkable' in props:
        if (props['isWalkable'] == "True"):
            return True
        else:
            return False


def init_all():
    global ui_elements
    ui_elements = []


def main():
    global exit_game
    global KEY_LEFT
    global KEY_RIGHT
    global KEY_UP
    global KEY_DOWN
    global KEY_A_DOWN
    global KEY_A
    global KEY_NO_DIR
    load_tile_data()
    while not exit_game:
        KEY_A_DOWN = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit_game = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    KEY_LEFT = True
                elif event.key == pygame.K_RIGHT:
                    KEY_RIGHT = True
                elif event.key == pygame.K_UP:
                    KEY_UP = True
                elif event.key == pygame.K_DOWN:
                    KEY_DOWN = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    KEY_LEFT = False
                elif event.key == pygame.K_RIGHT:
                    KEY_RIGHT = False
                elif event.key == pygame.K_UP:
                    KEY_UP = False
                elif event.key == pygame.K_DOWN:
                    KEY_DOWN = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    KEY_A = True
                    KEY_A_DOWN = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_c:
                    KEY_A = False
        if not KEY_LEFT and not KEY_RIGHT and not KEY_UP and not KEY_DOWN:
            KEY_NO_DIR = True
        else:
            KEY_NO_DIR = False
        if not inEvent:
            update_all()
        draw_all()
        clock.tick(fps)


def update_all():
    for obj in obj_list:
        obj.update()
    player.update()


def get_tile_location_from_gid(gid):
    pgid = gid
    for layer in range(2):
        for y in range(map.height):
            for x in range(map.width):
                tgid = map.get_tile_gid(x,y,layer)
                if tgid == pgid:
                    return x,y,layer
    return 900,900,0


def load_map(name):
    global map
    map = load_pygame(map_dir + name + '.tmx')
    load_tile_data()
    load_obj_data()
    load_map_connections()
    load_map_border()
    if 'music' in map.properties:
        pygame.mixer.music.load(music_dir + map.properties['music'])
        pygame.mixer.music.play(-1,0.0)


def unload_map():
    del animated_tiles_0
    del tileimages_sub
    del tileimages_0
    del events
    del obj_list
    del connection_left
    del c_left_offset
    del c_left_tileimages_0
    del c_left_surface
    del connection_right
    del c_right_offset
    del c_right_tileimages_0
    del connection_up
    del c_up_offset
    del c_up_tileimages_0
    del connection_down
    del c_down_offset
    del c_down_tileimages_0
    del map


def load_map_from_connection(dir):
    if dir == DIR_LEFT:
        global map
        name = map.properties['connection_left']
        del map
        map = load_pygame(map_dir + name + '.tmx')
        player.x += connection_left.width; player.y -= c_left_offset
        del connection_left
        del c_left_offset
    elif dir == DIR_RIGHT:
        global map
        name = map.properties['connection_right']
        del map
        map = load_pygame(map_dir + name + '.tmx')
        player.x -= connection_right.width; player.y -= c_right_offset
    elif dir == DIR_UP:
        global map
        name = map.properties['connection_up']
        del map
        map = load_pygame(map_dir + name + '.tmx')
        player.y += connection_up.height; player.x -= c_up_offset
    elif dir == DIR_DOWN:
        global map
        name = map.properties['connection_down']
        del map
        map = load_pygame(map_dir + name + '.tmx')
        player.y -= connection_down.height; player.x -= c_down_offset
    load_tile_data()
    load_obj_data()
    load_map_connections()


def load_tile_data():
    global animated_tiles_0
    animated_tiles_0 = []
    global tileimages_sub
    tileimages_sub = []
    for y in range(map.height):
        for x in range(map.width):
            image_list = []
            props = map.get_tile_properties(x,y,0)
            if 'frames' in props:
                if len(props['frames']) > 1:
                    for animation_frame in props['frames']:
                        d = animation_frame.duration
                        i = animation_frame.gid
                        image_list.append(i)
                    animtile = AnimatedTile((x*block_size,y*block_size), image_list)
                    animated_tiles_0.append(animtile)
    global tileimages_0
    tileimages_0 = []
    for y in range(map.height):
        for x in range(map.width):
            image = map.get_tile_image(x, y, 1)
            tileimages_0.append((x, y, image.convert_alpha()))


def load_obj_data():
    global obj_list
    obj_list = []
    global events
    events = map.get_layer_by_name("Events")
    for obj in events:
        if obj.type == "NPC":
            if 'char_image' in obj.properties:
                mv_pat = engine.mv_pattern_stationary
                if 'move_type' in obj.properties:
                    if obj.properties['move_type'] == 'stationary':
                        mv_pat = engine.mv_pattern_stationary
                    elif obj.properties['move_type'] == 'walk':
                        mv_pat = engine.mv_pattern_walk
                    elif obj.properties['move_type'] == 'look':
                        mv_pat = engine.mv_pattern_look
                npc = NPC(obj.x, obj.y, obj.properties['char_image'], mv_pat)
            else:
                npc = NPC(obj.x, obj.y)
            obj_list.append(npc)
        elif obj.type == "signpost":
            sign = Signpost(obj.x, obj.y, obj.properties['text'])
            obj_list.append(sign)
        elif obj.type == "door":
            door = Door()
            obj_list.append(door)


def load_map_connections():
    global connection_left
    global c_left_offset
    global c_left_tileimages_0
    global c_left_surface
    global connection_right
    global c_right_offset
    global c_right_tileimages_0
    global connection_up
    global c_up_offset
    global c_up_tileimages_0
    global connection_down
    global c_down_offset
    global c_down_tileimages_0
    if 'connection_left' in map.properties:
        connection_left = load_pygame(map_dir + map.properties['connection_left'])
        global c_left_tileimages_0
        c_left_tileimages_0 = []
        c_left_offset = 0
        if 'c_left_offset' in map.properties:
            c_left_offset = int(map.properties['c_left_offset'])
        for y in range(connection_left.height):
            for x in range(connection_left.width):
                image = connection_left.get_tile_image(x, y, 1)
                c_left_tileimages_0.append((x, y, image))
                #c_left_tileimages_0.append((x - connection_left.width, y - (c_left_offset), image))
        c_left_surface = pygame.Surface((connection_left.width * block_size,connection_left.height * block_size))
        for x,y,image in c_left_tileimages_0:
            c_left_surface.blit(image, (x * block_size, y * block_size))
    if 'connection_right' in map.properties:
        connection_right = load_pygame(map_dir + map.properties['connection_right'])
        global c_right_tileimages_0
        c_right_tileimages_0 = []
        c_right_offset = 0
        if 'c_right_offset' in map.properties:
            c_right_offset = map.properties['c_right_offset']
        for y in range(connection_right.height):
            for x in range(connection_right.width):
                image = map.get_tile_image(x, y, 1)
                c_right_tileimages_0.append((x - connection_right.width, y - (c_right_offset*block_size), image))


def draw_connection(dir):
    if dir == DIR_LEFT:
        if 'connection_left' in map.properties:
            gameDisplay.blit(c_left_surface, ((-connection_left.width * block_size)-cam.x,(c_left_offset * block_size)-cam.y))

    elif dir == DIR_RIGHT:
        if 'connection_right' in map.properties:
            for x, y, image in c_right_tileimages_0:
                if (x * block_size) - cam.x >= -block_size and (x * block_size) - cam.x < cam.width and (
                            y * block_size) - cam.y >= -block_size and (y * block_size) - cam.y < cam.height:
                    gameDisplay.blit(image.convert_alpha(), ((x * block_size) - cam.x, (y * block_size) - cam.y))


def load_map_border():
    global tile_border_img
    global map_base
    if 'tile_border' in map.properties:
        tile_border_img = pygame.image.load(map.properties['tile_border'])
        map_base = pygame.Surface((64 * (map.width + 8),64 * (map.height + 8)))
        x = -64 * 6
        y = -64 * 6
        while x < 64 * (map.width + 6):
            y = -64 * 6
            while y < 64 * (map.height + 6):
                map_base.blit(tile_border_img, (x - cam.x, y - cam.y))
                y += 64
            x += 64

    else:
        tile_border_img = pygame.load('blackborder.png')


def draw_all():
    if cam.center_on_player:
        cam.realign()
    cam.draw()
    global tileimages_0
    for x, y, image in tileimages_0:
        if (x * block_size) - cam.x >= -block_size and (x * block_size) - cam.x < cam.width and (
                y * block_size) - cam.y >= -block_size and (y * block_size) - cam.y < cam.height:
            gameDisplay.blit(image.convert_alpha(), ((x * block_size) - cam.x, (y * block_size) - cam.y))
    for tile in animated_tiles_0:
        tile.draw()
    draw_connection(DIR_LEFT)
    draw_connection(DIR_RIGHT)
    draw_connection(DIR_UP)
    draw_connection(DIR_DOWN)
    for obj in obj_list:
        obj.draw()
    player.draw()
    for element in ui_elements:
        element.draw()
    winDisplay.blit(pygame.transform.scale(gameDisplay,(display_width * resolution_factor, display_height * resolution_factor),winDisplay),(0,0))
    pygame.display.update([0,0,display_width * resolution_factor,display_height * resolution_factor])


print('Open game window...')
gameDisplay = pygame.Surface((display_width, display_height))
winDisplay = pygame.display.set_mode((display_width * resolution_factor, display_height * resolution_factor))
pygame.display.update()
pygame.display.set_caption(game_title)
loop = asyncio.get_event_loop()
inEvent = False
cam = Camera()
obj_list = []
ui_elements = []
load_map('test')
player = Player()
gameData = GameData()
save = SaveData()
# pygame.display.set_icon(game_icon)
print('Initializing game components...')
init_all()
exit_game = False
if __name__ == '__main__':
    print('Entering main loop...')
    main()
pygame.quit()
quit()
