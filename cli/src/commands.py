
from abc import ABCMeta
from abc import abstractmethod
import sys
import subprocess
from src.iostreams import *


class ExitException(Exception):
    """An exception raising when command 'exit' runs."""
    pass


class CommandResult:
    """
    The CommandResult passes the information about
    the result of command.
    Contains the input, the environment and the return flag.
    """
    def __init__(self, input, env, return_value=0):
        self.__input = input
        self.__env = env
        self.__return_value = return_value

    def return_value(self):
        """Returns the flag returned by command."""
        return self.__return_value

    def get_output(self):
        """Returns the output of command execution."""
        return self.__input.get_value()

    def get_env(self):
        """Returns the probably changed environment."""
        return self.__env


class Command(metaclass=ABCMeta):
    """
    The common class for all commands.
    Contains method 'run' that let start executions.
    """
    @abstractmethod
    def run(self, input, env):
        return NotImplemented


class CommandPipe(Command):
    """
    The abstract of PIPE that takes left command's output
    and redirect it to the right command as input stream.
    """
    def __init__(self, left, right):
        self.__left_cmd = left
        self.__right_cmd = right

    def run(self, input, env):
        result_of_left = self.__left_cmd.run(input, env)

        if result_of_left.return_value():
            return result_of_left

        changed_input = result_of_left.get_output()
        changed_env = result_of_left.get_env()
        return self.__right_cmd.run(changed_input, changed_env)


class CommandCAT(Command):
    """
    The command 'cat' concatenates files and print on the standard output.
    May have one and more arguments and even zero if placed on the right from PIPE.
    """
    def __init__(self, args):
        self.__args = args

    def run(self, input, env):
        return_value = 0
        self.__output = OutputStream()
        num_of_args = len(self.__args)

        if not num_of_args:
            self.__output.write(input.get_value())
        else:
            for file in self.__args:
                file_path = os.path.join(env.get_cwd(), file)
                if not os.path.isfile(file_path):
                    self.__output.write("cat: {}: No such file or directory.".format(file))
                    return_value = 1
                    break
                with open(file, 'r') as opened_file:
                    self.__output.write(opened_file.read())
        return CommandResult(self.__output, env, return_value)


class CommandPWD(Command):
    """
    The 'pwd' command print name of current/working directory.
    """
    def __init__(self, args):
        self.__args = args

    def run(self, input, env):
        self.__output = OutputStream()
        return_value = 0
        if self.__args:
            self.__output.write('Wrong number of arguments for pwd command:'
                                ' expected 0, got {}.'.format(len(self.__args)))
            return_value = 1
            return CommandResult(self.__output, env, return_value)

        self.__output.write(env.get_cwd())
        return CommandResult(self.__output, env, return_value)


class CommandEXIT(Command):
    """The class of 'exit' command causes normal process termination.
    Raise ExitException that will be catched in the main loop of program."""
    def __init__(self, args):
        self.__args = args

    def run(self, input, env):
        raise ExitException('Bye!')



class CommandECHO(Command):
    """ The 'echo' command displays a line of text that came as input."""
    def __init__(self, args):
        self.__args = args

    def run(self, input_stream, env):
        output = OutputStream()
        output.write_line(' '.join(self.__args))

        return CommandResult(output, env, 0)


class CommandWC(Command):
    """ The 'wc' command that prints newline, word, and byte counts for each file."""
    def __init__(self, args):
        self.__args = args

    def __count_lines_words_bytes(self, input):
        lines = input.splitlines()
        line_count = len(lines)
        word_count = 0
        for line in lines:
            word_count += len(line.split(' '))
        char_count = len(input.encode(sys.stdin.encoding))
        return [line_count, word_count, char_count]

    def run(self, input, env):
        self.__output = OutputStream()
        return_value = 0
        result = {}

        if not self.__args:
            result[' '] = self.__count_lines_words_bytes(input.get_value())
        else:
            for file in self.__args:
                file_path = os.path.join(env.get_cwd(), file)
                if not os.path.isfile(file_path):
                    self.__output.write("wc: {}: No such file or directory.".format(file))
                    return_value = 1
                    break
                with open(file, 'r') as opened_file:
                    result[file] = self.__count_lines_words_bytes(opened_file.read())

        if return_value is 0:
            total_lines = 0
            total_words = 0
            total_bytes = 0
            for (name, [line_count, word_count, byte_count]) in result.items():
                total_bytes += byte_count
                total_words += word_count
                total_lines += line_count
                self.__output.write_line('{:4d} {:4d} {:4d}    {}'.format
                                         (line_count, word_count, byte_count, name))

            if len(self.__args) > 1:
                self.__output.write_line('{:4d} {:4d} {:4d}    {}'.format
                                         (total_lines, total_words, total_bytes, 'total'))

        return CommandResult(self.__output, env, return_value)


class UnknownCommand(Command):
    """
    Commands that are not in this implementation will be called from standard shell.
    """
    def __init__(self, cmd, args):
        self.__command = cmd
        self.__args = args

    def run(self, input, env):
        self.__output = OutputStream()
        return_value = 0
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
            self.__output.write('Command {}: {}'.format(self.__command, 'some problems'))
            return_value = 1

        return CommandResult(self.__output, env, return_value)
