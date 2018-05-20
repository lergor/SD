from src.game_states import GameStates

ACTIVE_KEYS = {
    'UP': {'move': (0, -1)},
    'DOWN': {'move': (0, 1)},
    'LEFT': {'move': (-1, 0)},
    'RIGHT': {'move': (1, 0)},
    'ESCAPE': {'exit': True}
}

ACTIVE_CHARS = {
    'u': {'move': (0, -1)},
    'j': {'move': (0, 1)},
    'h': {'move': (-1, 0)},
    'k': {'move': (1, 0)},
    'y': {'move': (-1, -1)},
    'i': {'move': (1, -1)},
    'n': {'move': (-1, 1)},
    'm': {'move': (1, 1)},
    'w': {'wait': True},
    's': {'pickup': True},
    'd': {'damage': True},
    'a': {'show_inventory': True},
    'x': {'drop_inventory': True},
    'q': {'show_character_screen': True},
    '1': {'new_game': True},
    '2': {'info': True},
    '3': {'exit': True}
}

class Flags:

    def __init__(self, action=None):
        if action:
            self.update(action)
        else:
            self.__clear()

    def __clear(self):
        self.new_game = None
        self.info = None
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

    def update(self, action):
        self.__clear()
        self.new_game = action.get('new_game')
        self.info = action.get('info')
        self.exit = action.get('exit')
        self.move = action.get('move')
        self.wait = action.get('wait')
        self.pickup = action.get('pickup')
        self.show_inventory = action.get('show_inventory')
        self.drop_inventory = action.get('drop_inventory')
        self.inventory_index = action.get('inventory_index')
        self.take_stairs = action.get('take_stairs')
        self.level_up = action.get('level_up')
        self.show_character_screen = action.get('show_character_screen')
        self.fullscreen = action.get('fullscreen')


class InputHandler:

    def __init__(self):
        self.game_state = GameStates.PLAYERS_TURN

        self.STATE_TO_METHOD = {
            GameStates.PLAYERS_TURN: self.__handle_player_turn_keys,
            GameStates.PLAYER_DEAD: self.__handle_player_dead_keys,
            GameStates.SHOW_INVENTORY: self.__handle_inventory_keys,
            GameStates.DROP_INVENTORY: self.__handle_inventory_keys,
            GameStates.MENU: self.__handle_main_menu
        }

    def handle(self, user_input, state):
        action = dict()
        self.game_state = state
        self.user_input = user_input
        if self.user_input:
            if self.user_input.key == 'ESCAPE':
                action = {'exit': True}
            elif self.user_input.key == 'ENTER' and self.user_input.alt:
                action = {'fullscreen': True}
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
        if key_char in {'1', '2', '3'}:
            return ACTIVE_CHARS.get(key_char)
        return {}