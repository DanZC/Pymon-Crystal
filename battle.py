from const import *
import __main__
import math, random
import engine
import project
from engine import show_text, reformat_text, Text, white, black
import pygame


class TrainerBattleScene:
    def __init__(self):
        pass


class WildBattleScene:
    def __init__(self, mon):
        self.type = 'wild_battle'
        self.stage = 0
        self.option = dict()
        self.option['list'] = "main"
        self.option['index'] = 0
        self.wild_mon = mon
        self.wild_battler = Battler(self.wild_mon)
        self.wild_ai = AI(value=0,battler=self.wild_battler)
        self.player = __main__.player
        self.player_mon = self.player.data.party.get_first_able()
        self.plyr_battler = Battler(self.player_mon)
        self.exit = False
        self.player_mon_img = pygame.image.load(__main__.ui_dir + '/player_mon_img.png')
        self.battle_menu_bg = pygame.image.load(__main__.ui_dir + '/battle_menu.png')
        self.selector = pygame.image.load(__main__.ui_dir + '/selector.png')

    def move_option(self, direction):
        if self.option['list'] == 'main' or self.option['list'] == 'moves':
            if self.option['index'] == 0:
                if direction == __main__.DIR_RIGHT:
                    self.option['index'] = 1
                elif direction == __main__.DIR_UP:
                    self.option['index'] = 2
                elif direction == __main__.DIR_DOWN:
                    self.option['index'] = 2
            elif self.option['index'] == 1:
                if direction == __main__.DIR_LEFT:
                    self.option['index'] = 0
                elif direction == __main__.DIR_UP:
                    self.option['index'] = 3
                elif direction == __main__.DIR_DOWN:
                    self.option['index'] = 3
            elif self.option['index'] == 2:
                if direction == __main__.DIR_RIGHT:
                    self.option['index'] = 3
                elif direction == __main__.DIR_UP:
                    self.option['index'] = 0
                elif direction == __main__.DIR_DOWN:
                    self.option['index'] = 0
            elif self.option['index'] == 3:
                if direction == __main__.DIR_LEFT:
                    self.option['index'] = 2
                elif direction == __main__.DIR_UP:
                    self.option['index'] = 1
                elif direction == __main__.DIR_DOWN:
                    self.option['index'] = 1

    def select_option(self):
        if self.option['list'] == 'main':
            if self.option['index'] == 0:
                if len(self.player_mon.moves) >= 1:
                    self.option['list'] = 'moves'
                    print('get moves')
                else:
                    self.plyr_battler.select_action('move', 'STRUGGLE')
                    print('use struggle')
            elif self.option['index'] == 3:
                self.plyr_battler.select_action('flee', '')
                print('flee')
        elif self.option['list'] == 'moves':
            if self.option['index'] <= len(self.plyr_battler.mon.moves) - 1:
                self.plyr_battler.select_action('move',self.plyr_battler.mon.moves[self.option['index']])

    def back_option(self):
        if self.option['list'] == 'moves':
            self.option['list'] = 'main'
            self.option['index'] = 0

    def play_turn(self):
        print('play turn')
        while True:
            # If the player uses "RUN"
            if self.plyr_battler.action['type'] == 'flee':
                if self.wild_battler.mon.stat['spe'] == 0:
                    show_text(project.str_list['wild_battle_esc'])
                    self.exit = True
                    break
                f = 256
                if f > 255:
                    show_text(project.str_list['wild_battle_esc'])
                    self.exit = True
                    break
                elif self.plyr_battler.mon.stat['spe'] < self.wild_battler.mon.stat['spe']:
                    pass
            # If the player uses an item from the bag.
            if self.plyr_battler.action['type'] == 'item':
                pass
            # If the player switches out a pokemon.
            # If the player uses a move.
            if self.plyr_battler.action['type'] == 'move':
                plyr = self.plyr_battler
                wild = self.wild_battler
                move_plyr = project.move_list[plyr.action['value']]
                #move_wild = wild.mon.moves[int(wild.action['value'])]
                if self.plyr_battler.stat['spe'] > self.wild_battler.stat['spe']:
                    if confusion_check(self.plyr_battler
                                       ) and love_check(self.plyr_battler
                                                        ) and paralyze_check(self.plyr_battler):
                        show_text(project.str_list['mon_use_move'].format(self.plyr_battler.mon.nickname,move_plyr.name),False)
                        # If the move connects
                        if random.randint(0,100) <= move_plyr.accuracy:
                            if move_plyr.effect['type'] == "SINGLE_HIT":
                                dmg = calculate_damage(plyr,wild,move_plyr)
                                wild.apply_damage(dmg)
                                if wild.mon.current_hp <= 0:
                                    wild.faint()
                        # If the move misses
                        else:
                            show_text(project.str_list['mon_miss'].format(self.plyr_battler.mon.nickname),False)
            elif self.plyr_battler.stat['spe'] < self.wild_battler.stat['spe']:
                print('slower')
            break
        self.plyr_battler.action['type'] = ''
        self.plyr_battler.action['value'] = ''
        self.wild_battler.action['type'] = ''
        self.wild_battler.action['value'] = ''

    def draw(self):
        gd = __main__.gameDisplay
        gd.fill(white)
        if self.wild_mon.shiny:
            gd.blit(self.wild_mon.species.image_front_shiny, (184, 6))
        else:
            gd.blit(self.wild_mon.species.image_front, (184, 6))
        if self.stage == 0:
            gd.blit(self.player.data.back, (16, 64))
        if self.stage > 0:
            if self.player_mon.shiny:
                gd.blit(self.player_mon.species.image_back_shiny, (16, 64))
            else:
                gd.blit(self.player_mon.species.image_back, (16, 64))
            gd.blit(self.player_mon_img, (143, 112))
            origin = (143, 112)
            player_mon_nick = Text(self.plyr_battler.mon.nickname, (origin[0] + 32, origin[1]))
            player_mon_nick.draw()
            player_mon_lvl = Text(str(self.plyr_battler.mon.level), (origin[0] + 97 + 16, origin[1] + 16))
            player_mon_lvl.draw()
            text = Text("?",(origin[0] + 138, origin[1] + 16))
            if self.plyr_battler.mon.gender == 'm':
                text.text = reformat_text("{m}")
            elif self.plyr_battler.mon.gender == "f":
                text.text = reformat_text("{f}")
            text.draw()
            if(self.plyr_battler.mon.current_hp / self.plyr_battler.mon.stat['hp'] > 0.5):
                hp = (0, 0xb8, 0)
            elif(self.plyr_battler.mon.current_hp / self.plyr_battler.mon.stat['hp'] > 0.25):
                hp = (0xb8, 0xb8, 0)
            else:
                hp = (0xb8, 0, 0)
            pygame.draw.rect(gd,
                             hp,
                             (origin[0] + 50,
                              origin[1] + 38,
                              96 * (self.plyr_battler.mon.current_hp / self.plyr_battler.mon.stat['hp']),
                              4))
            text = Text(str(self.plyr_battler.mon.current_hp),(origin[0] + 80, origin[1] + 48))
            text.draw()
            text = Text(str(self.plyr_battler.mon.stat['hp']), (origin[0] + 144, origin[1] + 48), align=ALIGN_RIGHT)
            text.draw()
            gd.blit(self.battle_menu_bg, (0, __main__.display_height - 96))
            if self.option['list'] == 'main':
                if self.option['index'] == 0:
                    gd.blit(self.selector, (0, 0))
                if self.option['index'] == 1:
                    gd.blit(self.selector,(32,0))
                if self.option['index'] == 2:
                    gd.blit(self.selector,(0,32))
                if self.option['index'] == 3:
                    gd.blit(self.selector,(32,32))
            elif self.option['list'] == 'moves':
                if self.option['index'] == 0:
                    gd.blit(self.selector,(0,0))
                if self.option['index'] == 1:
                    gd.blit(self.selector,(32,0))
                if self.option['index'] == 2:
                    gd.blit(self.selector,(0,32))
                if self.option['index'] == 3:
                    gd.blit(self.selector,(32,32))
            text = Text(self.plyr_battler.action['type'], (4, 48))
            text.draw()
            text = Text(self.plyr_battler.action['value'], (4, 64))
            text.draw()


