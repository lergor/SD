import unittest
from src.iostreams import *
from src.environment import Environment


class TestEnvironment(unittest.TestCase):

    def setUp(self):
        self.env = Environment()

    def test_env(self):
        tests = {'a': 1, 'b': 2, 'c': 3}
        for (name, value) in tests.items():
            self.env.set_var_value(name, value)
        for (name, value) in tests.items():
            self.assertEqual(value, self.env.get_var_value(name))
        self.assertEqual('', self.env.get_var_value('d'))

    def test_cwd(self):
        right_cwd = os.getcwd()
        self.assertEqual(right_cwd, self.env.get_cwd())
