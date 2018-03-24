"""
The Parser class that parse list of lexemes and build a tree of commands.
It also uses the static Preprocessor class for variables substitution.
"""
from src.lexer import *
from src.commands import *
from src.preprocessor import *


class Parser:
    """
    The Parser class that takes list lexemes
    from Lexer and makes the commands tree from it.
    """
    def __init__(self, environment):
        """
        Takes the current environment.
        :param environment: the Environment instance with variables.
        """
        self.__env = environment

    def build_command(self, list_of_lexems):
        """
        Takes lexemes and builds the commands tree
        while the current index is not the last.
        :param list_of_lexems: list of Lexemes.
        :return: the root of the Command tree.
        """
        self.__list_lexems = list_of_lexems
        self.__cur_ix = 0
        self.__last_ix = len(list_of_lexems)
        self.__commands = []

        while self.__cur_ix < self.__last_ix:
            command = self.__get_command(self.__cur_ix)
            if command:
                self.__commands.append(command)
        return self.__commands[0]

    def __get_command(self, ix):
        """
        Parse the command from the given index.
        According to type of current Lexeme builds coherent command.
        :param ix: starts parsing command from this index (int).
        :return: the Command.
        """
        lexem = self.__list_lexems[ix]

        if lexem.type() == Lexeme_type.ASSIGNMENT:
            (name, value) = self.__parse_assignment(lexem)
            value = Preprocessor.substitute_vars(value, self.__env)
            self.__cur_ix += 1
            return CommandASSIGNMENT(name, value)

        if lexem.type() == Lexeme_type.VAR:
            self.__cur_ix += 1
            value = Preprocessor.substitute_vars(lexem.value(), self.__env)
            runnable_value = Lexer().get_lexemes(value)
            if runnable_value:
                command_name = runnable_value[0].value()
            else:
                raise ParserException('Unexpected token: {}.'.format(lexem.value()))
            args = self.__parse_args(self.__cur_ix)
            command = self.__make_certain_command(command_name, args)
            if command:
                result = command.run(Stream(), self.__env)
                result_value = result.get_output()
                return self.__make_certain_command('echo', [result_value])

        if lexem.type() == Lexeme_type.STRING:
            self.__cur_ix += 1
            args = self.__parse_args(self.__cur_ix)
            value = lexem.value()
            if lexem.type() == Lexeme_type.STRING:
                value = Preprocessor.substitute_vars(lexem.value(), self.__env)
            return self.__make_certain_command(value, args)

        if lexem.type() == Lexeme_type.PIPE:
            self.__cur_ix += 1
            if self.__commands:
                left_cmd = self.__commands.pop()
            else:
                raise ParserException('Syntax error near unexpected token {}'.
                                      format(lexem.value()))
            right_cmd = self.__get_command(self.__cur_ix)
            return CommandPIPE(left_cmd, right_cmd)
        else:
            raise ParserException('Syntax error near unexpected token {}'.
                                  format(lexem.value()))

    def __parse_assignment(self, lexem):
        """
        Parses the variable name and value of the value of the given
        lexeme value. Splits the input string by the first symbol '='.
        The lift part is the name of the variable, the right is the value.
        Raises the ParserException if some part is empty.
        :param lexem: the value of Lexeme with ASSIGNMENT type (string).
        :return: pair of name and value of the variable.
        """
        ix = lexem.value().find('=')
        name, value = lexem.value()[0:ix], lexem.value()[ix + 1:]
        if not value:
            raise ParserException('Variable {} has no value.'.format(name))
        elif not name:
            raise ParserException('Unattached definition {}.'.format(value))
        return (name, value)

    def __parse_args(self, ix):
        """
        Collects arguments for command on position ix till
        the current index is the last or the PIPE Lexeme appears.
        :param ix: the index of command (int).
        :return: the list of arguments.
        """
        self.__cur_ix += 1
        args = []
        if ix >= self.__last_ix:
            return args
        lexem = self.__list_lexems[ix]
        while ix < len(self.__list_lexems) and \
                self.__list_lexems[ix].type() is not Lexeme_type.PIPE:
            value = lexem.value()
            lexem_type = self.__list_lexems[ix].type()
            if lexem_type in \
                    [Lexeme_type.VAR, Lexeme_type.STRING, Lexeme_type.STRING_WITH_QUOTES]:
                value = self.__list_lexems[ix].value()
                value = Preprocessor.substitute_vars(value, self.__env)
            args.append(value)
            ix += 1
        self.__cur_ix = ix
        return args

    def __make_certain_command(self, name, args):
        """
        The very simple prototype of the command fabric.
        :param name: the name of the command (string).
        :param args: the list of arguments.
        :return: Certain command with the given name and rhe given arguments.
        """
        self.commands = ['cat', 'echo', 'exit', 'pwd', 'wc', 'grep']
        if name in self.commands:
            if name == 'wc':
                return CommandWC(args)
            if name == 'cat':
                return CommandCAT(args)
            if name == 'echo':
                return CommandECHO(args)
            if name == 'pwd':
                return CommandPWD(args)
            if name == 'exit':
                return CommandEXIT(args)
            if name == 'grep':
                return CommandGREP(args)
        return UnknownCommand(name, args)