import asyncio
import __main__
import engine


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
    __main__.loop.run_until_complete(engine.show_text(text))
    __main__.inEvent = False