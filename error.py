from const import *
from __main__ import gameDisplay, winDisplay, clock
from engine import font, Text
import pygame


class ErrorScreen:
    def __init__(self, text: str):
        self.image = pygame.image.load(ui_dir + "error.png")
        self.text = text

    def draw(self):
        gd = gameDisplay
        gd.blit(self.image, (0,0))
        texts = self.text.split("%n")
        p = (12, 160)
        l = 0
        for text in texts:
            r = Text(text, (p[0], p[1] + (32 * l)))
            r.draw()
            l += 1


def call_error_screen(text):
    error_screen = ErrorScreen(text)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        error_screen.draw()
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
    del error_screen
