import asyncio
import __main__
from engine import show_text


def __init__(npc_obj):
    global npc
    global text
    npc = npc_obj
    if 'text' in npc.properties:
        text = npc.properties['text']
    else:
        text = '...'


def run():
    npc.turn_toward_player()
    __main__.inEvent = True
    show_text(text)
    __main__.inEvent = False