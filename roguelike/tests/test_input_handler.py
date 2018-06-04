import unittest
from src.input_handler import InputHandler
from src.utils import GameStates, ACTIVE_CHARS, ACTIVE_KEYS


class TestInputHandler(unittest.TestCase):
    
    class KeyEvent:
        def __init__(self, char=None, key=None):
            self.char = char
            self.key = key
            self.type = 'KEYDOWN'

    def setUp(self):
        self.input_handler = InputHandler()
        self.menu_chars = {'a': 'new_game', 'b': 'show_info_screen', 'c': 'exit'}
        self.player_keys = ['u', 'j', 'h', 'k', 'y', 'i', 'n', 'm', 'w', 's', 'a',
                              'x', 'c', 'd', 'q', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'ESCAPE']

    def test_menu_keys(self):
        for char, field in self.menu_chars.items():
            pressed = [self.KeyEvent(char=char)]
            flags = self.input_handler.catch_and_process_input(GameStates.MENU, pressed)
            self.assertTrue(getattr(flags, field))

    def test_player_keys(self):
        for key in self.player_keys:
            if len(key) == 1:
                event = self.KeyEvent(char=key)
                field, expected = list(ACTIVE_CHARS.get(key).items())[0]
            else:
                event = self.KeyEvent(key=key)
                field, expected = list(ACTIVE_KEYS.get(key).items())[0]
            flags = self.input_handler.catch_and_process_input(GameStates.PLAYER_TURN, [event])
            self.assertEqual(expected, getattr(flags, field))
