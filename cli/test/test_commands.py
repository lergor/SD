import unittest
from src.commands import *
from src.iostreams import Stream
from src.environment import Environment


class TestAllCommands(unittest.TestCase):

    def setUp(self):
        self.env = Environment()
        self.file = 'test_text.txt'

    def test_unknown(self):
        command = UnknownCommand('echo', ['hello'])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('hello' + os.linesep, result.get_output())

    def test_unknown_fail(self):
        command = UnknownCommand('kek', [])
        result = command.run(Stream(), self.env)
        self.assertEqual(1, result.return_value())
        self.assertEqual('Command kek: command not found.{}'.format(os.linesep),
                         result.get_output())

    def test_assignment(self):
        command = CommandASSIGNMENT('x', 'ololo')
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('', result.get_output())
        self.assertEqual('ololo', result.get_env().get_var_value('x'))

    def test_pwd(self):
        command = CommandPWD([])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual(str(os.getcwd()) + os.linesep, result.get_output())

    def test_pwd_fail(self):
        command = CommandPWD(['x', 'ololo'])
        result = command.run(Stream(), self.env)
        self.assertEqual(result.return_value(), 1)
        self.assertEqual('Wrong number of arguments for pwd command:'
                         ' expected 0, got 2.{}'.format(os.linesep)
                         , result.get_output())

    def test_exit(self):
        command = CommandEXIT(['x', 'ololo'])
        self.assertRaises(ExitException, command.run, Stream(), self.env)

    def test_wc(self):
        command = CommandWC([self.file])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        result = result.get_output().split()
        right_result = ['9', '60', '283', self.file]
        self.assertEqual(len(right_result), len(result))
        for i in range(len(result)):
            self.assertEqual(right_result[i], result[i])

    def test_wc_fail(self):
        file = 'not_funny.txt'
        command = CommandWC([file])
        result = command.run(Stream(), self.env)
        self.assertEqual(1, result.return_value())
        self.assertEqual(result.get_output(), 'wc: not_funny.txt: '
                        'No such file or directory.{}'.format(os.linesep))

    def test_echo(self):
        command = CommandECHO(['testing', 'command', 'echo'])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('testing command echo' + os.linesep, result.get_output())

    def test_empty_echo(self):
        command = CommandECHO()
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual(os.linesep, result.get_output())

    def test_cat(self):
        command = CommandCAT([self.file])
        result = command.run(Stream(), self.env)
        with open(self.file, 'r') as f:
            answer = f.read()
        self.assertEqual(0, result.return_value())
        self.assertEqual(answer, result.get_output())

    def test_cat_fail(self):
        command = CommandCAT(['not_funny.txt'])
        result = command.run(Stream(), self.env)
        self.assertEqual(1, result.return_value())
        right = 'cat: not_funny.txt: No such file or directory.{}'.\
            format(os.linesep)
        self.assertEqual(right, result.get_output())

    def test_echo_pipe_cat(self):
        left_command = CommandECHO(['word1', 'word2', 'word3'])
        right_command = CommandCAT([])
        first_pipe = CommandPIPE(left_command, right_command)
        result = first_pipe.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('word1 word2 word3' + os.linesep, result.get_output())

    def test_echo_pipe_cat_pipe_wc(self):
        left_command = CommandECHO(['word1', 'word2', 'word3'])
        right_command = CommandCAT([])
        first_pipe = CommandPIPE(left_command, right_command)
        right_command = CommandWC([])
        second_pipe = CommandPIPE(first_pipe, right_command)
        result = second_pipe.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        result = result.get_output().split()
        right_result = ['1', '3', '18']
        self.assertEqual(len(right_result), len(result))
        for i in range(len(result)):
            self.assertEqual(right_result[i], result[i])

    def test_cat_pipe_pwd(self):
        left_command = CommandCAT([self.file, 'test_env.py'])
        right_command = CommandPWD([])
        first_pipe = CommandPIPE(left_command, right_command)
        result = first_pipe.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual(str(os.getcwd() + os.linesep), result.get_output())

    def test_cat_pipe_pwd_pipe_wc(self):
        left_command = CommandCAT([self.file, 'test_env.py'])
        right_command = CommandPWD([])
        first_pipe = CommandPIPE(left_command, right_command)
        right_command = CommandWC([self.file, 'test_env.py'])
        second_pipe = CommandPIPE(first_pipe, right_command)
        result = second_pipe.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        result = result.get_output().split()
        right_result = ['9', '60', '283', self.file,
                        '21', '50', '622', 'test_env.py',
                        '30', '110', '905', 'total']
        self.assertEqual(len(right_result), len(result))
        for i in range(len(result)):
            self.assertEqual(right_result[i], result[i])
