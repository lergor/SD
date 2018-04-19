import unittest
from src.preprocessor import *
from src.environment import Environment


class TestPreprocessor(unittest.TestCase):

        def setUp(self):
            self.__env = Environment()
            self.__env.set_var_value('x', '10')
            self.__env.set_var_value('var_name', 'kek')

        def test_find_var(self):
            var_name, rest = Preprocessor.find_var('var')
            self.assertEqual(var_name, 'var')
            self.assertEqual(rest, '')

        def test_find_var_in_string(self):
            var_name, rest = Preprocessor.find_var('var_1 567')
            self.assertEqual(var_name, 'var_1')
            self.assertEqual(rest, ' 567')

        def test_substitute_vars_single(self):
            result = Preprocessor.substitute_vars('$x', self.__env)
            self.assertEqual('10',result)

        def test_substitute_vars_in_single_quotes(self):
            result = Preprocessor.substitute_vars('\'$x\'', self.__env)
            self.assertEqual('$x', result)

        def test_substitute_vars_in_double_quotes(self):
            result = Preprocessor.substitute_vars('\"$x\"', self.__env)
            self.assertEqual('10', result)

        def test_substitute_vars_double_in_single_quotes(self):
            result = Preprocessor.substitute_vars('\'$var_name\"$x\"kek\'', self.__env)
            self.assertEqual('$var_name\"$x\"kek', result)

        def test_substitute_vars_single_in_double_quotes(self):
            result = Preprocessor.substitute_vars('\"$var_name\'$x\'kek\"', self.__env)
            self.assertEqual('kek\'10\'kek', result)

        def test_substitute_vars_single_in_single_quotes(self):
            result = Preprocessor.substitute_vars('\'$var_name\'$x\'kek\'', self.__env)
            self.assertEqual('$var_name10kek', result)

        def test_substitute_vars_double_in_double_quotes(self):
            result = Preprocessor.substitute_vars('\"$var_name\"$x\"kek\"', self.__env)
            self.assertEqual('kek10kek', result)

        def test_substitute_vars_single_quotes_in_text(self):
            result = Preprocessor.substitute_vars('kek\'$var_name\'kek', self.__env)
            self.assertEqual('kek$var_namekek', result)

        def test_substitute_vars_double_quotes_in_text(self):
            result = Preprocessor.substitute_vars('kek\"$var_name\"kek', self.__env)
            self.assertEqual('kekkekkek', result)

        def test_substitute_two_vars(self):
            result = Preprocessor.substitute_vars('$x$var_name', self.__env)
            self.assertEqual('10kek', result)

        def test_substitute_two_vars_in_single_quotes(self):
            result = Preprocessor.substitute_vars('\'$x$var_name\'', self.__env)
            self.assertEqual('$x$var_name', result)

        def test_substitute_two_vars_in_double_quotes(self):
            result = Preprocessor.substitute_vars('\"$x$var_name\"', self.__env)
            self.assertEqual('10kek', result)

        def test_substitute_no_var_in_text_in_double_quotes(self):
            result = Preprocessor.substitute_vars('\"kek$xl\"', self.__env)
            self.assertEqual('kek', result)

        def test_substitute_var_in_text_in_double_quotes(self):
            result = Preprocessor.substitute_vars('\"kek$var_name 10\"', self.__env)
            self.assertEqual('kekkek 10', result)

        def test_substitute_var_in_three_double_quotes(self):
            result = Preprocessor.substitute_vars('\"\"\"$var_name\"\"\"', self.__env)
            self.assertEqual('kek', result)

        def test_substitute_var_in_three_single_quotes(self):
            result = Preprocessor.substitute_vars('\'\'\'$var_name\'\'\'', self.__env)
            self.assertEqual('$var_name', result)

        def test_exception_one_single_quote(self):
            self.assertRaises(ParserException,
                              Preprocessor.substitute_vars, '\'xx', self.__env)

        def test_exception_one_double_quote(self):
            self.assertRaises(ParserException,
                              Preprocessor.substitute_vars, '\"xx', self.__env)

        def test_exception_one_single_and_one_double_quote(self):
            self.assertRaises(ParserException,
                              Preprocessor.substitute_vars, '\"x\'x', self.__env)
