import io
import os
import time
from glob import glob

file_list = []
dir_list = ['Data/','Encounters/','EventScripts/','ME/','Maps/','Music/','Sounds/','Sprites/','Tilesets/','UI/']
for cdir in dir_list:
    for f in os.listdir(cdir):
        if os.path.isfile(os.path.join(cdir,f)):
            file = io.FileIO(os.path.join(cdir,f))
            dict = {}
            bytearr = []
            byte = file.read(1)
            while byte:
                bytearr.append(byte)
                byte = file.read(1)
            dict['name'] = os.path.join(cdir,f)
            dict['size'] = len(bytearr)
            dict['f'] = bytearr
            file_list.append(dict)
            file.close()
            print(dict['name'],dict['size'],'bytes read.')

offset = 0
with open("header.bin", "w") as yo:
    for file in file_list:
        yo.write(file['name'])
        yo.write(":")
        yo.write(str(file['size']))
        yo.write(":")
        file['offset'] = offset
        yo.write(str(file['offset']))
        yo.write('|')
        offset += file['size']
        print(file['name'],hex(file['offset']),hex(file['size']))

with open("data.bin", "wb") as byteio:
    for file in file_list:
        time.sleep(1)
        for byte in file['f']:
            byteio.write(byte)
        print(file['name'],' written.')