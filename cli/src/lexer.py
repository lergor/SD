"""
A module contains Lexer class that split the input string into lexemes
which are word or collocation with certain meaning and option.
"""

from enum import Enum


class Lexeme_type(Enum):
    """
    Types of lexemes:

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
    """An exception raising while lexing."""
    pass


class Lexeme:
    """
    The abstraction of lexeme,
     that contains the value and type of single lexeme."""

    def __init__(self, value, tp):
        """
        Takes the lexeme value and type.
        :param value: the lexeme value (string).
        :param tp: the lexeme type (Lexeme_type).
        """
        self.__type = tp
        self.__value = value

    def value(self):
        """Returns the lexeme value."""
        return self.__value

    def type(self):
        """Returns the lexeme type."""
        return self.__type


class Lexer:
    """
    The Lexer class for lexing the input string.
    Splits the input into list of lexemes.
    """
    def get_lexemes(self, str):
        """
        Takes the input string,
        splits in by spaces into words
        and gives thew the type.
        :param str: the input string.
        :return: list of Lexemes.
        """
        self.__input = str
        self.__cur_ix = 0
        self.__last_ix = len(str)
        self.__list_lexems = []

        while self.__cur_ix < self.__last_ix:
            while self.__input[self.__cur_ix] is ' ':
                self.__cur_ix = self.__next_idx()
            self.__list_lexems.append(self.__get_lexem())
            self.__cur_ix = self.__next_idx()
        return self.__list_lexems

    def __get_lexem(self):
        """
        Takes the next lexeme from current index.
        :return: the next Lexeme.
        """
        ix = self.__cur_ix

        if self.__input[ix] is '|':
            lexem_value = '|'
            lexem_type = Lexeme_type.PIPE
            self.__cur_ix = self.__next_idx()

        elif self.__input[ix] in ('\"', '\''):
            quote = self.__input[ix]
            ix = self.__next_idx(quote, self.__cur_ix + 1)
            if ix >= self.__last_ix:
                raise LexerException('Missing second quote for fist one '
                                     'at position {}.'.format(self.__cur_ix))
            lexem_value = self.__input[self.__cur_ix:ix+1]
            self.__cur_ix = ix + 1
            if self.__cur_ix < self.__last_ix - 1 and \
                    ((self.__input[self.__cur_ix]).isalpha() or
                      self.__input[self.__cur_ix] in ['\'', '\"']):
                following_text = self.__get_lexem().value()
                lexem_value += following_text
            lexem_type = Lexeme_type.STRING_WITH_QUOTES

        elif self.__input[ix] is '$':
            lexem_type = Lexeme_type.VAR
            ix = self.__next_idx(' ', self.__cur_ix)
            lexem_value = self.__input[self.__cur_ix:ix]
            self.__cur_ix = ix

        else:
            lexem_type = Lexeme_type.STRING
            ix = self.__next_idx(' ', self.__cur_ix)
            lexem_value = self.__input[self.__cur_ix:ix]
            eq_symb_ix = lexem_value.find('=')
            if eq_symb_ix is not -1:
                lexem_type = Lexeme_type.ASSIGNMENT
            self.__cur_ix = ix
        return Lexeme(lexem_value, lexem_type)

    def __next_idx(self, symbol=None, ix=None):
        """
        Returns the index or the last index if it is the end of string.
        If the symbol and index are given returns the next index
        of the given symbol from the given index.
        """
        if symbol is not None:
            d_ix = (self.__input[ix:]).find(symbol)
            if d_ix is -1:
                return self.__last_ix
            return ix + d_ix
        else:
            if self.__cur_ix + 1 > self.__last_ix:
                return self.__last_ix + 1
            return self.__cur_ix + 1
