import unittest
from src.iostreams import *
import os


class TestStream(unittest.TestCase):

    def test_write_get_value(self):
        test_obj = Stream()
        test_obj.write('kek')
        test_obj.write(' ')
        test_obj.write_line('kek')
        self.assertEqual('kek kek{}'.format(os.linesep), test_obj.get_value())
