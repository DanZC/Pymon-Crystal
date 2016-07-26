from const import *
import pygame
from threading import Thread
import time
import __main__
from __main__ import loop
import math
import random
import pickle
import asyncio
import csv
from pytmx.util_pygame import load_pygame

pygame.font.init()
font_size = 16
font = pygame.font.Font('UI/font.ttf', font_size)
font_right = pygame.font.Font('UI/font.ttf', font_size)


class AnimatedSprite:
    def __init__(self,pos,frames,speed):
        self.x = pos[0]
        self.y = pos[1]
        self.frames = frames
        self.framenum = 0
        if speed > 0:
            self.speed = speed
        else:
            self.speed = 1.0
        self.wait = self.frames // self.speed

    def update(self):
        if self.wait == 0:
            if self.framenum >= len(self.frames):
                self.framenum = 0
            else:
                self.framenum += 1
            self.wait = self.speed * self.frames
        self.wait -= 1

    def draw(self):
        gd = __main__.gameDisplay
        gd.blit(self.frames[self.framenum],(self.x,self.y))


class Text:
    def __init__(self,text,pos,color = black,align = ALIGN_LEFT):
        self.text = text
        self.pos = pos
        self.align = align
        self.color = color

    def move(self, pos):
        self.pos = pos

    def update(self,text):
        self.text = text

    def draw(self):
        surf = font.render(self.text,False,black)
        rect = surf.get_rect(x=0,y=0)
        if self.align == ALIGN_RIGHT:
            rect.right = self.pos[0]
        rect.move_ip(self.pos[0]+rect.width,self.pos[1])
        gd = __main__.gameDisplay
        gd.blit(surf,rect)


class TextBox:
    def __init__(self):
        self.type = 'text_box'
        self.ln_1 = ''
        self.ln_2 = ''
        self.ln_3 = ''
        self.image = pygame.image.load(__main__.ui_dir + 'textboxback.png')
        self.lines = 1
        self.text_surface_ln_1 = font.render(self.ln_1, False, black, self.image)
        self.text_surface_ln_2 = font.render(self.ln_2, False, black, self.image)
        self.text_surface_ln_3 = font.render(self.ln_3, False, black, self.image)

    def draw(self):
        gd = __main__.gameDisplay
        gd.blit(self.image, (0, __main__.display_height - 96))
        if self.lines < 3:
            gd.blit(self.text_surface_ln_1, (18, __main__.display_height - 64))
            if self.lines >= 2:
                gd.blit(self.text_surface_ln_2, (18, __main__.display_height - 32))
        elif self.lines >= 3:
            gd.blit(self.text_surface_ln_2, (18, __main__.display_height - 64))
            gd.blit(self.text_surface_ln_3, (18, __main__.display_height - 32))


class YesNoBox:
    def __init__(self, default=0):
        self.type = 'yesno_box'
        self.bg = pygame.image.load(__main__.ui_dir + 'yesnoboxbg.png')
        self.select = default
        self.selector = pygame.image.load(__main__.ui_dir + 'selector.png')
        self.exit = False

    def move_select(self):
        if self.select == 0:
            self.select = 1
        else:
            self.select = 0

    def select_option(self):
        self.exit = True

    def draw(self):
        gd = __main__.gameDisplay
        gd.blit(self.bg, (224, 112))
        gd.blit(self.selector, (242, 128 + (32 * self.select)))


class MenuBox:
    def __init__(self):
        self.type = 'menu_box'
        self.options = []
        plyr = __main__.player
        if plyr.data.hasDex:
            self.options.append("POK{e}DEX")
        if len(plyr.data.party) > 0:
            self.options.append("POK{e}MON")
        self.options.append("BAG")
        if plyr.data.hasGear:
            self.options.append("{poke}GEAR")
        self.options.append(plyr.data.name)
        self.options.append("SAVE")
        self.options.append("DEBUG")
        self.options.append("EXIT")
        self.topimg = pygame.image.load(__main__.ui_dir + 'menu_top.png')
        self.midimg = pygame.image.load(__main__.ui_dir + 'menu_mid.png')
        self.bottomimg = pygame.image.load(__main__.ui_dir + 'menu_bottom.png')
        self.select = 0
        self.selector = pygame.image.load(__main__.ui_dir + 'selector.png')

    def move_select(self, amount):
        if amount > 0:
            if self.select + amount >= len(self.options):
                self.select = 0
            else:
                self.select += amount
        elif amount < 0:
            if self.select + amount < 0:
                self.select = len(self.options) - 1
            else:
                self.select += amount

    def select_option(self):
        if self.options[self.select] == "SAVE":
            print("save selected")
            show_text(project.str_list['save_prompt_0'], True)
            result = yes_no_box(True)
            if result:
                clear_ui('text_box')
                show_text(project.str_list['save_prompt_1'], True)
                if __main__.save.export_("save.bin") == 1:
                    show_text(project.str_list['save_prompt_2'])
                else:
                    show_text(project.str_list['save_error'])
            else:
                clear_ui('text_box')
        elif self.options[self.select] == "DEBUG":
            import debug
            debug.call_debug_screen()
        elif self.options[self.select] == "POK{e}MON":
            print("pokemon selected")
        elif self.options[self.select] == "{poke}GEAR":
            call_pokegear_screen()
        elif self.options[self.select] == "BAG":
            call_bag_screen()

    def draw(self):
        gd = __main__.gameDisplay
        gd.blit(self.topimg, (160, 0))
        y = 1
        n = len(self.options)
        for option in self.options:
            if y == n:
                gd.blit(self.bottomimg, (160, y * 32))
            else:
                gd.blit(self.midimg, (160, y * 32))
            option = reformat_text(option)
            text = font.render(option, False, black)
            gd.blit(text, (192, y * 32))
            y += 1
        gd.blit(self.selector, (178, ((self.select + 1) * 32) + 4))


