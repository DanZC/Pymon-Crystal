import fluidsynth
import asyncio

C0 = 0
Cs0 = 1 
D0 = 2
Ds0 = 3
Eb0 = 3
E0 = 4
F0 = 5
Fs0 = 6
G0 = 7
Gs0 = 8
Ab0 = 8
A0 = 9
Bb0 = 10
B0 = 11
C1 = 12
Cs1 = 13
D1 = 14
Eb1 = 15
E1 = 16
F1 = 17
Fs1 = 18
G1 = 19
Gs1 = 20
Ab1 = 20
A1 = 21
Bb1 = 22
B1 = 23
C2 = 24
Cs2 = 25
D2 = 26
Eb2 = 27
E2 = 28
F2 = 29
Fs2 = 30
G2 = 31
Ab2 = 32
A2 = 33
Bb2 = 34
B2 = 35
C3 = 36
Cs3 = 37
D3 = 38
C4 = 48
C5 = 60
C6 = 72
C7 = 84
C8 = 96

class MusicPlayer:
    def __init__(self):
        self.synth = fluidsynth.Synth()
        self.sf = self.synth.sfload("PokemonCrystal.sf2")
        self.channel = []
        for x in range(4):
            self.channel.append(Channel(x))
        self.position = 0
        self.tempo = 120

    def get_time_from_tempo(self,beats):
        bps = self.tempo / 60
        return beats / bps

    @asyncio.coroutine
    def play_note(self,channel,note,duration=1):
        self.synth.noteon(channel,note,128)
        yield from asyncio.sleep(duration)
        self.synth.noteoff(channel,note)

    @asyncio.coroutine
    def wait(duration=1):
        yield from asyncio.sleep(duration)
    
    def change_instrument(self,instrument):
        pass

class Channel:
    def __init__(self,number):
        self.instrument = 0
        self.number = number