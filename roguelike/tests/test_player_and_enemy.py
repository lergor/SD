import unittest
from src.input_handler import InputHandler
from src.game_objects.entity import EntityFactory
from src.game_objects.obj_keeper import ObjectsKeeper
from src.utils import GameStates


class TestPlayerAndEnemy(unittest.TestCase):

    class KeyEvent:
        def __init__(self, char=None, key=None):
            self.char = char
            self.key = key
            self.type = 'KEYDOWN'

    def setUp(self):
        self.input_handler = InputHandler()
        self.obj_keeper = ObjectsKeeper()
        self.obj_keeper.init_objects()
        self.player = self.obj_keeper.player
        self.pressed = [self.KeyEvent(key='RIGHT')]

    def test_player_move_by_keys(self):
        flags = self.input_handler.catch_and_process_input(GameStates.PLAYER_TURN, self.pressed)
        self.assertIsNotNone(flags.move)
        previous_x, previous_y = self.player.x, self.player.y
        dx, dy = flags.move
        expected_x, expected_y = previous_x + dx, previous_y + dy
        self.obj_keeper.player_move(flags.move)
        self.assertEqual(expected_x, self.player.x)
        self.assertEqual(expected_y, self.player.y)

    def test_enemy_move_towards(self):
        enemy = EntityFactory.create_entity('Spider', self.player.x + 4, self.player.y)
        self.obj_keeper.map.fov[enemy.x, enemy.y] = True
        previous_distance = enemy.distance_to(self.player)
        enemy.ai.take_turn(self.player, self.obj_keeper)
        self.assertTrue(enemy.distance_to(self.player) < previous_distance)

    def test_enemy_attacks(self):
        enemy = EntityFactory.create_entity('Spider', self.player.x + 1, self.player.y)
        self.obj_keeper.map.fov[enemy.x, enemy.y] = True
        previous_distance = enemy.distance_to(self.player)
        previous_player_hp = self.player.fighter.hp
        enemy.ai.take_turn(self.player, self.obj_keeper)
        self.assertEqual(enemy.distance_to(self.player), previous_distance)
        self.assertTrue(self.player.fighter.xp < previous_player_hp)

    def test_player_attacks(self):
        flags = self.input_handler.catch_and_process_input(GameStates.PLAYER_TURN, self.pressed)
        self.assertIsNotNone(flags.move)
        enemy = EntityFactory.create_entity('Spider', self.player.x + 1, self.player.y)
        self.obj_keeper.map.fov[enemy.x, enemy.y] = True
        self.obj_keeper.entities.append(enemy)
        previous_distance = self.player.distance_to(enemy)
        previous_enemy_hp = enemy.fighter.hp
        self.obj_keeper.player_move(flags.move)
        self.assertEqual(enemy.distance_to(self.player), previous_distance)
        self.assertTrue(enemy.fighter.hp < previous_enemy_hp)