class BagScreen:
    def __init__(self, bag):
        self.type = 'bag_screen'
        self.pockets = {"ITEMS": [], "KEY ITEMS": [], "BALLS": [], "TMHM": []}
        for item in bag.contents:
            if item.type == "KEY ITEM":
                if item not in self.pockets['KEY ITEMS']:
                    self.pockets['KEY ITEMS'].append(item)
            elif item.type == "ITEM":
                if item not in self.pockets['ITEMS']:
                    self.pockets['ITEMS'].append(item)
            elif item.type == "BALL":
                if item not in self.pockets['BALLS']:
                    self.pockets['BALLS'].append(item)
        self.current_pocket = self.pockets['ITEMS']
        self.pocket_num = 0
        self.pocket_nums = {"0": "ITEMS", "1": "KEY ITEMS", "2": "BALLS", "3": "TMHM"}
        self.bg = pygame.image.load(__main__.ui_dir + 'bagbg1.png')
        self.select = 0
        self.selector_img = pygame.image.load(__main__.ui_dir + 'bagselector.png')
        self.bag_img_items = pygame.image.load(__main__.ui_dir + 'bagicn_0.png')
        self.bag_img_key = pygame.image.load(__main__.ui_dir + 'bagicn_2.png')
        self.bag_img_ball = pygame.image.load(__main__.ui_dir + 'bagicn_1.png')
        self.bag_img_tmhm = pygame.image.load(__main__.ui_dir + 'bagicn_3.png')
        self.bag_txt_items = pygame.image.load(__main__.ui_dir + 'baglbl_0.png')
        self.bag_txt_key = pygame.image.load(__main__.ui_dir + 'baglbl_2.png')
        self.bag_txt_ball = pygame.image.load(__main__.ui_dir + 'baglbl_1.png')
        self.bag_txt_tmhm = pygame.image.load(__main__.ui_dir + 'baglbl_3.png')
        self.bag = bag
        self.scroll = 0

    def select_option(self):
        print("selected", self.current_pocket[self.select].name)

    def change_pocket(self, amount):
        if amount > 1:
            amount = 1
        if amount < -1:
            amount = -1
        self.pocket_num += amount
        if self.pocket_num < 0:
            self.pocket_num = len(self.pockets) - 1
        if self.pocket_num > len(self.pockets) - 1:
            self.pocket_num = 0
        self.current_pocket = self.pockets[self.pocket_nums[str(self.pocket_num)]]
        self.select = 0
        self.scroll = 0

    def move_select(self, amount):
        if amount > 0:
            if self.select + amount > len(self.current_pocket):
                self.select = 0
                self.scroll = 0
            else:
                self.select += amount
                if self.select >= (self.scroll + 5):
                    self.scroll += 1
        elif amount < 0:
            if self.select + amount < 0:
                self.select = len(self.current_pocket)
                if self.select < 4:
                    self.scroll = 0
                else:
                    self.scroll = self.select - 4
            else:
                self.select += amount
                if self.select < self.scroll:
                    self.scroll -= 1

    def draw(self):
        gd = __main__.gameDisplay
        gd.blit(self.bg, (0, 0))
        gd.blit(self.selector_img, (96, 36 + (self.select * 32) - (self.scroll * 32)))
        if self.pocket_nums[str(self.pocket_num)] == "ITEMS":
            gd.blit(self.bag_img_items, (0, 44))
            gd.blit(self.bag_txt_items, (0, 154))
        elif self.pocket_nums[str(self.pocket_num)] == "KEY ITEMS":
            gd.blit(self.bag_img_key, (0, 44))
            gd.blit(self.bag_txt_key, (0, 154))
        elif self.pocket_nums[str(self.pocket_num)] == "BALLS":
            gd.blit(self.bag_img_ball, (0, 44))
            gd.blit(self.bag_txt_ball, (0, 154))
        elif self.pocket_nums[str(self.pocket_num)] == "TMHM":
            gd.blit(self.bag_img_tmhm, (0, 44))
            gd.blit(self.bag_txt_tmhm, (0, 154))
        n = 0
        for item in self.current_pocket:
            if self.scroll <= n and self.scroll + 5 > n:
                text = font.render(item.name, False, black)
                gd.blit(text, (110, 32 + (32 * n) - (32 * self.scroll)))
                if not item.type == "KEY ITEM":
                    text_amount = font.render("*" + str(self.bag.count_item(item.name)), False, black)
                    gd.blit(text_amount, (256, 48 + (32 * n) - (32 * self.scroll)))
                n += 1
            else:
                n += 1
        if self.scroll <= n and self.scroll + 5 > n:
            cancel_text = font.render("CANCEL", False, black)
            gd.blit(cancel_text, (110, 32 + (32 * n) - (32 * self.scroll)))
        if len(self.current_pocket) > 0:
            if self.select < len(self.current_pocket):
                item = self.current_pocket[self.select]
                desc_raw = item.desc
                desc_f = reformat_text(desc_raw)
                desc_ln = desc_f.split('%n')
                text_lns = []
                for desc_l in desc_ln:
                    text_ln = font.render(desc_l, False, white)
                    text_lns.append(text_ln)
                n = 0
                for text in text_lns:
                    gd.blit(text, (8, 220 + 32 * n))


