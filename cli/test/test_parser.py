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
        self.exseptions_lexemes = [Lexeme('|', Lexeme_type.PIPE),
                               Lexeme('m=', Lexeme_type.ASSIGNMENT),
                               Lexeme('|', Lexeme_type.PIPE)]

    def test_echo(self):
        lexems = [Lexeme('$echo', Lexeme_type.VAR),
                  Lexeme('\'word\'', Lexeme_type.STRING_WITH_QUOTES),
                  Lexeme('\"word$x\"', Lexeme_type.STRING_WITH_QUOTES)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandECHO, type(command))

    def test_wc(self):
        lexems = [Lexeme('wc', Lexeme_type.STRING),
                  Lexeme('test1.txt', Lexeme_type.STRING_WITH_QUOTES),
                  Lexeme('test2.txt', Lexeme_type.STRING_WITH_QUOTES),
                  Lexeme('test3.txt', Lexeme_type.STRING_WITH_QUOTES)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandWC, type(command))

    def test_cat(self):
        lexems = [Lexeme('cat', Lexeme_type.STRING),
                  Lexeme('test.txt', Lexeme_type.STRING)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandCAT, type(command))

    def test_pwd(self):
        lexems = [Lexeme('pwd', Lexeme_type.STRING),
                  Lexeme('$t$x', Lexeme_type.VAR)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandPWD, type(command))

    def test_var(self):
        lexems = [Lexeme('$e', Lexeme_type.VAR)]
        self.assertRaises(ExitException, self.parser.build_command, lexems)

    def test_assignment(self):
        lexems = [Lexeme('m=$echo', Lexeme_type.ASSIGNMENT)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandASSIGNMENT, type(command))

    def test_unknown(self):
        lexems = [Lexeme('ls', Lexeme_type.STRING),
                  Lexeme('-la', Lexeme_type.STRING)]
        command = self.parser.build_command(lexems)
        self.assertEqual(UnknownCommand, type(command))

    def test_echo_pipe_cat(self):
        lexems = [Lexeme('$echo', Lexeme_type.VAR),
                  Lexeme('\"t\"', Lexeme_type.STRING_WITH_QUOTES),
                  Lexeme('|', Lexeme_type.PIPE),
                  Lexeme('cat', Lexeme_type.STRING)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandPIPE, type(command))

    def test_echo_pipe_cat_pipe_pwd(self):
        lexems = [Lexeme('$echo', Lexeme_type.VAR),
                  Lexeme('\"t\"', Lexeme_type.STRING_WITH_QUOTES),
                  Lexeme('|', Lexeme_type.PIPE),
                  Lexeme('cat', Lexeme_type.STRING),
                  Lexeme('test_text.txt', Lexeme_type.STRING),
                  Lexeme('|', Lexeme_type.PIPE),
                  Lexeme('pwd', Lexeme_type.STRING)]
        command = self.parser.build_command(lexems)
        self.assertEqual(CommandPIPE, type(command))

    def test_exception_start_with_pipe(self):
        self.assertRaises(ParserException,
                          self.parser.build_command, self.exseptions_lexemes)

    def test_exception_assignment_without_value(self):
        self.assertRaises(ParserException,
                          self.parser.build_command, self.exseptions_lexemes[1:])

    def test_exception_ends_with_pipe(self):
        self.assertRaises(ParserException,
                          self.parser.build_command, self.exseptions_lexemes[1:2])

    def test_exception_bad_assignment(self):
        self.assertRaises(ParserException,
                          self.parser.build_command, [Lexeme('$a=10', Lexeme_type.VAR)])