import tdl
import textwrap
from src.utils import *


class ScreenSwitcher:

    def __init__(self, console, root_console):
        self.__console = console
        self.__root_console = root_console

    def show(self, screen_type, player=None):
        if screen_type == GameStates.MENU:
            self.__main_menu()
        if screen_type == GameStates.LEVEL_UP:
            self.__level_up_menu(player)
        if screen_type in {GameStates.SHOW_INVENTORY,
                           GameStates.DROP_INVENTORY}:
            self.__inventory_menu(player)
        if screen_type == GameStates.INFO:
            self.__info_screen()
        if screen_type == GameStates.CHARACTER_SCREEN:
            self.__character_screen(player)

    def __main_menu(self):
        UISettings.background_image.blit_2x(self.__root_console, 0, 0)
        title = UISettings.window_title
        center = (UISettings.screen_width - len(title)) // 2
        self.__root_console.draw_str(center, UISettings.screen_height // 2 - 4,
                                     title, bg=None, fg=UISettings.light_yellow)
        center = (UISettings.screen_width - len(title)) // 2
        self.__root_console.draw_str(center, UISettings.screen_height - 2, UISettings.author, bg=None,
                                     fg=UISettings.light_yellow)

        self.__menu('', ['New game', 'About game', 'Quit'], 24)

    def __menu(self, header, options, width):
        header_wrapped = textwrap.wrap(header, width)
        header_height = len(header_wrapped)
        height = len(options) + header_height
        window = tdl.Console(width, height)
        window.draw_rect(0, 0, width, height, None, fg=(255, 255, 255), bg=None)
        for i, line in enumerate(header_wrapped):
            window.draw_str(0, 0 + i, header_wrapped[i])
        y = header_height
        letter_index = ord('a')
        for option_text in options:
            text = '(' + chr(letter_index) + ') ' + option_text
            window.draw_str(0, y, text, bg=None)
            y += 1
            letter_index += 1
        x = UISettings.screen_width // 2 - width // 2
        y = UISettings.screen_height // 2 - height // 2
        self.__root_console.blit(window, x, y, width, height, 0, 0)
        tdl.flush()

    def __inventory_menu(self, player):
        inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'
        options = []
        if len(player.inventory.items) == 0:
            options = ['Inventory is empty.']
        for item in player.inventory.items:
            if len(options) > 26:
                break
            if player.equipment.main_hand == item:
                options.append('{0} (on main hand)'.format(item.name))
            elif player.equipment.off_hand == item:
                options.append('{0} (on off hand)'.format(item.name))
            else:
                options.append(item.name)
        self.__menu(inventory_title, options, UISettings.inventory_width)

    def __character_screen(self, player):
        width, height = UISettings.character_screen
        self.__show_text_window(width, height, player.get_info())

    def __level_up_menu(self, player):
        options = ['Constitution (+20 HP, from {0})'.format(player.fighter.max_hp),
                   'Strength (+1 attack, from {0})'.format(player.fighter.power),
                   'Agility (+1 defense, from {0})'.format(player.fighter.defense)]
        self.__menu('', options, UISettings.inventory_width)

    def __info_screen(self):
        self.__root_console.clear()
        with open(UISettings.info_file) as f:
            lines = f.readlines()
        width, height = 30, 25
        self.__show_text_window(width, height, lines)

    def __show_text_window(self, width, height, text):
        screen_width, screen_height = UISettings.screen_width, UISettings.screen_height
        window = tdl.Console(width, height)
        window.draw_rect(0, 0, width, height,
                         None, fg=UISettings.white, bg=None)
        for i in range(len(text)):
            window.draw_str(0, i + 1, text[i].replace('\n', ''))
        x = screen_width // 2 - width // 2
        y = screen_height // 2 - height // 2
        self.__root_console.blit(window, x, y, width,
                                 height, 0, 0)
