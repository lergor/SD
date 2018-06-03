import tdl
from src.utils import *


logger = get_logger(__name__)


class Flags:
    """
    contains an interpretation of user input.
    """

    def __init__(self, input_dict=None):
        if input_dict:
            self.update(input_dict)
        else:
            self.__clear()

    def __clear(self):
        self.new_game = None
        self.show_info_screen = None
        self.exit = None
        self.move = None
        self.wait = None
        self.pickup = None
        self.show_inventory = None
        self.drop_inventory = None
        self.inventory_index = None
        self.take_stairs = None
        self.level_up = None
        self.show_character_screen = None
        self.fullscreen = None

    def update(self, input_dict):
        self.__clear()
        self.new_game = input_dict.get('new_game')
        self.show_info_screen = input_dict.get('info')
        self.exit = input_dict.get('exit')
        self.move = input_dict.get('move')
        self.wait = input_dict.get('wait')
        self.pickup = input_dict.get('pickup')
        self.show_inventory = input_dict.get('show_inventory')
        self.drop_inventory = input_dict.get('drop_inventory')
        self.inventory_index = input_dict.get('inventory_index')
        self.take_stairs = input_dict.get('take_stairs')
        self.level_up = input_dict.get('level_up')
        self.show_character_screen = input_dict.get('show_character_screen')
        self.message = input_dict.get('message')
        self.dead_entity = input_dict.get('dead')
        self.item_added = input_dict.get('item_added')
        self.item_consumed = input_dict.get('consumed')
        self.item_dropped = input_dict.get('item_dropped')
        self.equip = input_dict.get('equip')
        self.xp = input_dict.get('xp')


class InputHandler:
    """
    The class that listens to the user input and convert it into Flags.
    """

    def __init__(self):
        self.game_state = GameStates.PLAYER_TURN

        self.STATE_TO_METHOD = {
            GameStates.PLAYER_TURN: self.__handle_player_turn_keys,
            GameStates.PLAYER_DEAD: self.__handle_player_dead_keys,
            GameStates.SHOW_INVENTORY: self.__handle_inventory_keys,
            GameStates.DROP_INVENTORY: self.__handle_inventory_keys,
            GameStates.LEVEL_UP: self.__handle_level_up,
            GameStates.MENU: self.__handle_main_menu
        }

    def __catch_input(self):
        for event in tdl.event.get():
            if event.type == 'KEYDOWN':
                if event.key != 'TEXT':
                    logger.info('Pressed: {} {}'.format(event.key, event.char))
                return event
        return None

    def catch_and_process_input(self, state):
        action = dict()
        self.game_state = state
        self.user_input = self.__catch_input()
        if self.user_input:
            if self.user_input.key == 'ESCAPE':
                action = {'exit': True}
            else:
                handler = self.STATE_TO_METHOD.get(self.game_state, None)
                if handler:
                    action = handler()
            return Flags(action)
        return Flags()

    def __handle_player_turn_keys(self):
        key_char = self.user_input.char
        if key_char and key_char not in {'1', '2', '3'}:
            return ACTIVE_CHARS.get(key_char, {})
        else:
            return ACTIVE_KEYS.get(self.user_input.key, {})

    def __handle_player_dead_keys(self):
        key_char = self.user_input.char
        if self.user_input.char == 'q':
            return ACTIVE_CHARS.get(key_char, {})
        return {}

    def __handle_inventory_keys(self):
        if self.user_input.char:
            index = ord(self.user_input.char) - ord('a')
            if index >= 0:
                return {'inventory_index': index}
        return {}

    def __handle_main_menu(self):
        key_char = self.user_input.char
        if key_char in {'a', 'b', 'c'}:
            return ACTIVE_CHARS.get(key_char + key_char)
        return {}

    def __handle_level_up(self):
        if self.user_input.char:
            choices = ['hp', 'str', 'def']
            index = ord(self.user_input.char) - ord('a')
            if index < len(choices):
                return {'level_up': choices[index]}
        return {}
