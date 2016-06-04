import pygame
import __main__
import engine
import project
font = pygame.font.Font("UI/font.ttf",16)

white = (255,255,255)
black = (0,0,0)


class DebugMenu:
    def __init__(self, options = list()):
        self.options = options
        self.select = self.options[0]
        self.select_num = 0
        self.exit = False

    def move_select(self, amount):
        if amount < 0:
            if self.select_num + amount < 0:
                self.select_num = len(self.options) - 1
            else:
                self.select_num -= 1
        elif amount > 0:
            if self.select_num + amount > len(self.options) - 1:
                self.select_num = 0
            else:
                self.select_num += 1
        self.select = self.options[self.select_num]

    def select_option(self):
        if self.select == "VIEW MONS":
            list = []
            for mon in __main__.player.data.party.mons:
                gender = "N"
                if mon.gender == "m":
                    gender = engine.reformat_text("{m}")
                elif mon.gender == "f":
                    gender = engine.reformat_text("{f}")
                list.append(mon.nickname + " L:" + str(mon.level) + " " + gender)
            list.append("BACK")
            call_debug_submenu(list)
        if self.select == "BIKE":
            list = []
            if __main__.player.data.on_bike:
                list.append("DISMOUNT")
            else:
                list.append("MOUNT")
            list.append("BACK")
            call_debug_submenu(list)
        if self.select == "MOUNT":
            __main__.player.data.on_bike = True
            __main__.player.update_image()
            self.exit = True
        if self.select == "DISMOUNT":
            __main__.player.data.on_bike = False
            __main__.player.update_image()
            self.exit = True
        if self.select == engine.reformat_text("OPEN {poke}GEAR"):
            engine.call_pokegear_screen()
        if self.select == "TEST WILD BATTLE":
            engine.start_wild_battle(project.species_list[0],100)
        if self.select == "INPUT NAME":
            engine.call_name_entry_screen()
        elif self.select == "EXIT" or self.select == "BACK":
            self.exit = True

    def draw(self):
        gd = __main__.gameDisplay
        gd.fill(black)
        x = 32
        n = 0
        for option in self.options:
            text = font.render(option,False,white)
            gd.blit(text,(x,n))
            n += 32
        pointlist = []
        pointlist.append((16,self.select_num * 32))
        pointlist.append((24,(self.select_num * 32)+8))
        pointlist.append((16,(self.select_num * 32)+16))
        pygame.draw.polygon(gd,white,pointlist)


def call_debug_screen():
    pygame.mixer.music.pause()
    pokegear = engine.reformat_text("OPEN {poke}GEAR")
    options = ["VIEW MONS",pokegear,"TEST WILD BATTLE","INPUT NAME","BIKE","EXIT"]
    debug_menu = DebugMenu(options)
    pygame.event.clear()
    while not debug_menu.exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    debug_menu.move_select(-1)
                elif event.key == pygame.K_DOWN:
                    debug_menu.move_select(1)
                elif event.key == pygame.K_c:
                    debug_menu.select_option()
        debug_menu.draw()
        __main__.winDisplay.blit(pygame.transform.scale(__main__.gameDisplay,(__main__.display_width * __main__.resolution_factor, __main__.display_height * __main__.resolution_factor),__main__.winDisplay),(0,0))
        pygame.display.update([0,0,__main__.display_width * __main__.resolution_factor,__main__.display_height * __main__.resolution_factor])
        __main__.clock.tick(30)
    pygame.mixer.unpause()

def call_debug_submenu(list):
    debug_menu = DebugMenu(list)
    pygame.event.clear()
    while not debug_menu.exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    debug_menu.move_select(-1)
                elif event.key == pygame.K_DOWN:
                    debug_menu.move_select(1)
                elif event.key == pygame.K_c:
                    debug_menu.select_option()
        debug_menu.draw()
        __main__.winDisplay.blit(pygame.transform.scale(__main__.gameDisplay,(__main__.display_width * __main__.resolution_factor, __main__.display_height * __main__.resolution_factor),__main__.winDisplay),(0,0))
        pygame.display.update([0,0,__main__.display_width * __main__.resolution_factor,__main__.display_height * __main__.resolution_factor])
        __main__.clock.tick(30)
