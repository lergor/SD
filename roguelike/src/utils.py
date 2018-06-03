from tcod import image_load
from enum import Enum


class RenderOrder(Enum):
    STAIRS = 1
    CORPSE = 2
    ITEM = 3
    ACTOR = 4


class UISettings:
    game_font = 'src/font_and_pic/arial12x12.png'
    background_image = image_load('src/font_and_pic/background.png')
    info_file = 'src/font_and_pic/info'
    window_title = 'Roguelike'
    author = 'By lergor'
    screen_width = 90
    screen_height = 50
    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height
    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1
    map_width = 80
    map_height = 43
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 3
    max_items_per_room = 2
    inventory_width = 50
    character_screen = (30, 10)

    dark_wall = (0, 0, 100)
    dark_ground = (50, 50, 150)
    light_wall = (130, 110, 50)
    light_ground = (200, 180, 50)
    desaturated_green = (63, 127, 63)
    my_green = (0, 127, 63)
    darker_green = (0, 127, 0)
    dark_red = (191, 0, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)
    orange = (255, 127, 0)
    light_red = (255, 114, 114)
    darker_red = (127, 0, 0)
    violet = (127, 0, 255)
    yellow = (255, 255, 0)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    light_yellow = (255, 255, 114)
    light_violet = (184, 114, 255)
    sky = (20, 50, 150)
    darker_orange = (127, 63, 0)


class GameStates(Enum):
    PLAYER_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3
    SHOW_INVENTORY = 4
    DROP_INVENTORY = 5
    INFO = 6
    LEVEL_UP = 7
    CHARACTER_SCREEN = 8
    MENU = 9
    EXIT = 10


def find(f, seq):
    for x in seq:
        if f(x):
            return x


class EquipmentSlots(Enum):
    MAIN_HAND = 1
    OFF_HAND = 2
