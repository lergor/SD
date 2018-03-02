
from src.parser import Parser, ParserException
from src.lexer import Lexer, LexerException
from src.commands import *
from src.environment import Environment
import os


class Cli:
    """
    The main Cli class. Need to create an instance and call method run().
    """
    def __init__(self):
        self.__env = Environment()
        self.__parser = Parser(self.__env)
        self.__lexer = Lexer()


    def __process_input(self, input):
        lexems = self.__lexer.get_lexemes(input)
        command = self.__parser.build_command(lexems)
        result = None
        if command and len(command) == 1:
            result = command[0].run(InputStream(), self.__env)
            self.__env = result.get_env()
        return result


    def run(self):
        """The main method of Cli class with infinite loop."""
        running = True
        print('>\t\tHello! This is a shell imitator.')
        while running:
            input_string = input('> ')
            if input_string is 'exit':
                running = False
            try:
                return_value = 0
                result = self.__process_input(input_string)
                if result:
                    print(result.get_output())

                    return_value = result.return_value()

                if return_value:
                    print('Process exited with error code {}'.format(return_value))
            except ParserException as ex:
                print('Parsing exception:\n{}'.format(str(ex)))
            except LexerException as ex:
                print('Lexing exception:\n{}'.format(str(ex)))
            except ExitException:
                running = False
            except Exception:
                running = False

        print('Good bye.')