import pygame
from threading import Thread
import time
import __main__
from __main__ import *
import asyncio
import csv
from pytmx.util_pygame import load_pygame

red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
yellow = (255, 255, 0)
white = (255, 255, 255)
black = (0, 0, 0)

pygame.font.init()
font_size = 16
font = pygame.font.Font('font.ttf',font_size)

mv_pattern_stationary = 0
mv_pattern_look = 1
mv_pattern_walk = 2
mv_pattern_look_clockw = 3
mv_pattern_look_cclockw = 4
mv_pattern_walk_ln_h = 5
mv_pattern_walk_ln_v = 6
mv_pattern_player = 7


class TextBox:
    def __init__(self):
        self.ln_1 = ''
        self.ln_2 = ''
        self.ln_3 = ''
        self.image = pygame.image.load('textboxback.png')
        self.lines = 1
        self.text_surface_ln_1 = font.render(self.ln_1,False,black,self.image)
        self.text_surface_ln_2 = font.render(self.ln_2,False,black,self.image)
        self.text_surface_ln_3 = font.render(self.ln_3,False,black,self.image)

    def draw(self):
        __main__.gameDisplay.blit(self.image,(0,__main__.display_height - 112))
        __main__.gameDisplay.blit(self.text_surface_ln_1, (16,__main__.display_height - 96))
        if self.lines > 1:
            __main__.gameDisplay.blit(self.text_surface_ln_2, (16, __main__.display_height - (96 - font_size - 8)))
        if self.lines > 2:
            __main__.gameDisplay.blit(self.text_surface_ln_3, (16, __main__.display_height - (96 - (font_size*2) - 16)))


class Item:
    def __init__(self, name, desc, type, price, scope, effect):
        self.name = name
        self.desc = desc
        self.type = type
        self.price = price
        self.can_use = scope
        self.effect = effect


class MonSpecies:
    def __init__(self, name, base_stats, learnset = {},evolutions = [],gender_ratio = "GENDERLESS", catchrate = 45):
        self.name = name
        self.base_stat = base_stats
        self.learnset = learnset
        self.evolution = evolutions
        self.gender_ratio = gender_ratio
        self.catch_rate = catchrate


