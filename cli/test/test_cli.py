import unittest
from src.cli import *


class testCli(unittest.TestCase):

    def setUp(self):
        self.cli = Cli()

    def test_commands(self):
        result = self.cli.process_input('echo \'Hello, World!\'')
        self.assertEqual('Hello, World!' + os.linesep, result.get_output())
        result = self.cli.process_input('echo \'Hello, World!\' | cat')
        self.assertEqual('Hello, World!' + os.linesep, result.get_output())

        self.cli.process_input('FILE=test_text.txt')
        result = self.cli.process_input('cat $FILE test_env.py | wc')
        result = (result.get_output()).split()
        right_result = ['31', '110', '906']
        self.assertEqual(len(right_result), len(result))
        for i in range(len(result)):
            self.assertEqual(right_result[i], result[i])
        result = self.cli.process_input('pwd')
        self.assertEqual(os.getcwd() + os.linesep, result.get_output())

    def test_cat_pipe_grep(self):
        result = self.cli.process_input('cat ../Readme.md | grep cat')
        self.assertEqual('  - \x1b[1;31mcat\x1b[0m;' + os.linesep, result.get_output())

    def test_grep_from_file(self):
        result = self.cli.process_input('grep cat ../Readme.md')
        self.assertEqual('  - \x1b[1;31mcat\x1b[0m;' + os.linesep, result.get_output())

    def test_grep_fail_without_num(self):
        result = self.cli.process_input('grep -A cat ../Readme.md')
        self.assertEqual('The NUM argument is required.' + os.linesep, result.get_output())

    def test_exceptions(self):
        self.cli.process_input('x=exit')
        self.assertRaises(ExitException,
                          self.cli.process_input, '$x')
        self.assertRaises(LexerException,
                          self.cli.process_input, '\'x')
        self.assertRaises(ParserException,
                          self.cli.process_input, 'x\"')
