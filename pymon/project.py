from const import *
import pygame
import json
import pymon.engine as engine

data_dir = 'Data/'
did_init = False

me_list = list()
se_list = list()
item_list = dict()
type_list = dict()
move_list = dict()
species_list = list()
str_list = list()


def init():
    global did_init
    if not did_init:
        print('Compiling databases...')

        me_list = []
        me_list.append(pygame.mixer.Sound(me_dir + 'get_item.wav'))
        #me_list.append(pygame.mixer.Sound(me_dir + '1.wav'))

        se_list = []
        se_list.append(pygame.mixer.Sound(sound_dir + 'select.wav'))
        se_list.append(pygame.mixer.Sound(sound_dir + 'door_enter.wav'))
        se_list.append(pygame.mixer.Sound(sound_dir + 'door_exit.wav'))
        se_list.append(pygame.mixer.Sound(sound_dir + 'bump.wav'))
        se_list.append(pygame.mixer.Sound(sound_dir + 'pc_on.wav'))
        se_list.append(pygame.mixer.Sound(sound_dir + 'pc_off.wav'))


        with open(data_dir + 'items.json') as json_data:
            items = json.load(json_data)
        item_list = {}
        for item in items['items']:
            new_item = engine.Item(item['name'],item['desc'],item['type'],item['price'],item['can_use'],item['effect'])
            item_list[new_item.name] = new_item
            print('New item, "' + new_item.name + '," with a type of ' + new_item.type + '.')

        type_list = {}
        with open(data_dir + 'types.json') as json_data:
            types_list = json.load(json_data)
        for type in types_list['types']:
            type_list[type['name']] = type
            print("New type,",type_list[type['name']])
        del types_list

        move_list = {}
        with open(data_dir + 'moves.json') as json_data:
            moves = json.load(json_data)
        for move in moves['moves']:
            if 'secondary' in move:
                if 'field_effect' in move:
                    move_entry = engine.Move(
                        move,int(move['pp']),int(move['power']),int(move['accuracy']),move['type'],
                        move['effect'],move['secondary'],move['field_effect'])
                else:
                    move_entry = engine.Move(
                        move,int(move['pp']),int(move['power']),int(move['accuracy']),move['type'],
                        move['effect'],move['secondary'])
            elif 'field_effect' in move:
                move_entry = engine.Move(
                    move,int(move['pp']),int(move['power']),int(move['accuracy']),move['type'],
                    move['effect'],field_effect=move['field_effect'])
            else:
                move_entry = engine.Move(move,int(move['pp']),int(move['power']),int(move['accuracy']),move['type'],move['effect'])
            move_list[move['name']] = move_entry
            print("New move,",move_entry.name,"with a type of",move_entry.type)
        del moves

        with open(data_dir + 'species.json') as json_data:
            mon_list = json.load(json_data)
        x = 0
        species_list = []
        for mon in mon_list['species']:
            mv_dict = {}
            for move_l in mon['learnset']:
                for n in range(100):
                    if str(n) in move_l:
                        list_0 = []
                        for move in move_l[str(n)]:
                            list_0.append(move_list[move])
                        mv_dict[str(n)] = list_0
            new_mon = engine.MonSpecies(
                species_id=x,
                name=mon['name'],
                base_stats=mon['stats'],
                type=mon['type'],
                learnset=mv_dict,
                evolutions=mon['evolution'],
                gender_ratio=mon['gender_ratio'],
                catchrate=int(mon['catch_rate'])
            )
            print('New mon, "' + new_mon.name + '," with an id of ' + str(x))
            species_list.append(new_mon)
            x += 1
        del x
        del mon_list

        str_list = []
        try:
            with open(data_dir + 'text.json') as json_data:
                raw_text_list = json.load(json_data)
            str_list = raw_text_list['texts']
            del raw_text_list
            print(str_list['success'])
        except:
            print('Something went wrong while compiling text...')

        print('Databases loaded...')
        did_init = True