class Mon:
    def __init__(self, species, level):
        self.species = species
        self.nickname = self.species.name
        self.iv = self.generate_ivs()
        self.ev = {"hp":0,"atk":0,"def":0,"spa":0,"spd":0,"spe":0}
        self.level = level
        self.stat = self.calculate_stats()
        self.gender = self.generate_gender()
        self.item = project.item_list['?']

    def generate_ivs(self):
        ivs = {"hp":0,"atk":0,"def":0,"spa":0,"spd":0,"spe":0}
        ivs['hp'] = random.randrange(0,15)
        ivs['atk'] = random.randrange(0,15)
        ivs['def'] = random.randrange(0, 15)
        ivs['spa'] = random.randrange(0, 15)
        ivs['spd'] = random.randrange(0, 15)
        ivs['spe'] = random.randrange(0, 15)
        return ivs

    def generate_gender(self):
        gender = ""
        if self.species.gender_ratio != "GENDERLESS":
            s = self.species.gender_ratio.replace("MALE_","")
            ss = s.replace("%","")
            p = int(ss)
            del s
            g = random.randrange(0,100)
            if g < p:
                gender = "male"
            elif g >= p:
                gender = "female"
        else:
            gender = "?"
        return gender

    def calculate_stats(self):
        stats = {'hp':0,'atk':0,'def':0,'spa':0,'spd':0,'spe':0}
        hp_stat = math.floor((((self.species.base_stat['hp']+self.iv['hp'])*2+math.floor(math.ceil(math.sqrt(self.ev['hp']))/4))*self.level)/100) + self.level + 10
        stats['hp'] = hp_stat
        for key in stats.keys():
            if key == 'hp':
                continue
            calc_stat = math.floor((((self.species.base_stat[key]+self.iv[key])*2+math.floor(math.ceil(math.sqrt(self.ev[key]))/4))*self.level)/100) + 5
            stats[key] = calc_stat
        return stats

    def recalculate_stats(self):
        self.stat = {'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0}
        hp_stat = math.floor((((self.species.base_stat['hp'] + self.iv['hp']) * 2 + math.floor(
            math.ceil(math.sqrt(self.ev['hp'])) / 4)) * self.level) / 100) + self.level + 10
        self.stat['hp'] = hp_stat
        for key in self.stat.keys():
            if key == 'hp':
                continue
            calc_stat = math.floor((((self.species.base_stat[key] + self.iv[key]) * 2 + math.floor(
                math.ceil(math.sqrt(self.ev[key])) / 4)) * self.level) / 100) + 5
            self.stat[key] = calc_stat



class PlayerData:
    class Bag:
        def __init__(self):
            self.contents = []
        def add_item(self,item):
            self.contents.append(item)
        def remove_item(self,item):
            for itm in self.contents:
                if item == itm:
                    self.contents.remove(itm)
        def count_item(self,item):
            n = 0
            for itm in self.contents:
                if item.name == itm.name:
                    n += 1
            return n
    def __init__(self):
        self.name = 'PLAYER'
        self.rival_name = 'RIVAL'
        self.money = 0
        self.isGirl = False
        self.numOfBadges = 0
        self.badges = [False,False,False,False,False,False,False,False]
        self.party = []
        self.party.append(Mon(project.species_list[3], 5))
        self.bag = self.Bag()





import project





@asyncio.coroutine
def play_sound(sound):
    sound.play()
    while sound.get_num_channels() > 0:
        yield from asyncio.sleep(0.1)

@asyncio.coroutine
def show_text(text):
    text_box = TextBox()
    __main__.ui_elements.append(text_box)
    global command
    command = False
    global texts
    texts = []
    global skip
    skip = 0
    text = str.replace(text,'{NAME}','%P')
    text = str.replace(text,'{PLAYER}','%P')
    text = str.replace(text,'{RIVAL}','%R')
    for x in range(len(__main__.gameData.vars)):
        text = str.replace(text,'%V' + str(x),str(__main__.gameData.vars[x]))
    for x in range(len(__main__.gameData.flags)):
        text = str.replace(text,'%F' + str(x),str(__main__.gameData.flags[x]))
    texts = text.split('%p')
    global t_index
    t_index = 0
    for text in texts:
        for chars in text:
            if skip > 0:
                skip -= 1
                continue
            if command:
                if chars == '%':
                    if text_box.lines == 1:
                        text_box.ln_1 = text_box.ln_1 + chars
                        text_box.text_surface_ln_1 = font.render(text_box.ln_1, False, black, text_box.image)
                    elif text_box.lines == 2:
                        text_box.ln_2 = text_box.ln_2 + chars
                        text_box.text_surface_ln_2 = font.render(text_box.ln_2, False, black, text_box.image)
                    elif text_box.lines == 3:
                        text_box.ln_3 = text_box.ln_3 + chars
                        text_box.text_surface_ln_3 = font.render(text_box.ln_2, False, black, text_box.image)
                    __main__.draw_all()
                    yield from asyncio.sleep(0.02)
                elif chars == 'P':
                    for chrs in __main__.player.data.name:
                        if text_box.lines == 1:
                            text_box.ln_1 = text_box.ln_1 + chrs
                            text_box.text_surface_ln_1 = font.render(text_box.ln_1, False, black, text_box.image)
                        elif text_box.lines == 2:
                            text_box.ln_2 = text_box.ln_2 + chrs
                            text_box.text_surface_ln_2 = font.render(text_box.ln_2, False, black, text_box.image)
                        elif text_box.lines == 3:
                            text_box.ln_3 = text_box.ln_3 + chrs
                            text_box.text_surface_ln_3 = font.render(text_box.ln_3, False, black, text_box.image)
                        __main__.draw_all()
                        yield from asyncio.sleep(0.02)
                elif chars == 'R':
                    for chrs in __main__.player.data.rival_name:
                        if text_box.lines == 1:
                            text_box.ln_1 = text_box.ln_1 + chrs
                            text_box.text_surface_ln_1 = font.render(text_box.ln_1, False, black, text_box.image)
                        elif text_box.lines == 2:
                            text_box.ln_2 = text_box.ln_2 + chrs
                            text_box.text_surface_ln_2 = font.render(text_box.ln_2, False, black, text_box.image)
                        elif text_box.lines == 3:
                            text_box.ln_3 = text_box.ln_3 + chrs
                            text_box.text_surface_ln_3 = font.render(text_box.ln_3, False, black, text_box.image)
                        __main__.draw_all()
                        yield from asyncio.sleep(0.02)
                elif chars == 'S':
                    beginscript = text.index('[',t_index)
                    endscript = text.index(']',t_index)
                    script = text[beginscript + 1:endscript - 1]
                    exec(script)
                    t_index += endscript - beginscript
                    skip += endscript - beginscript
                elif chars == 'm':
                    t_index += 1
                    skip += 1
                    n1 = int(text[t_index:t_index + 1])
                    t_index += 1
                    skip += 1
                    n2 = int(text[t_index:t_index + 1])
                    num = (n1 * 10 + n2)
                    __main__.music.pause()
                    __main__.loop.run_until_complete(play_sound(project.me_list[num]))
                    __main__.music.unpause()
                elif chars == 'y':
                    begins = text.index('(', t_index)
                    ends = text.index(')', t_index)
                    num = int(text[begins + 1:ends - 1])
                    t_index += ends - begins
                    skip += ends - begins
                    yield from asyncio.sleep(0.01 * num)
                elif chars == 'q':
                    pass
                elif chars == 's':
                    t_index += 1
                    skip += 1
                    n1 = int(text[t_index:t_index + 1])
                    t_index += 1
                    skip += 1
                    n2 = int(text[t_index:t_index + 1])
                    num = (n1 * 10 + n2)
                    __main__.music.pause()
                    __main__.loop.run_until_complete(play_sound(project.se_list[num]))
                    __main__.music.unpause()
                elif chars == 'n':
                    text_box.lines += 1
                elif chars == 'e':
                    if text_box.lines == 1:
                        text_box.ln_1 = text_box.ln_1 + 'é'
                        text_box.text_surface_ln_1 = font.render(text_box.ln_1, False, black, text_box.image)
                    elif text_box.lines == 2:
                        text_box.ln_2 = text_box.ln_2 + 'é'
                        text_box.text_surface_ln_2 = font.render(text_box.ln_2, False, black, text_box.image)
                    elif text_box.lines == 3:
                        text_box.ln_3 = text_box.ln_3 + 'é'
                        text_box.text_surface_ln_3 = font.render(text_box.ln_3, False, black, text_box.image)
                    __main__.draw_all()
                    yield from asyncio.sleep(0.02)
                command = False
                t_index += 1
                continue
            if chars != '%':
                if text_box.lines == 1:
                    text_box.ln_1 = text_box.ln_1 + chars
                    text_box.text_surface_ln_1 = font.render(text_box.ln_1, False, black, text_box.image)
                    __main__.draw_all()
                    if chars != ' ':
                        yield from asyncio.sleep(0.02)
                elif text_box.lines == 2:
                    text_box.ln_2 = text_box.ln_2 + chars
                    text_box.text_surface_ln_2 = font.render(text_box.ln_2, False, black, text_box.image)
                    __main__.draw_all()
                    if chars != ' ':
                        yield from asyncio.sleep(0.02)
                elif text_box.lines == 3:
                    text_box.ln_3 = text_box.ln_3 + chars
                    text_box.text_surface_ln_3 = font.render(text_box.ln_3, False, black, text_box.image)
                    __main__.draw_all()
                    if chars != ' ':
                        yield from asyncio.sleep(0.02)
                t_index += 1
            else:
                command = True
                t_index += 1
                continue
        pygame.event.clear()
        while True:
            getout = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        getout = True
            if getout == True:
                break
            yield from asyncio.sleep(0.1)
        text_box.ln_3 = ''
        text_box.ln_2 = ''
        text_box.ln_1 = ''
        text_box.lines = 1
        __main__.draw_all()
    __main__.ui_elements.remove(text_box)
    del text_box


def get_prompt(text,type):
    pass


@asyncio.coroutine
def receive_item(item):
    pocket = item.type + "S POCKET"
    __main__.player.data.bag.add_item(item)
    __main__.loop.run_until_complete(show_text(project.str_list['receive_item'].format(item.name)))
    __main__.loop.run_until_complete(show_text(project.str_list['item_in_bag'].format(item.name,pocket)))
