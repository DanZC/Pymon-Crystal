from const import *
from __main__ import musicsys, loop, screen_blink, gameDisplay, winDisplay, clock
from engine import Text
import pygame


class AnimatedTitle:
    def __init__(self):
        self.images = []
        source = pygame.image.load(ui_dir + "title.png")
        self.images.append(pygame.transform.chop(pygame.transform.chop(source, (320,0,0,0)), (320,288,960,288)))
        self.images.append(pygame.transform.chop(pygame.transform.chop(source, (0, 0, 320, 0)), (320, 288, 960, 288)))
        self.images.append(pygame.transform.chop(pygame.transform.chop(source, (0, 0, 640, 0)), (320, 288, 960, 288)))
        self.current_image = 0
        self.s = 0

    def draw(self):
        gd = gameDisplay
        gd.blit(self.images[self.current_image], (0,0))
        self.s += 1
        if self.s > 4:
            self.s = 0
            if self.current_image + 1 >= len(self.images):
                self.current_image = 0
            else:
                self.current_image += 1


def call_title_sequence():
    print('Start title screen')
    title_screen = AnimatedTitle()
    exit = False
    while not exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    loop.run_until_complete(screen_blink(0.5))
                    exit = True
        title_screen.draw()
        version_string = 'v' + str(build_version[0]) + '.' + str(build_version[1]) + '.' + str(build_version[2])
        text = Text(text=version_string, pos=(0, 0), color=white)
        text.draw()
        musicsys.update()
        winDisplay.blit(pygame.transform.scale(
            gameDisplay, (
                display_width * resolution_factor,
                display_height * resolution_factor
            ), winDisplay), (0, 0))
        pygame.display.update([
            0, 0,
            display_width * resolution_factor, display_height * resolution_factor
        ])
        clock.tick(30)
    del title_screen