class GearScreen:
    def __init__(self):
        self.type = "pokegear_screen"
        self.bg = pygame.image.load(__main__.ui_dir + 'pokegear_bg.png')
        self.btn_back = pygame.image.load(__main__.ui_dir + "pokegearbtn_back.png")
        self.btn_map = pygame.image.load(__main__.ui_dir + "pokegearbtn_map.png")
        self.btn_phone = pygame.image.load(__main__.ui_dir + "pokegearbtn_phone.png")
        self.selector = pygame.image.load(__main__.ui_dir + 'pokegear_selector.png')
        self.buttons = []
        self.buttons.append("BACK")
        if __main__.player.data.gearMapCard:
            self.buttons.append("MAP")
        self.buttons.append("PHONE")
        if __main__.player.data.gearRadioCard:
            self.buttons.append("RADIO")
        self.select = 0
        self.scene = None

    def move_select(self, amount):
        if amount > 1:
            amount = 1
        if amount < -1:
            amount = -1
        if amount > 0:
            if self.select + amount >= 3:
                if __main__.player.data.gearRadioCard:
                    self.select = 3
                else:
                    self.select = 2
            elif self.select + amount == 1:
                if __main__.player.data.gearMapCard:
                    self.select = 1
                else:
                    self.select = 2
            elif self.select == 3:
                pass
            else:
                self.select += amount
        if amount < 0:
            if self.select + amount < 0:
                self.select = 0
            elif self.select + amount == 1:
                if __main__.player.data.gearMapCard:
                    self.select = 1
                else:
                    self.select = 0
            elif self.select + amount == 3:
                if __main__.player.data.gearRadioCard:
                    self.select = 3
                else:
                    self.select = 2
            else:
                self.select = 0
        if self.select == 0:
            if self.scene is not None:
                del self.scene
                self.scene = None
        elif self.select == 1:
            if self.scene is not None:
                del self.scene
            self.scene = MapScreen()
        elif self.select == 2:
            if self.scene is not None:
                del self.scene
                self.scene = None
        elif self.select == 3:
            if self.scene is not None:
                del self.scene
                self.scene = None

    def draw(self):
        gd = __main__.gameDisplay
        gd.blit(self.bg, (0, 0))
        text = __main__.systime.get_weekday()
        weekday_text = font.render(text, False, black)
        gd.blit(weekday_text, (96, 96))
        text = __main__.systime.get_date()
        m_text = font.render(text, False, white)
        gd.blit(m_text, (96, 48))
        if __main__.systime.get_hour() >= 12:
            if __main__.systime.get_hour() == 12:
                text = str(__main__.systime.get_hour()) + ":" + '{:02}'.format(__main__.systime.get_minute()) + " PM"
            else:
                text = str(__main__.systime.get_hour() - 12) + ":" + '{:02}'.format(__main__.systime.get_minute()) + " PM"
        else:
            if __main__.systime.get_hour() == 0 or __main__.systime.get_hour() == 24:
                text = "12:" + '{:02}'.format(__main__.systime.get_minute()) + " AM"
            else:
                text = str(__main__.systime.get_hour()) + ":" + '{:02}'.format(__main__.systime.get_minute()) + " AM"
        time_text = font.render(text, False, black)
        gd.blit(time_text, (96, 128))
        text = "Please select an%noption."
        texts = text.split("%n")
        offset = 0
        for text in texts:
            m_text = font.render(text, False, black)
            gd.blit(m_text, (18, __main__.display_height - (64 - 32 * offset)))
            offset += 1
        if self.scene is not None:
            self.scene.draw()
        gd.blit(self.btn_back, (0, 0))
        if __main__.player.data.gearMapCard:
            gd.blit(self.btn_map, (32, 0))
        gd.blit(self.btn_phone, (64, 0))
        gd.blit(self.selector, (32 * self.select, 0))

