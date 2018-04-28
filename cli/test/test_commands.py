import unittest
from src.commands import *
from src.iostreams import Stream
from src.environment import Environment


class TestAllCommands(unittest.TestCase):

    def setUp(self):
        self.exited = False
        self.env = Environment()
        self.file = 'test_text.txt'

    def test_unknown(self):
        command = UnknownCommand('echo', ['hello'])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('hello' + os.linesep, result.get_output())

        command = UnknownCommand('kek', [])
        result = command.run(Stream(), self.env)
        self.assertEqual(1, result.return_value())
        print(result.get_output())
        self.assertEqual('Command kek: command not found.{}'.format(os.linesep),
                         result.get_output())

    def test_assignment(self):
        command = CommandASSIGNMENT('x', 'ololo')
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('', result.get_output())
        self.assertEqual('ololo', result.get_env().get_var_value('x'))

    def test_pwd(self):
        command = CommandPWD()
        command.set_args([])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual(str(os.getcwd()) + os.linesep, result.get_output())

        command = CommandPWD()
        command.set_args(['x', 'ololo'])
        result = command.run(Stream(), self.env)
        self.assertEqual(result.return_value(), 1)
        self.assertEqual('Wrong number of arguments for pwd command:'
                         ' expected 0, got 2.{}'.format(os.linesep)
                         , result.get_output())

    def test_exit(self):
        command = CommandEXIT()
        command.set_args(['x', 'ololo'])
        self.assertRaises(ExitException, command.run, Stream(), self.env)

    def test_wc(self):
        command = CommandWC()
        command.set_args([self.file])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        result = result.get_output().split()
        right_result = ['10', '60', '284', self.file]
        self.assertEqual(len(right_result), len(result))
        for i in range(len(result)):
            self.assertEqual(right_result[i], result[i])

        file = 'not_funny.txt'
        command = CommandWC()
        command.set_args([file])
        result = command.run(Stream(), self.env)
        self.assertEqual(1, result.return_value())
        self.assertEqual(result.get_output(), 'wc: not_funny.txt: '
                        'No such file or directory.{}'.format(os.linesep))

    def test_echo(self):
        command = CommandECHO()
        command.set_args(['testing', 'command', 'echo'])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('testing command echo' + os.linesep, result.get_output())

        command = CommandECHO()
        command.set_args()
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual(os.linesep, result.get_output())

    def test_cat(self):
        command = CommandCAT()
        command.set_args([self.file])
        result = command.run(Stream(), self.env)
        with open(self.file, 'r') as f:
            answer = f.read()
            sep = '\n'
            if '\r\n' in answer:
                sep = '\r\n'
            answer = answer.replace(sep, os.linesep)
        self.assertEqual(0, result.return_value())
        self.assertEqual(answer, result.get_output())

        command = CommandCAT()
        command.set_args(['not_funny.txt'])
        result = command.run(Stream(), self.env)
        self.assertEqual(1, result.return_value())
        right = 'cat: not_funny.txt: No such file or directory.{}'.\
            format(os.linesep)
        self.assertEqual(right, result.get_output())

    def test_grep_without_keys(self):
        command = CommandGREP()
        command.set_args(['Son', self.file])
        result = command.run(Stream(), self.env)
        sep = '\n'
        if '\r\n' in result.get_output():
            sep = '\r\n'
        result_text = result.get_output().replace(sep, os.linesep)
        self.assertEqual(0, result.return_value())
        self.assertEqual('The Perfect \x1b[1;31mSon\x1b[0m.' + os.linesep, result_text)

    def test_grep_ignore_case(self):
        command = CommandGREP()
        command.set_args(['-i', 'DOES', self.file])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('B: \x1b[1;31mDoes\x1b[0m he smoke?{}'
                         'A: No, he \x1b[1;31mdoes\x1b[0mn\'t.{}'
                         'B: \x1b[1;31mDoes\x1b[0m he drink whiskey?{}'
                         'A: No, he \x1b[1;31mdoes\x1b[0mn\'t.{}'
                         'B: \x1b[1;31mDoes\x1b[0m he ever come home late?{}'
                         'A: No, he \x1b[1;31mdoes\x1b[0mn\'t.{}'.
                         format(os.linesep, os.linesep, os.linesep,
                                os.linesep, os.linesep, os.linesep),
                         result.get_output())

    def test_grep_after_context(self):
        true_result = 'A: I \x1b[1;31mhave\x1b[0m the perfect son.{}'\
                         'B: Does he smoke?{}'\
                         '\x1b[0;34m---\x1b[0m{}'\
                         'B: I guess you really do \x1b[1;31mhave\x1b[0m '\
                         'the perfect son. How old is he?{}'\
                         'A: He will be six months old next Wednesday.{}'.\
                         format(os.linesep, os.linesep, os.linesep, os.linesep, os.linesep)

        command = CommandGREP()
        command.set_args(['-A', '1', 'have', self.file])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual(true_result,
                         result.get_output())

        command.set_args(['-A1', 'have', self.file])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual(true_result,
                         result.get_output())

    def test_grep_i_w(self):
        command = CommandGREP()
        command.set_args(['-iw', 'does', self.file])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('B: \x1b[1;31mDoes\x1b[0m he smoke?{}'
                         'B: \x1b[1;31mDoes\x1b[0m he drink whiskey?{}'
                         'B: \x1b[1;31mDoes\x1b[0m he ever come home late?{}'.
                         format(os.linesep, os.linesep, os.linesep),
                         result.get_output())

    def test_grep_i_w_A(self):
        command = CommandGREP()
        command.set_args(['-iwA', '2', 'HAVE', self.file])
        result = command.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('A: I \x1b[1;31mhave\x1b[0m the perfect son.{}'
                         'B: Does he smoke?{}'
                         'A: No, he doesn\'t.{}'
                         '\x1b[0;34m---\x1b[0m{}'
                         'B: I guess you really do \x1b[1;31mhave\x1b[0m '
                         'the perfect son. How old is he?{}'
                         'A: He will be six months old next Wednesday.{}'.
                         format(os.linesep, os.linesep, os.linesep,
                                os.linesep, os.linesep, os.linesep),
                         result.get_output())

    def test_grep_without_source(self):
        command = CommandGREP()
        command.set_args(['pattern'])
        result = command.run(Stream(), self.env)
        self.assertEqual(1, result.return_value())
        self.assertEqual('Wrong number of arguments for grep command.' + os.linesep,
                         result.get_output())

    def test_grep_with_wrong_file(self):
        command = CommandGREP()
        command.set_args(['pattern', 'other_file.txt'])
        result = command.run(Stream(), self.env)
        self.assertEqual(1, result.return_value())
        self.assertEqual('grep: other_file.txt: No such file or directory.' + os.linesep,
                         result.get_output())

    def test_pipe(self):
        left_command = CommandECHO()
        left_command.set_args(['word1', 'word2', 'word3'])
        right_command = CommandCAT()
        right_command.set_args([])
        first_pipe = CommandPIPE(left_command, right_command)
        result = first_pipe.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('word1 word2 word3' + os.linesep, result.get_output())

        right_command = CommandWC()
        right_command.set_args([])
        second_pipe = CommandPIPE(first_pipe, right_command)
        result = second_pipe.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        result = result.get_output().split()
        right_result = ['1', '3', '18']
        self.assertEqual(len(right_result), len(result))
        for i in range(len(result)):
            self.assertEqual(right_result[i], result[i])

        left_command = CommandCAT()
        left_command.set_args([self.file, 'test_env.py'])
        right_command = CommandPWD()
        right_command.set_args([])
        first_pipe = CommandPIPE(left_command, right_command)
        result = first_pipe.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual(str(os.getcwd() + os.linesep), result.get_output())

        right_command = CommandWC()
        right_command.set_args([self.file, 'test_env.py'])
        second_pipe = CommandPIPE(first_pipe, right_command)
        result = second_pipe.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        result = result.get_output().split()
        right_result = ['10', '60', '284', self.file,
                        '21', '50', '622', 'test_env.py',
                        '31', '110', '906', 'total']
        self.assertEqual(len(right_result), len(result))
        for i in range(len(result)):
            self.assertEqual(right_result[i], result[i])

    def test_echo_pipe_grep(self):
        left_command = CommandECHO()
        left_command.set_args(['kek1', 'kek2', 'kek3'])
        right_command = CommandGREP()
        right_command.set_args(['kek'])
        pipe = CommandPIPE(left_command, right_command)
        result = pipe.run(Stream(), self.env)
        self.assertEqual(0, result.return_value())
        self.assertEqual('\x1b[1;31mkek\x1b[0m1 \x1b[1;31mkek\x1b[0m2'
                         ' \x1b[1;31mkek\x1b[0m3' + os.linesep,
                         result.get_output())

    def test_echo_pipe_grep_without_pattern(self):
        left_command = CommandECHO()
        left_command.set_args(['kek1', 'kek2', 'kek3'])
        right_command = CommandGREP()
        right_command.set_args([])
        pipe = CommandPIPE(left_command, right_command)
        result = pipe.run(Stream(), self.env)
        self.assertEqual(1, result.return_value())
        self.assertEqual('Wrong number of arguments for grep '
                         'command.' + os.linesep, result.get_output())
