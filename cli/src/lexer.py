"""
A module contains Lexer class that
split the input string into lexems
which are word or collocation with
certain meaning and option.
"""

from enum import Enum


class Lexem_type(Enum):
    """
    Types of lexems:

    VAR - string that starts the '$' symbol;
    STRING_WITH_QUOTES - string with single or double quotes around;
    STRING - single word or sequence of symbols without spaces;
    PIPE - "|" symbol;
    ASSIGNMENT - the expression with '=' symbol.
    """
    VAR = 1
    STRING_WITH_QUOTES = 2
    STRING = 3
    ASSIGNMENT = 4
    PIPE = 5


class LexerException(Exception):
    """An exception raising while lexing. """
    pass


class Lexem:
    """ The abstract of lexem, that contains the value and type."""

    def __init__(self, value, type):
        self.__type = type
        self.__value = value

    def value(self):
        return self.__value

    def type(self):
        return self.__type


class Lexer:
    """
    The lexer class for lexing the input string.
    It split the input into lexems.
    """

    # @staticmethod
    def get_lexemes(self, str):
        self.__input = str
        self.__cur_ix = 0
        self.__last_ix = len(str)
        self.__list_lexems = []

        while self.__cur_ix < self.__last_ix:
            while self.__input[self.__cur_ix] is ' ':
                self.__cur_ix = self.__next_symbol()
            self.__list_lexems.append(self.__get_lexem())
            self.__cur_ix = self.__next_symbol()

        return self.__list_lexems

    def __get_lexem(self):

        ix = self.__cur_ix

        if self.__input[ix] is '|':
            lexem = Lexem('|', Lexem_type.PIPE)
            self.__cur_ix = self.__next_symbol()

        elif self.__input[ix] in ('\"' , '\''):
            quote = self.__input[ix]
            ix = self.__next_symbol(quote, self.__cur_ix + 1)
            if ix >= self.__last_ix:
                raise LexerException('Missing second quote for fist one '
                                     'at position {}.'.format(self.__cur_ix))
            ix += 1
            lexem = Lexem(self.__input[self.__cur_ix:ix], Lexem_type.STRING_WITH_QUOTES)
            self.__cur_ix = ix

        elif self.__input[ix] is '$':
            ix = self.__next_symbol(' ', self.__cur_ix)
            lexem_value = self.__input[self.__cur_ix:ix]
            self.__cur_ix = ix
            lexem = Lexem(lexem_value, Lexem_type.VAR)

        else:
            lexem_type = Lexem_type.STRING
            ix = self.__next_symbol(' ', self.__cur_ix)
            lexem_value = self.__input[self.__cur_ix:ix]
            eq_symb_ix = lexem_value.find('=')
            if eq_symb_ix is not -1:
                lexem_type = Lexem_type.ASSIGNMENT
            self.__cur_ix = ix
            lexem = Lexem(lexem_value, lexem_type )

        return lexem

    def __next_symbol(self,symbol=None,ix=None):
        if symbol is not None:
            d_ix = (self.__input[ix:]).find(symbol)
            if d_ix is -1:
                return self.__last_ix
            return ix + d_ix

        else:
            if self.__cur_ix + 1 > self.__last_ix:
                return self.__last_ix + 1
            return self.__cur_ix + 1
