import io
from __main__ import Player, GameData
from engine import PlayerData, Party, Mon, MonSpecies

gd = GameData()

player = PlayerData()

with open('somefile.bin', 'wb') as f:
    for x in range(0x800000):
        f.write(bytes(0xFF))
    f.seek(0x0, io.SEEK_SET)
    f.write(bytes(0))
    f.write(bytes(0))
    f.write(bytes("SAVE FILE"))
    f.seek(0x10,io.SEEK_SET)
    f.write(gd.flags)
    f.seek(0x80,io.SEEK_SET)
    f.write(gd.vars)
    f.seek(0x120)