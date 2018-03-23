import unittest
from src.parser import *
from src.commands import *
from src.lexer import *
from src.environment import Environment


class TestParser(unittest.TestCase):

    def setUp(self):
        self.env = Environment()
        self.env.set_var_value('x', '10')
        self.env.set_var_value('t', 'text')
        self.env.set_var_value('e', 'exit')
        self.env.set_var_value('echo', 'echo')
        self.env.set_var_value('p', 'pwd')
        self.parser = Parser(self.env)

    def test_single_command(self):
        lexems = [Lexeme('$echo', Lexeme_type.VAR),
                  Lexeme('\'word\'', Lexeme_type.STRING_WITH_QUOTES),
                  Lexeme('\"word$x\"', Lexeme_type.STRING_WITH_QUOTES)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandECHO, type(command))

        lexems = [Lexeme('wc', Lexeme_type.STRING),
                  Lexeme('test1.txt', Lexeme_type.STRING_WITH_QUOTES),
                  Lexeme('test2.txt', Lexeme_type.STRING_WITH_QUOTES),
                  Lexeme('test3.txt', Lexeme_type.STRING_WITH_QUOTES)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandWC, type(command))

        lexems = [Lexeme('cat', Lexeme_type.STRING),
                  Lexeme('test.txt', Lexeme_type.STRING)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandCAT, type(command))

        lexems = [Lexeme('pwd', Lexeme_type.STRING),
                  Lexeme('$t$x', Lexeme_type.VAR)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandPWD, type(command))

        lexems = [Lexeme('$e', Lexeme_type.VAR)]
        self.assertRaises(ExitException, self.parser.build_command, lexems)

        lexems = [Lexeme('m=$echo', Lexeme_type.ASSIGNMENT)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandASSIGNMENT, type(command))

        lexems = [Lexeme('ls', Lexeme_type.STRING),
                  Lexeme('-la', Lexeme_type.STRING)]
        command = self.parser.build_command(lexems)
        self.assertEqual(UnknownCommand, type(command))

    def test_pipe(self):
        lexems = [Lexeme('$echo', Lexeme_type.VAR),
                  Lexeme('\"t\"', Lexeme_type.STRING_WITH_QUOTES),
                  Lexeme('|', Lexeme_type.PIPE),
                  Lexeme('cat', Lexeme_type.STRING)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandPIPE, type(command))

        lexems = [Lexeme('$echo', Lexeme_type.VAR),
                  Lexeme('\"t\"', Lexeme_type.STRING_WITH_QUOTES),
                  Lexeme('|', Lexeme_type.PIPE),
                  Lexeme('cat', Lexeme_type.STRING),
                  Lexeme('test_text.txt', Lexeme_type.STRING),
                  Lexeme('|', Lexeme_type.PIPE),
                  Lexeme('pwd', Lexeme_type.STRING)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandPIPE, type(command))

    def test_exception(self):
        lexems = [Lexeme('|', Lexeme_type.PIPE),
                  Lexeme('m=', Lexeme_type.ASSIGNMENT),
                  Lexeme('|', Lexeme_type.PIPE)]
        self.assertRaises(ParserException,
                          self.parser.build_command, lexems)
        self.assertRaises(ParserException,
                          self.parser.build_command, lexems[1:])
        self.assertRaises(ParserException,
                          self.parser.build_command, lexems[1:2])
        self.assertRaises(ParserException,
                          self.parser.build_command, [Lexeme('$a=10', Lexeme_type.VAR)])