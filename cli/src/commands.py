"""
The abstraction of commands and their results in the CLI.
All commands have method 'run', that takes input parameters
and the environment and returns the CommandResult instance.

Also contains ExitException that raises if command 'exit' was parsed.
"""
from abc import ABCMeta, abstractmethod
import sys
import subprocess
from src.iostreams import *
import argparse
import re


class ExitException(Exception):
    """An exception raising when command 'exit' runs."""
    pass


class CommandResult:
    """
    The CommandResult passes the information about
    the result of command.
    Contains the input, the environment and the return flag.
    """
    def __init__(self, output, env, return_value=0):
        """
        :param output: the Stream instance with command result.
        :param env: the Environment instance with variables.
        :param return_value: return flag (int):
        0 - process exited successfully
        1 - otherwise
        """
        self.__output = output
        self.__env = env
        self.__return_value = return_value

    def return_value(self):
        """Returns the flag returned by command."""
        return self.__return_value

    def get_output(self):
        """Returns the output of command execution."""
        return self.__output.get_value()

    def get_env(self):
        """Returns the changed (or not) environment."""
        return self.__env


class Command(metaclass=ABCMeta):
    """
    The common class for all commands.
    Contains method 'run' that starts executions.
    """
    @abstractmethod
    def run(self, input, env):
        return NotImplemented


class CommandPIPE(Command):
    """
    The abstract of PIPE that takes left command's output
    and redirect it to the right command as input stream.
    """
    def __init__(self, left, right):
        """
        Takes left and right commands.
        :param left: some Command located to the left from the pipe.
        :param right: some Command located to the right from the pipe.
        """
        self.__left_cmd = left
        self.__right_cmd = right

    def run(self, input, env):
        """
        Takes the input Stream and the environment,
        executes left command with them,
        takes its result Stream and new environment,
        executes the right command with them
        and return its result.
        :param input: the Stream instance with previous results.
        :param env: the Environment instance with variables.
        :return: the right command result (CommandResult instance).
        """
        result_of_left = self.__left_cmd.run(input, env)

        if result_of_left.return_value():
            return result_of_left

        changed_input = Stream()
        output = result_of_left.get_output()
        if output[-1] == os.linesep:
            output = output[0:-1]
        changed_input.write_line(output)
        changed_env = result_of_left.get_env()
        return self.__right_cmd.run(changed_input, changed_env)


class CommandCAT(Command):
    """
    The command 'cat' takes files and prints their content
    on the standard output. May has one and more arguments and
    even zero if placed on the right from PIPE.
    """
    def set_args(self, args):
        """
        Takes and sets arguments if they are given.
        :param args: list with file names.
        """
        self.__args = args

    def run(self, input, env):
        """
        Takes the input Stream and the environment, writes the content of files
        in the Stream and returns the result.
        :param input: the Stream instance with previous results.
        :param env: the Environment instance with variables.
        :return: the CommandResult instance with contents of arguments.
        """
        return_value = 0
        self.__output = Stream()
        num_of_args = len(self.__args)

        if not num_of_args:
            self.__output.write(input.get_value())
        else:
            for file in self.__args:
                file_path = os.path.join(env.get_cwd(), file)
                if not os.path.isfile(file_path):
                    self.__output.write_line('cat: {}: No such file or directory.'.
                                        format(file))
                    return_value = 1
                    break
                with open(file, 'r') as opened_file:
                    self.__output.write(opened_file.read())
        return CommandResult(self.__output, env, return_value)


class CommandPWD(Command):
    """
    The 'pwd' command prints name of current/working directory.
    """
    def set_args(self, args):
        """
        Takes and sets arguments if they are given.
        :param args: list of arguments.
        """
        self.__args = args

    def run(self, input, env):
        """
        Takes the input Stream and the environment
        and returns current directory.
        :param input: the Stream instance with previous results.
        :param env: the Environment instance with variables.
        :return: the CommandResult instance with current directory.
        """
        self.__output = Stream()
        return_value = 0
        if self.__args:
            self.__output.write_line('Wrong number of arguments for pwd command:'
                                ' expected 0, got {}.'.format(len(self.__args)))
            return_value = 1
            return CommandResult(self.__output, env, return_value)

        self.__output.write_line(env.get_cwd())
        return CommandResult(self.__output, env, return_value)


class CommandEXIT(Command):
    """
    The class of 'exit' command causes normal process termination.
    Raises ExitException that will be catched
    in the main loop of program in the Cli class.
    """
    def set_args(self, args):
        """
        Takes and sets arguments if they are given.
        :param args: list of arguments.
        """
        self.__args = args

    def run(self, input, env):
        """
        Just raises ExitException.
        :param input: the Stream instance with previous results.
        :param env: the Environment instance with variables.
        """
        raise ExitException('Bye!')


