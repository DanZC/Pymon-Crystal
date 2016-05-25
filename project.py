import pygame
import json
import __main__
import engine

data_dir = 'Data/'

print('Compiling databases...')

me_list = []
me_list.append(pygame.mixer.Sound(__main__.me_dir + 'get_item.wav'))
#me_list.append(pygame.mixer.Sound(me_dir + '1.wav'))

se_list = []
se_list.append(pygame.mixer.Sound(__main__.sound_dir + 'select.wav'))
se_list.append(pygame.mixer.Sound(__main__.sound_dir + 'door_enter.wav'))
se_list.append(pygame.mixer.Sound(__main__.sound_dir + 'door_exit.wav'))
se_list.append(pygame.mixer.Sound(__main__.sound_dir + 'bump.wav'))
se_list.append(pygame.mixer.Sound(__main__.sound_dir + 'pc_on.wav'))
se_list.append(pygame.mixer.Sound(__main__.sound_dir + 'pc_off.wav'))


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
    type_list[type] = type
    print("New type,",type_list[type])

move_list = {}

with open(data_dir + 'species.json') as json_data:
    mon_list = json.load(json_data)
x = 0
species_list = []
for mon in mon_list['species']:
    new_mon = engine.MonSpecies(mon['name'],mon['stats'],mon['learnset'],mon['evolution'],mon['gender_ratio'],int(mon['catch_rate']))
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