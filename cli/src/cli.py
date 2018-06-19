"""
The main CLI class with the infinite loop.
"""
from src.parser import Parser, ParserException
from src.lexer import Lexer, LexerException
from src.commands import *
from src.environment import Environment
import sys


class Cli:
    """
    The main CLI class.
    Need to create an instance and call method run().

    cli = Cli()
    cli.run()
    """
    def __init__(self):
        """
        The class needs:
        the Environment instance for storing variables,
        the Parser and Lexer instances for parsing and lexing the input.
        """
        self.__env = Environment()
        self.__parser = Parser(self.__env)
        self.__lexer = Lexer()

    def process_input(self, input):
        """
        Method for processing input string:
        lexing, parsing and running the resultant.

        :param input: The input string.
        :return: The CommandResult instance with result of command execution.
        """
        lexems = self.__lexer.get_lexemes(input)
        command = self.__parser.build_command(lexems)
        result = None
        if command:
            result = command.run(Stream(), self.__env)
            self.__env = result.get_env()
        return result

    def run(self):
        """
        The main method of Cli class with infinite loop.
        Take input, process it and print the result continuously
        till ExitException, EOFError or Exception are raising.
        """
        running = True
        print('>\t\tHello! This is a shell imitator.')
        while running:
            try:
                input_string = input('> ')
                if input_string:
                    result = self.process_input(input_string)
                    if result:
                        output = result.get_output()
                        if output:
                            print(output, end='')
                        return_value = result.return_value()
                    if return_value:
                        print('Process exited with error code {}'.
                              format(return_value))
            except ParserException as ex:
                print('Parsing exception:\n{}'.format(str(ex)))
            except LexerException as ex:
                print('Lexing exception:\n{}'.format(str(ex)))
            except ExitException:
                running = False
            except EOFError:
                running = False
            except Exception:
                print('Something wrong, sorry.')
                return

        print('Good bye.')