class Battler:
    def __init__(self, mon):
        self.mon = mon
        self.action = dict()
        self.action['type'] = ''
        self.action['value'] = ''
        self.stat_mod = {'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0}
        self.temp_status = dict()
        self.status = {"name":mon.status, "count":0}
        self.stat = self.mon.stat

    def select_action(self, type, value):
        self.action['type'] = type
        self.action['value'] = value

    def able_to_fight(self):
        return self.mon.current_hp > 0

    def change_self_stat(self, stat, amount):
        if self.stat_mod[stat] + amount > 6:
            self.stat_mod[stat] = 6
        elif self.stat_mod[stat] + amount < -6:
            self.stat_mod[stat] = -6
        if amount > 0:
            show_text(project.str_list['mon_raise_stat'].format(self.mon.nickname, stat.capitalize()))
        elif amount < 0:
            show_text(project.str_list['mon_lower_stat'].format(self.mon.nickname, stat.capitalize()))

    def recalculate_stats(self):
        self.stat = dict()
        for key in self.mon.stat.keys():
            if key == 'hp':
                continue
            if self.stat_mod[key] >= 0:
                self.stat[key] = self.mon.stat[key] * ((2 + self.stat_mod[key]) / 2)
            elif self.stat_mod[key] < 0:
                self.stat[key] = self.mon.stat[key] * (2 / (2 - self.stat_mod[key]))

    def has_status(self, status):
        return self.status["name"] == status

    def has_temp_status(self, status):
        return status in self.temp_status

    def apply_status(self, status):
        self.status = {"name":status,"count":0}

    def remove_status(self):
        self.status = {"name":"NON", "count":0}

    def apply_temp_status(self, status):
        self.temp_status[status] = {"count":0}

    def remove_all_temp_statuses(self):
        self.temp_status = dict()

    def push_status_to_mon(self):
        self.mon.status = self.status['name']

    def apply_damage(self, amount):
        if self.mon.current_hp - amount > 0:
            self.mon.current_hp -= amount
        else:
            self.mon.current_hp = 0

    def faint(self):
        show_text(project.str_list['mon_faint'].format(self.mon.nickname))


class AI:
    def __init__(self, value, battler, trainer=None, items=list()):
        self.value = value
        self.items = items
        self.trainer = trainer
        self.battler = battler

    def calculate_next_move(self):
        # Am I a wild mon?
        if self.value == 0:
            self.battler.select_action('moves', self.battler.mon.moves[math.floor(random.randrange(0,len(self.battler.mon.moves)))])
        else:
            # Do I have other mons I can switch to?
            if len(self.trainer.party) > 1:
                # Can I switch to a different mon?
                if 'TRAP' not in self.battler.temp_status:
                    pass
                else:
                    print("I can't switch out!")
            # Is my mon at low health?
            if self.battler.mon.current_hp < (self.battler.mon.stat['hp'] * 0.4):
                print("My mon is low on health!")
                item_to_use = ""
                # Do I have a healing item available?
                for item in self.items:
                    if item.effect == "HEALHP" or item.effect == "HEALHP%" or item.effect == "HEALALL":
                        self.battler.select_action('item', self.items[self.items.index(item)])
                        item_to_use = self.items[self.items.index(item)]
                if item_to_use != "":
                    return
            move_damages = []
            # Check all my moves and see which one will do the most damage.
            for move in self.battler.mon.moves:
                if move.pp != 0:
                    move_damages.append(calculate_damage(self.battler, self.battler, move))
                else:
                    move_damages.append(-1)
            m = 0
            for move in self.battler.mon.moves:
                if self.battler.mon.moves.index(move) == 0:
                    continue
                if move_damages[self.battler.mon.moves.index(move)] > move_damages[m]:
                    m = self.battler.mon.moves.index(move)
            self.battler.select_action('moves', self.battler.mon.moves[m])


def calculate_damage(battler_a: Battler, battler_b: Battler, move):
    other = 1
    if battler_a.mon.status == "burn":
        other = 0.5
    stab = 1
    if battler_a.mon.species.type[0] == move.type:
        stab = 1.5
    elif len(battler_a.mon.species.type) >= 2:
        if battler_a.mon.species.type[1] == move.type:
            stab = 1.5
    type_eff = 1
    for type in battler_b.mon.species.type:
        type_eff *= get_type_eff(project.type_list[move.type],project.type_list[type])
    mod = stab * type_eff * other
    if move.get_category() == 'PHYSICAL':
        damage = ((2 * battler_a.mon.level + 10) / 250) * (battler_a.stat['atk'] / battler_b.stat['def']
                                                           ) * move.power * mod
    else:
        damage = ((2 * battler_a.mon.level + 10) / 250) * (battler_a.stat['spa'] / battler_b.stat['spd']
                                                           ) * move.power * mod
    print("Calculated damage of", math.floor(damage))
    return math.floor(damage)


def get_type_eff(type_a: dict, type_b: dict):
    for eff in type_a:
        if eff != 'name' and eff != 'category':
            if eff == project.type_list[type_b['name']]:
                return eff
    return 1


def confusion_check(battler):
    # Is the Pokemon confused?
    if battler.has_status("confusion"):
        show_text(project.str_list['mon_confuse'].format(battler.mon.nickname))
        r = random.randint(1,4)
        print("DEBUG: CONF_CHECK:",r)
        if r == 1:
            show_text(project.str_list['mon_hurt_confuse'].format(battler.mon.nickname))
            return False
    return True


def love_check(battler):
    if battler.has_status("love"):
        show_text(project.str_list['mon_love'].format(battler.mon.nickname))
        r = random.randint(1,4)
        print("DEBUG: INFA_CHECK:",r)
        if r == 1:
            show_text(project.str_list['mon_hurt_love'].format(battler.mon.nickname))
            return False
    return True


def paralyze_check(battler):
    if battler.has_status("paralysis"):
        r = random.randint(1,3)
        print("DEBUG: PARA_CHECK:",r)
        if r == 1:
            return False
    return True


def sleep_check(battler):
    if battler.has_status("sleep"):
        show_text(project.str_list['mon_sleep'].format(battler.mon.nickname))
        return False
    return True
