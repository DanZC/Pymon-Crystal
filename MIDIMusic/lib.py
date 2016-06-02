import fluidsynth
import asyncio

G0 = 45

class MusicPlayer:
    def __init__(self):
        self.synth = fluidsynth.Synth()
        self.sf = self.synth.sfload("PokemonCrystal.sf2")


    @asyncio.coroutine
    def play_note(self,note,duration=1):
        self.synth.noteon()
        yield from asyncio.sleep(duration)

    @asyncio.coroutine
    def wait(duration=1):
        yield from asyncio.sleep(duration)