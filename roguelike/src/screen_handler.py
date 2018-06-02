import tdl
import textwrap
from src.utils import *


class ScreenHandler:

    def __init__(self, console, root_console):
        self.console = console
        self.root_console = root_console

    def show(self, screen_type, **kwargs):
        if screen_type == ScreenType.MAIN:
            self.__main_menu()
        if screen_type == ScreenType.LEVEL_UP:
            self.level_up_menu(kwargs.get('player'))

    def __main_menu(self):
        UISettings.background_image.blit_2x(self.root_console, 0, 0)
        title = UISettings.window_title
        center = (UISettings.screen_width - len(title)) // 2
        self.root_console.draw_str(center, UISettings.screen_height // 2 - 4,
                                   title, bg=None, fg=UISettings.colors.get('light_yellow'))
        title = 'By lergor'
        center = (UISettings.screen_width - len(title)) // 2
        self.root_console.draw_str(center, UISettings.screen_height - 2, title, bg=None,
                                   fg=UISettings.colors.get('light_yellow'))

        self.menu(self.root_console, '', ['Play a new game', 'Continue last game', 'Quit'],
             24, UISettings.screen_width, UISettings.screen_height)
        tdl.flush()

    def menu(self, root, header, options, width, screen_width, screen_height):
        if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

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
        x = screen_width // 2 - width // 2
        y = screen_height // 2 - height // 2
        root.blit(window, x, y, width, height, 0, 0)

    def inventory_menu(self, player):
        inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'
        if len(player.inventory.items) == 0:
            options = ['Inventory is empty.']
        else:
            options = []

            for item in player.inventory.items:
                if player.equipment.main_hand == item:
                    options.append('{0} (on main hand)'.format(item.name))
                elif player.equipment.off_hand == item:
                    options.append('{0} (on off hand)'.format(item.name))
                else:
                    options.append(item.name)

        self.menu(self.root_console, inventory_title, options, UISettings.inventory_width,
                  UISettings.screen_width, UISettings.screen_height)

    def character_screen(self, root_console, player, character_screen_width, character_screen_height, screen_width,
                         screen_height):
        window = tdl.Console(character_screen_width, character_screen_height)

        window.draw_rect(0, 0, character_screen_width, character_screen_height,
                         None, fg=(255, 255, 255), bg=None)

        window.draw_str(0, 1, 'Character Information')
        window.draw_str(0, 2, 'Level: {0}'.format(player.level.current_level))
        window.draw_str(0, 3, 'Experience: {0}'.format(player.level.current_xp))
        window.draw_str(0, 4, 'Experience to Level: {0}'.format(player.level.experience_to_next_level))
        window.draw_str(0, 6, 'Maximum HP: {0}'.format(player.fighter.max_hp))
        window.draw_str(0, 7, 'Attack: {0}'.format(player.fighter.power))
        window.draw_str(0, 8, 'Defense: {0}'.format(player.fighter.defense))

        x = screen_width // 2 - character_screen_width // 2
        y = screen_height // 2 - character_screen_height // 2
        root_console.blit(window, x, y, character_screen_width, character_screen_height, 0, 0)

    def message_box(self, root_console, header, width, screen_width, screen_height):
        self.menu(root_console, header, [], width, screen_width, screen_height)

    def level_up_menu(self, player):
        options = ['Constitution (+20 HP, from {0})'.format(player.fighter.max_hp),
                   'Strength (+1 attack, from {0})'.format(player.fighter.power),
                   'Agility (+1 defense, from {0})'.format(player.fighter.defense)]

        self.menu(self.root_console, '', options, UISettings.inventory_width,
                               UISettings.screen_width, UISettings.screen_height)