class CommandECHO(Command):
    """ The 'echo' command, displays a line of text that came as input."""
    def set_args(self, args=['']):
        """
        Takes and sets arguments if they are given.
        :param args: list of arguments.
        """
        self.__args = args

    def run(self, input, env):
        """
        Takes the input Stream and the environment and prints the arguments.
        :param input: the Stream instance with previous results.
        :param env: the Environment instance with variables.
        :return: the CommandResult instance with printed arguments.
        """
        output = Stream()
        output.write_line(' '.join(self.__args))
        return CommandResult(output, env, 0)


class CommandWC(Command):
    """
    The 'wc' prints newline, word, and byte counts for each file.
    """
    def set_args(self, args):
        """
        Takes and sets arguments if they are given.
        :param args: list of arguments.
        """
        self.__args = args

    def __count_lines_words_bytes(self, input):
        """
        Counts newlines, words and bytes for the input file.
        :param input: the name of file (string).
        :return: list with three counts.
        """
        lines = input.split(os.linesep)
        line_count = len(lines) - 1
        if len(lines) == 1:
            line_count = 1
        word_count = 0
        for line in lines:
            word_count += len(line.split())
        char_count = len(input.encode(sys.stdin.encoding))
        return [line_count, word_count, char_count]

    def run(self, input, env):
        """
        Takes the input Stream and the environment, counts newlines,
        words and bytes in each argument and returns the result.
        If more than one argument given also return total counts.
        :param input: the Stream instance with previous results.
        :param env: the Environment instance with variables.
        :return: the CommandResult instance with all counts.
        """
        self.__output = Stream()
        return_value = 0
        result = list()

        if not self.__args:
            result.append((' ',
                           self.__count_lines_words_bytes(input.get_value())))
        else:
            for file in self.__args:
                file_path = os.path.join(env.get_cwd(), file)
                if not os.path.isfile(file_path):
                    self.__output.write_line("wc: {}: No such file or directory.".
                                        format(file))
                    return_value = 1
                    break
                with open(file, 'r') as opened_file:
                    text = opened_file.read()
                    result.append((file, self.__count_lines_words_bytes(text)))

        if return_value is 0:
            total_lines = 0
            total_words = 0
            total_bytes = 0
            for (name, [line_count, word_count, byte_count]) in result:
                total_bytes += byte_count
                total_words += word_count
                total_lines += line_count
                if not len(self.__args) == 1:
                    self.__output.write_line('{:4d} {:4d} {:4d}    {}'.
                                         format(line_count, word_count, byte_count, name))
                else:
                    self.__output.write_line('{:4d} {:4d} {:4d}    {}'.
                                             format(line_count, word_count, byte_count, name))

            if len(self.__args) > 1:
                self.__output.write_line('{:4d} {:4d} {:4d}    {}'.
                                    format(total_lines, total_words, total_bytes, 'total'))
        return CommandResult(self.__output, env, return_value)


class UnknownCommand(Command):
    """
    Commands that are not in this implementation
    will be called from the standard shell.
    """
    def __init__(self, cmd, args):
        """
        Takes the command name and arguments if they are given.
        :param cmd: the command name (string).
        :param args: list of arguments.
        """
        self.__command = cmd
        self.__args = args

    def run(self, input, env):
        """
        Takes the input Stream and the environment and
        tries to call the command with given arguments from the standard shell.
        :param input: the Stream instance with previous results.
        :param env: the Environment instance with variables.
        :return: the CommandResult instance with results of the called process.
        """
        self.__output = Stream()
        args_list = [self.__command]
        args_list.extend(self.__args)

        try:
            process = subprocess.run(args_list,
                                     input=input.get_value(),
                                     stdout=subprocess.PIPE,
                                     encoding=sys.stdout.encoding)
            return_value = process.returncode
            self.__output.write(str(process.stdout))

        except Exception as err:
            self.__output.write_line('Command {}: command not found.'.
                                format(self.__command))
            return_value = 1

        return CommandResult(self.__output, env, return_value)


class CommandASSIGNMENT(Command):
    """
    Command that assigns value to variable, i.e. x=10.
    """
    def __init__(self, var_name, value):
        """
        Takes the variable's name and value.
        :param var_name: name of the variable (string).
        :param value: new value of the variable (string).
        """
        self.__var_name = var_name
        self.__value = value

    def run(self, input, env):
        """
        Takes the input Stream and the environment and
        puts the new value of the variable into the environment.
        :param input: the Stream instance with previous results.
        :param env: the Environment instance with variables.
        :return: the CommandResult instance with the changed environment.
        """
        self.__output = Stream()
        return_value = 0
        env.set_var_value(self.__var_name, self.__value)
        return CommandResult(input, env, return_value)