class MapObject:
    def __init__(self, x, y, width, height, name, type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.type = type


class MapScreen:
    def __init__(self):
        self.type = 'map_screen'
        self.bg = pygame.image.load(__main__.ui_dir + 'pokegear_bg_map.png')
        self.loc_select = (__main__.map.region_x, __main__.map.region_y)
        self.map_selector = pygame.image.load(__main__.ui_dir + "map_select.png")
        self.map_selector = pygame.transform.scale(self.map_selector, (16, 16))
        map_data = load_pygame(__main__.map_dir + "map_" + str(__main__.map.region) + ".tmx")
        self.map_objects = []
        for obj in map_data.objects:
            mobj = MapObject(obj.x, obj.y, obj.width, obj.height, obj.name, obj.type)
            self.map_objects.append(mobj)
        self.map_objects.reverse()
        self.map_img = pygame.Surface((map_data.width * 32, map_data.height * 32))
        for x in range(map_data.width):
            for y in range(map_data.height):
                self.map_img.blit(map_data.get_tile_image(x, y, 0), (x * 32, y * 32))
        self.map_img = pygame.transform.scale(self.map_img, (map_data.width * 16, map_data.height * 16))
        self.width = map_data.width
        self.height = map_data.height
        del map_data

    def move_select(self, direction):
        if direction == __main__.DIR_UP:
            if self.loc_select[1] > 0:
                self.loc_select = (self.loc_select[0], self.loc_select[1] - 1)
        elif direction == __main__.DIR_DOWN:
            if self.loc_select[1] < self.height - 1:
                self.loc_select = (self.loc_select[0], self.loc_select[1] + 1)
        elif direction == __main__.DIR_LEFT:
            if self.loc_select[0] > 0:
                self.loc_select = (self.loc_select[0] - 1, self.loc_select[1])
        elif direction == __main__.DIR_RIGHT:
            if self.loc_select[0] < self.width - 1:
                self.loc_select = (self.loc_select[0] + 1, self.loc_select[1])

    def draw(self):
        gd = __main__.gameDisplay
        gd.blit(self.bg, (0, 0))
        origin_x = 16
        origin_y = 48
        gd.blit(self.map_img, (origin_x, origin_y))
        for obj in self.map_objects:
            if math.floor(obj.x // 32) <= self.loc_select[0] and (
                math.floor(obj.y // 32) <= self.loc_select[1]) and (
                math.floor(obj.x // 32) + math.floor(obj.width // 32) > self.loc_select[0]) and (
                math.floor(obj.y // 32) + math.floor(obj.height // 32) > self.loc_select[1]
            ):
                name_text = font.render(obj.name, False, black)
                gd.blit(name_text, (143, 0))
                if obj.type == "place":
                    break
        gd.blit(self.map_selector, ((self.loc_select[0] * 16) + origin_x, (self.loc_select[1] * 16) + origin_y))


class NameEntryScreen:
    def __init__(self):
        self.type = 'name_entry'
        self.bg = pygame.image.load(__main__.ui_dir + 'namebg.png')
        self.name_string = ""
        self.select = (0, 0)
        self.selector = pygame.image.load(__main__.ui_dir + 'letterselector.png')
        self.name_blank = pygame.image.load(__main__.ui_dir + 'name_blank.png')
        self.name_current = pygame.image.load(__main__.ui_dir + 'name_current.png')
        self.pos = 0
        self.complete = False

    def select_option(self):
        if self.select[0] == 0:
            if self.select[1] == 0:
                self.input("A")
            elif self.select[1] == 1:
                self.input("J")
            elif self.select[1] == 2:
                self.input("S")
            elif self.select[1] == 3:
                self.input("-")
        elif self.select[0] == 1:
            if self.select[1] == 0:
                self.input("B")
            elif self.select[1] == 1:
                self.input("K")
            elif self.select[1] == 2:
                self.input("T")
            elif self.select[1] == 3:
                self.input("?")
            elif self.select[1] == 4:
                self.backspace()
        elif self.select[0] == 2:
            if self.select[1] == 0:
                self.input("C")
            elif self.select[1] == 1:
                self.input("L")
            elif self.select[1] == 2:
                self.input("U")
            elif self.select[1] == 3:
                self.input("!")
            elif self.select[1] == 4:
                self.complete = True
        elif self.select[0] == 3:
            if self.select[1] == 0:
                self.input("D")
            elif self.select[1] == 1:
                self.input("M")
            elif self.select[1] == 2:
                self.input("V")
            elif self.select[1] == 3:
                self.input("/")
        elif self.select[0] == 4:
            if self.select[1] == 0:
                self.input("E")
            elif self.select[1] == 1:
                self.input("N")
            elif self.select[1] == 2:
                self.input("W")
            elif self.select[1] == 3:
                self.input(",")
        elif self.select[0] == 5:
            if self.select[1] == 0:
                self.input("F")
            elif self.select[1] == 1:
                self.input("O")
            elif self.select[1] == 2:
                self.input("X")
            elif self.select[1] == 3:
                self.input(".")
        elif self.select[0] == 6:
            if self.select[1] == 0:
                self.input("G")
            elif self.select[1] == 1:
                self.input("P")
            elif self.select[1] == 2:
                self.input("Y")
            elif self.select[1] == 3:
                self.input(" ")
        elif self.select[0] == 7:
            if self.select[1] == 0:
                self.input("H")
            elif self.select[1] == 1:
                self.input("Q")
            elif self.select[1] == 2:
                self.input("Z")
            elif self.select[1] == 3:
                self.input(" ")
        elif self.select[0] == 8:
            if self.select[1] == 0:
                self.input("I")
            elif self.select[1] == 1:
                self.input("R")
            elif self.select[1] == 2:
                self.input(" ")
            elif self.select[1] == 3:
                self.input(" ")

    def move_select(self, direction):
        if direction == __main__.DIR_DOWN:
            if self.select[1] < 3:
                self.select = (self.select[0], self.select[1] + 1)
            elif self.select[1] < 4:
                self.select = (self.select[0] // 3, 4)
            else:
                self.select = (self.select[0], 0)
        elif direction == __main__.DIR_UP:
            if self.select[1] > 0:
                self.select = (self.select[0], self.select[1] - 1)
            else:
                self.select = (self.select[0] // 3, 4)
        elif direction == __main__.DIR_LEFT:
            if self.select[1] < 4:
                if self.select[0] > 0:
                    self.select = (self.select[0] - 1, self.select[1])
                else:
                    self.select = (8, self.select[1])
            else:
                if self.select[0] > 0:
                    self.select = (self.select[0] - 1, self.select[1])
                else:
                    self.select = (2, self.select[1])
        elif direction == __main__.DIR_RIGHT:
            if self.select[1] < 4:
                if self.select[0] < 8:
                    self.select = (self.select[0] + 1, self.select[1])
                else:
                    self.select = (0, self.select[1])
            else:
                if self.select[0] < 2:
                    self.select = (self.select[0] + 1, self.select[1])
                else:
                    self.select = (0, self.select[1])

    def input(self, char):
        if len(self.name_string) < 8:
            self.name_string += char

    def backspace(self):
        print('backspace')
        if len(self.name_string) > 0:
            string = ""
            n = 0
            for char in self.name_string:
                if n + 1 < len(self.name_string):
                    string += char
                    n += 1
                    continue
                break
            self.name_string = string

    def draw(self):
        gd = __main__.gameDisplay
        gd.blit(self.bg, (0, 0))
        gd.blit(__main__.player.spr_down, (32, 24))
        n = 0
        if len(self.name_string) > 0:
            for char in self.name_string:
                name_surface = font.render(char, False, black)
                gd.blit(name_surface, (80 + n, 96))
                n += 16
        if n < (16 * 8):
            gd.blit(self.name_current, (81 + n, 96))
            n += 16
        while n < (16 * 8):
            gd.blit(self.name_blank, (81 + n, 96))
            n += 16
        gd.blit(self.selector, (31 + (32 * self.select[0]), 127 + (32 * self.select[1])))


class Item:
    def __init__(self, name, desc, type, price, scope, effect):
        self.name = name
        self.desc = desc
        self.type = type
        self.price = price
        self.can_use = scope
        self.effect = effect


class MonSpecies:
    def __init__(self, species_id, name, base_stats, type=list("???"), learnset={}, evolutions=[], gender_ratio="GENDERLESS",
                 catchrate=45):
        self.id = species_id
        self.name = name
        self.base_stat = base_stats
        self.type = type
        self.learnset = LearnSet(learnset)
        self.evolution = evolutions
        self.gender_ratio = gender_ratio
        self.catch_rate = catchrate
        self.image_front = pygame.image.load('Battlers/Mons/' + str(self.id) + '.png')
        self.image_back = pygame.image.load('Battlers/Mons/' + str(self.id) + 'b.png')
        self.image_shiny_front = pygame.image.load('Battlers/Mons/' + str(self.id) + 's.png')
        self.image_shiny_back = pygame.image.load('Battlers/Mons/' + str(self.id) + 'sb.png')


class Mon:
    def __init__(self, species, level, moves = [], shiny=False, is_egg=False, steps=0):
        self.species = species
        self.nickname = self.species.name
        self.shiny = shiny
        self.iv = self.generate_ivs()
        self.ev = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
        self.level = level
        self.is_egg = is_egg
        self.steps = steps
        self.stat = self.calculate_stats()
        self.current_hp = self.stat['hp']
        self.status = "NON"
        self.gender = self.generate_gender()
        self.item = project.item_list['?']
        if moves is []:
            self.moves = self.species.learnset.get_last_four_moves(self.level)
        else:
            self.moves = moves

    def generate_ivs(self):
        ivs = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
        ivs['hp'] = random.randrange(0, 15)
        ivs['atk'] = random.randrange(0, 15)
        ivs['def'] = random.randrange(0, 15)
        ivs['spa'] = random.randrange(0, 15)
        ivs['spd'] = random.randrange(0, 15)
        ivs['spe'] = random.randrange(0, 15)
        return ivs

    def generate_gender(self):
        gender = ""
        if self.species.gender_ratio != "GENDERLESS":
            s = self.species.gender_ratio.replace("MALE_", "")
            ss = s.replace("%", "")
            p = int(ss)
            del s
            del ss
            g = random.randrange(0, 100)
            if g < p:
                gender = "m"
            elif g >= p:
                gender = "f"
        else:
            gender = "?"
        return gender

    def calculate_stats(self):
        stats = {'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0}
        hp_stat = math.floor((((self.species.base_stat['hp'] + self.iv['hp']) * 2 + math.floor(
            math.ceil(math.sqrt(self.ev['hp'])) / 4)) * self.level) / 100) + self.level + 10
        stats['hp'] = hp_stat
        for key in stats.keys():
            if key == 'hp':
                continue
            calc_stat = math.floor((((self.species.base_stat[key] + self.iv[key]) * 2 + math.floor(
                math.ceil(math.sqrt(self.ev[key])) / 4)) * self.level) / 100) + 5
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
    def __init__(self):
        self.name = 'PLAYER'
        self.rival_name = 'RIVAL'
        self.money = 0
        self.isGirl = False
        self.numOfBadges = 0
        self.badges = [False, False, False, False, False, False, False, False]
        self.party = Party()
        self.party.add(Mon(project.species_list[0], 5, moves=['SCRATCH']))
        self.on_bike = False
        self.surfing = False
        self.hasDex = False
        self.hasGear = True
        self.gearMapCard = True
        self.gearJukebox = False
        self.gearRadioCard = False
        self.gearRadioEXPCard = False
        self.back_raw = pygame.image.load('Player/Male/trback000.png')
        self.back = pygame.transform.chop(pygame.transform.chop(self.back_raw, (128, 0, 0, 0)), (128, 128, 640, 640))
        self.bag = Bag()
        self.bag.add_item('POTION')
        self.bag.add_item('MAX POTION', 8)
        self.bag.add_item('ETHER', 2)
        self.bag.add_item('ELIXIR', 6)
        self.bag.add_item('FULL HEAL', 4)
        self.bag.add_item('BICYCLE')


class Party:
    def __init__(self):
        self.mons = []

    def add(self, mon):
        if len(self.mons) < 6:
            self.mons.append(mon)
            return True
        return False

    def get(self, index):
        if index < len(self.mons):
            return self.mons[index]
        else:
            return None

    def get_first(self):
        if 0 < len(self.mons):
            return self.mons[0]
        else:
            return None

    def get_first_able(self):
        for mon in self.mons:
            if mon.is_egg:
                continue
            if mon.current_hp <= 0:
                continue
            return mon
        return None

    def get_first_non_egg(self):
        for mon in self.mons:
            if mon.is_egg:
                continue
            return mon
        return None

    def count_able(self):
        n = 0
        for mon in self.mons:
            if mon.is_egg:
                continue
            if mon.current_hp <= 0:
                continue
            n += 1
        return n

    def count_non_egg(self):
        n = 0
        for mon in self.mons:
            if mon.is_egg:
                continue
            n += 1
        return n

    def __len__(self):
        return len(self.mons)


class PCMenu:
    def __init__(self):
        pass


class PCBoxSystem:
    def __init__(self):
        self.box = []
        for x in range(30):
            self.box = PCBox()


class PCBox:
    def __init__(self):
        self.content = []
        for x in range(30):
            self.content.append(None)

    def get_pokemon(self, column, row):
        spot = (row * 6) + column
        return self.content[spot]


class Bag:
    def __init__(self):
        self.contents = []

    def add_item(self, item, amount=1):
        for n in range(amount):
            self.contents.append(project.item_list[item])

    def remove_item(self, item):
        for itm in self.contents:
            if item.name == itm:
                self.contents.remove(project.item_list[itm])

    def count_item(self, item):
        n = 0
        for itm in self.contents:
            if item == itm.name:
                n += 1
        return n


class Move:
    def __init__(self,move,maxpp,power,accuracy=100,type="???",effect={},secondary={},field_effect="NONE"):
        self.move = move
        self.name = move['name']
        self.type = type
        self.power = power
        self.accuracy = accuracy
        self.maxpp = maxpp
        self.effect = effect
        self.secondary = secondary
        self.field_effect = field_effect
        self.pp = self.maxpp

    def get_category(self):
        return project.type_list[self.type]['category']


class LearnSet:
    def __init__(self,dict):
        self.set = {}
        for x in range(100):
            if str(x) in dict:
                self.set[str(x)] = dict[str(x)]

    def get_all_moves_learned_at(self,level):
        list_at_level = []
        if str(level) in self.set:
            list_at_level = self.set[str(level)]
        return list_at_level

    def get_last_four_moves(self,level):
        x = level
        move_list = []
        for y in range(x-1):
            if str(x-y) in self.set:
                for move in self.set[str(x-y)]:
                    move_list.append(move)
            if len(move_list) >= 4:
                break
        return move_list


import project


def reformat_text(string):
    text = string
    text = str.replace(text, '{NAME}', '%P')
    text = str.replace(text, '{PLAYER}', '%P')
    text = str.replace(text, '{RIVAL}', '%R')
    text = str.replace(text, '{e}', 'é')
    text = str.replace(text, '{poke}', '[]')
    text = str.replace(text, "{pkmn}", "{}")
    text = str.replace(text, "{m}", "<")
    text = str.replace(text, "{f}", ">")
    text = str.replace(text, "'m", "µ")
    text = str.replace(text, "'s", "=")
    text = str.replace(text, "'d", "`")
    for x in range(len(__main__.gameData.vars)):
        text = str.replace(text, '%V' + str(x), str(__main__.gameData.vars[x]))
    for x in range(len(__main__.gameData.flags)):
        text = str.replace(text, '%F' + str(x), str(__main__.gameData.flags[x]))
    return text


@asyncio.coroutine
def play_sound(sound):
    sound.play()
    while sound.get_num_channels() > 0:
        yield from asyncio.sleep(0.1)


@asyncio.coroutine
def show_text_raw(text, keep_open=False):
    text_box = TextBox()
    __main__.ui_elements.append(text_box)
    global command
    command = False
    global texts
    texts = []
    global skip
    skip = 0
    text = reformat_text(text)
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
                    beginscript = text.index('[', t_index)
                    endscript = text.index(']', t_index)
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
        if not keep_open:
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
    if not keep_open:
        __main__.ui_elements.remove(text_box)
        del text_box


def show_text(text, keep_open=False):
    __main__.loop.run_until_complete(show_text_raw(text, keep_open))


def get_prompt(text, type):
    pass


@asyncio.coroutine
def receive_item(item):
    pocket = item.type + "S POCKET"
    __main__.player.data.bag.add_item(item)
    __main__.loop.run_until_complete(show_text(project.str_list['receive_item'].format(item.name)))
    __main__.loop.run_until_complete(show_text(project.str_list['item_in_bag'].format(item.name, pocket)))


def warp(map, x, y):
    print('unload_map')
    __main__.unload_map()
    print('load_map')
    __main__.load_map(map)
    __main__.player.x = math.floor((x * 32.0) / 32)
    __main__.player.y = math.floor((y * 32.0) / 32)
    __main__.player.dest_x = __main__.player.x
    __main__.player.dest_y = __main__.player.y


def yes_no_box(default=True):
    if default:
        def_num = 0
    else:
        def_num = 1
    box = YesNoBox(def_num)
    __main__.ui_elements.append(box)
    pygame.event.clear()
    while not box.exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    box.exit = True
                if event.key == pygame.K_DOWN:
                    box.move_select()
                if event.key == pygame.K_UP:
                    box.move_select()
                if event.key == pygame.K_c:
                    box.select_option()
        if box.exit:
            break
        __main__.draw_all()
        __main__.clock.tick(__main__.fps)
    result = default
    if box.select == 0:
        result = True
    else:
        result = False
    __main__.ui_elements.remove(box)
    del box
    return result


def open_menu():
    menu = MenuBox()
    __main__.ui_elements.append(menu)
    while True:
        getout = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    getout = True
                if event.key == pygame.K_DOWN:
                    menu.move_select(1)
                if event.key == pygame.K_UP:
                    menu.move_select(-1)
                if event.key == pygame.K_c:
                    if menu.options[menu.select] == "EXIT":
                        getout = True
                    else:
                        menu.select_option()
        if getout:
            break
        __main__.draw_all()
        __main__.clock.tick(__main__.fps)
    __main__.ui_elements.remove(menu)
    del menu


def call_bag_screen():
    __main__.loop.run_until_complete(__main__.screen_blink(0.5))
    bag_screen = BagScreen(__main__.player.data.bag)
    __main__.ui_elements.append(bag_screen)
    pygame.event.clear()
    while True:
        getout = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    getout = True
                if event.key == pygame.K_DOWN:
                    bag_screen.move_select(1)
                if event.key == pygame.K_UP:
                    bag_screen.move_select(-1)
                if event.key == pygame.K_RIGHT:
                    bag_screen.change_pocket(1)
                if event.key == pygame.K_LEFT:
                    bag_screen.change_pocket(-1)
                if event.key == pygame.K_c:
                    if bag_screen.select == len(bag_screen.current_pocket):
                        getout = True
                    else:
                        bag_screen.select_option()
                        getout = True
        if getout:
            break
        __main__.draw_all()
        __main__.clock.tick(__main__.fps)
    __main__.loop.run_until_complete(__main__.screen_blink(0.5))
    __main__.ui_elements.remove(bag_screen)
    del bag_screen


def call_pokegear_screen():
    __main__.loop.run_until_complete(__main__.screen_blink(0.5))
    gear_screen = GearScreen()
    __main__.ui_elements.append(gear_screen)
    pygame.event.clear()
    while True:
        getout = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    getout = True
                if event.key == pygame.K_DOWN:
                    pass
                if event.key == pygame.K_UP:
                    pass
                if event.key == pygame.K_RIGHT:
                    gear_screen.move_select(1)
                if event.key == pygame.K_LEFT:
                    gear_screen.move_select(-1)
                if event.key == pygame.K_c:
                    if gear_screen.scene is not None:
                        if gear_screen.scene.type == 'map_screen':
                            call_into_map_screen(gear_screen.scene)
        if getout:
            break
        __main__.draw_all()
        __main__.clock.tick(__main__.fps)
    __main__.loop.run_until_complete(__main__.screen_blink(0.5))
    __main__.ui_elements.remove(gear_screen)
    del gear_screen


def call_into_map_screen(map_scene):
    pygame.event.clear()
    getout = False
    while not getout:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    getout = True
                if event.key == pygame.K_DOWN:
                    map_scene.move_select(__main__.DIR_DOWN)
                if event.key == pygame.K_UP:
                    map_scene.move_select(__main__.DIR_UP)
                if event.key == pygame.K_RIGHT:
                    map_scene.move_select(__main__.DIR_RIGHT)
                if event.key == pygame.K_LEFT:
                    map_scene.move_select(__main__.DIR_LEFT)
        __main__.draw_all()
        __main__.clock.tick(__main__.fps)



def call_name_entry_screen():
    __main__.loop.run_until_complete(__main__.screen_blink(0.5))
    name_screen = NameEntryScreen()
    __main__.ui_elements.append(name_screen)
    pygame.event.clear()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    getout = True
                if event.key == pygame.K_DOWN:
                    name_screen.move_select(__main__.DIR_DOWN)
                if event.key == pygame.K_UP:
                    name_screen.move_select(__main__.DIR_UP)
                if event.key == pygame.K_RIGHT:
                    name_screen.move_select(__main__.DIR_RIGHT)
                if event.key == pygame.K_LEFT:
                    name_screen.move_select(__main__.DIR_LEFT)
                if event.key == pygame.K_c:
                    name_screen.select_option()
        if name_screen.complete:
            break
        __main__.draw_all()
        __main__.clock.tick(__main__.fps)
    name = name_screen.name_string
    __main__.loop.run_until_complete(__main__.screen_blink(0.5))
    __main__.ui_elements.remove(name_screen)
    del name_screen
    return name


def clear_ui(ui_type):
    for element in __main__.ui_elements:
        if element.type == ui_type:
            __main__.ui_elements.remove(element)
            del element


@asyncio.coroutine
def save_game_async(obj, file_path):
    yield from asyncio.sleep(0.5)
    with open(file_path, "wb") as f:
        if f.writable():
            s_obj = pickle.dumps(obj)
            f.write(s_obj)
            clear_ui('text_box')
            return 1
        else:
            print(project.str_list['save_error'])
            clear_ui('text_box')
            return 0


@asyncio.coroutine
def load_game_async(file_path):
    yield from asyncio.sleep(0.5)
    with open(file_path, "wb") as f:
        m = f.readall()
        obj = pickle.loads(m)
        return obj

import battle

def start_wild_battle(mon, level, shiny=False, fateful=False):
    wild_mon = Mon(mon, level, shiny=shiny)
    battle_s = battle.WildBattleScene(wild_mon)
    __main__.loop.run_until_complete(__main__.screen_blink(0.5))
    __main__.ui_elements.append(battle_s)
    show_text(project.str_list['wild_battle_begin'].format(wild_mon.nickname))
    show_text(project.str_list['plyr_battle_send_out'].format(battle_s.plyr_battler.mon.nickname))
    battle_s.stage = 1
    pygame.event.clear()
    while not battle_s.exit:
        while battle_s.plyr_battler.action['type'] == '' and battle_s.plyr_battler.action['value'] == '':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        battle_s.select_option()
                    if event.key == pygame.K_x:
                        battle_s.back_option()
                    if event.key == pygame.K_DOWN:
                        battle_s.move_option(__main__.DIR_DOWN)
                    if event.key == pygame.K_UP:
                        battle_s.move_option(__main__.DIR_UP)
                    if event.key == pygame.K_RIGHT:
                        battle_s.move_option(__main__.DIR_RIGHT)
                    if event.key == pygame.K_LEFT:
                        battle_s.move_option(__main__.DIR_LEFT)
                if battle_s.exit:
                    break
                __main__.draw_all()
                __main__.clock.tick(__main__.fps)
        battle_s.play_turn()
        __main__.draw_all()
        __main__.clock.tick(__main__.fps)
    loop.run_until_complete(__main__.screen_blink(0.5))
    __main__.ui_elements.remove(battle_s)
    del battle_s
