import unittest
from src.lexer import *
from src.lexer import LexerException


class TestLexer(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()

    def test_var(self):
        lexemes = self.lexer.get_lexemes('$a $a_a $v_2')
        self.assertEqual(len(lexemes), 3)
        for lexem in lexemes:
            self.assertEqual(lexem.type(), Lexeme_type.VAR)
        self.assertEqual('$a', lexemes[0].value())
        self.assertEqual('$a_a', lexemes[1].value())
        self.assertEqual('$v_2', lexemes[2].value())

    def test_string_with_quotes(self):
        lexems = self.lexer.get_lexemes(
            '\'text\' \"text 7    with space\" \'text\'\'text\' \'k\'ek')
        self.assertEqual(4, len(lexems))
        for lexem in lexems[:-1]:
            self.assertEqual(Lexeme_type.STRING_WITH_QUOTES, lexem.type())
        self.assertEqual('\'text\'', lexems[0].value())
        self.assertEqual('\"text 7    with space\"', lexems[1].value())
        self.assertEqual('\'text\'\'text\'', lexems[2].value())
        self.assertEqual('\'k\'ek', lexems[3].value())

    def test_exception(self):
        self.assertRaises(LexerException, self.lexer.get_lexemes, '\'kek')

    def test_string(self):
        lexems = self.lexer.get_lexemes('echo 123 test.txt val$val some_name')
        self.assertEqual(5, len(lexems))
        for lexem in lexems:
            self.assertEqual(Lexeme_type.STRING, lexem.type())
        self.assertEqual('echo', lexems[0].value())
        self.assertEqual('123', lexems[1].value())
        self.assertEqual('test.txt', lexems[2].value())
        self.assertEqual('val$val', lexems[3].value())
        self.assertEqual('some_name', lexems[4].value())

    def test_assignment(self):
        lexems = self.lexer.get_lexemes('a=12 b=$a')
        self.assertEqual(2, len(lexems))
        for lexem in lexems:
            self.assertEqual(Lexeme_type.ASSIGNMENT, lexem.type())
        self.assertEqual('a=12', lexems[0].value())
        self.assertEqual('b=$a', lexems[1].value())

    def test_pipe(self):
        lexems = self.lexer.get_lexemes('|')
        self.assertEqual(Lexeme_type.PIPE, lexems[0].type())
        lexems = self.lexer.get_lexemes('echo cat | cat')
        self.assertEqual(4, len(lexems))
        for i in [0, 1, 3]:
            self.assertEqual(Lexeme_type.STRING, lexems[i].type())
        self.assertEqual('echo', lexems[0].value())
        self.assertEqual('cat', lexems[1].value())
        self.assertEqual('cat', lexems[3].value())
        self.assertEqual('|', lexems[2].value())
        self.assertEqual(Lexeme_type.PIPE, lexems[2].type())

    def test_all(self):
        lexems = self.lexer.get_lexemes(
            'echo \'word\' | cat \"text 7\" | a=10 | $var_1')
        self.assertEqual(9, len(lexems))
        for i in [0, 3]:
            self.assertEqual(Lexeme_type.STRING, lexems[i].type())
        self.assertEqual('echo', lexems[0].value())
        self.assertEqual('cat', lexems[3].value())
        for i in [1, 4]:
            self.assertEqual(Lexeme_type.STRING_WITH_QUOTES, lexems[i].type())
        self.assertEqual('\'word\'', lexems[1].value())
        self.assertEqual('\"text 7\"', lexems[4].value())
        for i in [2, 5, 7]:
            self.assertEqual(Lexeme_type.PIPE, lexems[i].type())
            self.assertEqual('|', lexems[i].value())
        self.assertEqual(Lexeme_type.ASSIGNMENT, lexems[6].type())
        self.assertEqual(Lexeme_type.VAR, lexems[8].type())
        self.assertEqual('a=10', lexems[6].value())
        self.assertEqual('$var_1', lexems[8].value())

    def test_single_quotes_in_single_quotes(self):
        lexems = self.lexer.get_lexemes('echo \'aaa\'aa\'aaa\'')
        self.assertEqual(2, len(lexems))
        self.assertEqual(Lexeme_type.STRING, lexems[0].type())
        self.assertEqual('echo', lexems[0].value())
        self.assertEqual(Lexeme_type.STRING_WITH_QUOTES, lexems[1].type())
        self.assertEqual('\'aaa\'aa\'aaa\'', lexems[1].value())

    def test_one_single_quote_in_text(self):
        lexems = self.lexer.get_lexemes('aaa\'aa')
        self.assertEqual(1, len(lexems))
        self.assertEqual('aaa\'aa', lexems[0].value())
        self.assertEqual(Lexeme_type.STRING, lexems[0].type())
