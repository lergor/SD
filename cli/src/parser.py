
from src.lexer import *
from src.commands import *

class ParserException(Exception):
    """An exception raising while parsing. """
    pass


class Parser:
    """The Parser class that takes lexems from Lexer and make commands from it."""
    def __init__(self, environment):
        self.__env = environment

    def build_command(self, list_of_lexems):
        """The main method that returns a final command."""
        self.__list_lexems = list_of_lexems
        self.__cur_ix = 0
        self.__last_ix = len(list_of_lexems)
        self.__commands = []

        while self.__cur_ix < self.__last_ix:
            command = self.__get_command(self.__cur_ix)
            if command:
                self.__commands.append(command)

        return  self.__commands


    def __get_command(self, ix):
        lexem = self.__list_lexems[ix]

        if lexem.type() == Lexem_type.ASSIGNMENT:
            (name, value) = self.__parse_assignment(lexem)
            self.__env.set_var_value(name,value)
            return None

        if lexem.type() == Lexem_type.VAR:
            pass

        if lexem.type() == Lexem_type.STRING:
            self.__cur_ix += 1
            return self.__parse_command(lexem)

        if lexem.type() == Lexem_type.PIPE:
            self.__cur_ix += 1
            if self.__commands:
                left_cmd = self.__commands.pop()
            else:
                raise ParserException('Syntax error near unexpected token {}'.format(lexem.value()))
            right_cmd = self.__get_command(self.__cur_ix)
            return CommandPipe(left_cmd, right_cmd)

        else:
            raise ParserException('Syntax error near unexpected token {}'.format(lexem.value()))


    def __parse_assignment(self, lexem):
        self.__cur_ix += 1
        [name, value] = lexem.value().split('=')
        if not value:
            raise ParserException('Variable {} has no value.'.format(name))
        elif not name:
            raise ParserException('Unattached definition {}.'.format(value))
        if value[0] is '$':
            value = self.__env.get_var_value(value[1:])
        return (name, value)

    def __parse_string(self, ix=None, lexem=None):
        if lexem:
            return lexem
        if ix:
            lexem = self.__list_lexems[ix].value()
        return lexem
        pass

    def __parse_string_with_quotes(self, ix):
        lexem = self.__list_lexems[ix].value()
        if lexem[0] is '\'':
            return lexem
        if lexem[0] is '\"':
            changed_lexem = self.__parse_string(lexem=lexem[1:-1])
            # return ('\"' + changed_lexem + '\"')
            return (changed_lexem)

    def __parse_var(self, lexem):
        variable = lexem.value()
        if variable[0] == '$':
            variable = variable[1:]
        return self.__env.get_var_value(variable)

    def __parse_pipe(self, lexem):
        pass

    def __reading_var_name(self, lexem):
        pass

    def __parse_command(self, lexem):
        args = []
        ix = self.__cur_ix

        while ix < len(self.__list_lexems) and self.__list_lexems[ix].type() is not Lexem_type.PIPE:
            value = lexem.value()
            if self.__list_lexems[ix].type() is Lexem_type.VAR:
                value = self.__parse_var(self.__list_lexems[ix])
            if self.__list_lexems[ix].type() is Lexem_type.STRING:
                value = self.__parse_string(lexem=self.__list_lexems[ix].value())
            if self.__list_lexems[ix].type() is Lexem_type.STRING_WITH_QUOTES:
                value = self.__parse_string_with_quotes(ix)
            args.append(value)
            ix += 1
        self.__cur_ix = ix
        name = lexem.value()
        if name in self.__env.commands:
            if name == 'cat':
                return CommandCAT(args)
            if name == 'echo':
                return CommandECHO(args)
            if name == 'pwd':
                return CommandPWD(args)
            if name == 'exit':
                return CommandEXIT(args)
        return UnknownCommand(name, args)