class CommandGREP(Command):
    """
    Prints lines matching a pattern. Available keys:
    -i, --ignore-case
              Ignore case distinctions, so that characters that differ only in
              case match each other.
    -w, --word-regexp
              Select  only  those  lines  containing  matches  that form whole
              words.
    -A NUM, --after-context=NUM
              Print  NUM  lines  of  trailing  context  after  matching lines.
    """
    def set_args(self, args):
        """
        Takes and sets arguments if they are given.
        :param args: list of arguments.
        """
        self.__args = args

    def run(self, input, env):
        """
        Takes the input Stream and the environment.

        :param input: the Stream instance with previous results.
        :param env: the Environment instance with variables.
        :return: the CommandResult instance with the changed environment.
        """
        self.__output = Stream()
        return_value = 0
        if (not input.get_value() and len(self.__args) <= 1) or (input.get_value() and len(self.__args) < 1):
            self.__output.write_line('Wrong number of arguments for grep command.')
            return CommandResult(self.__output, env, 1)
        as_str = ' '.join(self.__args)
        if re.search('-.*A', as_str)and not re.search('-.*A\s*[0-9]{1,}', as_str):
                self.__output.write_line('The NUM argument is required.')
                return CommandResult(self.__output, env, 1)
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--ignore-case', action='store_true',
                            help='Ignore case distinctions, so that characters'
                                 ' that differ only in case match each other.')
        parser.add_argument('-w', '--word-regexp', action='store_true',
                            help='Select  only  those  lines  containing '
                                 'matches that form whole words.')
        parser.add_argument('-A', '--after-context', metavar='NUM', type=int,
                            help='Increase output verbosity.')
        parser.add_argument('pattern', type=str, metavar='PATTERN')
        if not input.get_value():
            parser.add_argument('file', metavar='FILE',
                                type=str, nargs='+')
        try:
            args = parser.parse_args(self.__args)
        except argparse.ArgumentError as ae:
            msg = 'ArgumentError while \'grep\' running.'
            self.__output.write_line(msg)
            return_value = 1
        except argparse.ArgumentTypeError as ate:
            msg = 'ArgumentTypeError while \'grep\' running.'
            self.__output.write_line(msg)
            return_value = 1
        except Exception as ex:
            msg = 'Exception {} while \'grep\' running.'.format(str(type(ex)))
            self.__output.write_line(msg)
            return_value = 0

        if return_value != 0:
            return CommandResult(self.__output, env, return_value)
        self.__args = args
        pattern = args.pattern
        if args.word_regexp:
            pattern = '{} '.format(pattern)
        if args.ignore_case:
            self.__pattern = re.compile(pattern, re.IGNORECASE)
        else:
            self.__pattern = re.compile(pattern)
        if not input.get_value():
            if not args.file:
                self.__output.write_line('grep: no argument FILE.')
                return CommandResult(self.__output, env, 1)
            for file in args.file:
                file_path = os.path.join(env.get_cwd(), file)
                if not os.path.isfile(file_path):
                    self.__output.write_line('grep: {}: No such file or directory.'.
                                             format(file))
                    return CommandResult(self.__output, env, 1)

                with open(file, 'r') as f:
                    self.__result = ''
                    self.__i = 0
                    lines = f.readlines()
                    self.__lines_after = None
                    for line in lines:
                        self.process_string(line, len(lines))

        else:
            lines = input.get_value().split(os.linesep)
            self.__result = ''
            self.__i = 0
            self.__lines_after = None
            for line in lines:
                self.process_string(line, len(lines))
            self.__output.write_line('')
        return CommandResult(self.__output, env, return_value)

    def process_string(self, line, length_lines):
        """
        Searches the pattern the given string.
        :param line: the string where pattern is searching.
        :param length_lines: length of all lines to check if the given is the last.
        """
        self.__i += 1
        result_line = ''
        self.__ix = 0
        while True:
            string = line[self.__ix:]
            matched = self.__pattern.search(string)
            if not matched:
                break
            else:
                self.__lines_after = self.__args.after_context
                self.__ix += matched.end()
                if self.__args.word_regexp:
                    self.__ix -= 1
                result_line += string[:matched.start()]
                finded = matched.group()
                if self.__args.word_regexp:
                    finded = finded[:-1]
                    if not line[matched.start() - 1].isspace():
                        self.__result += finded
                        continue
                result_line += '\x1b[1;31m{}\x1b[0m'.format(finded)
        if result_line:
            result_line += line[self.__ix:]
            self.__result += result_line
            if self.__lines_after:
                self.__lines_after = self.__args.after_context
        else:
            if self.__lines_after and self.__lines_after > 0:
                self.__lines_after -= 1
                self.__result += line
                if self.__lines_after == 0 and self.__i < length_lines:
                    self.__result += '\x1b[0;34m---\x1b[0m' + os.linesep
        self.__output.write(self.__result)
        self.__result = ''
