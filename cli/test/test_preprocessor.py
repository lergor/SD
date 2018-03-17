import unittest
from src.preprocessor import *
from src.environment import Environment


class TestPreprocessor(unittest.TestCase):

        def test_find_var(self):
            var_name, rest = Preprocessor.find_var('var')
            self.assertEqual(var_name, 'var')
            self.assertEqual(rest, '')
            var_name, rest = Preprocessor.find_var('var_1 567')
            self.assertEqual(var_name, 'var_1')
            self.assertEqual(rest, ' 567')

        def test_substitute_vars(self):
            env = Environment()
            env.set_var_value('x', '10')
            env.set_var_value('var_name', 'kek')
            result = Preprocessor.substitute_vars('$x', env)
            self.assertEqual('10',result)
            result = Preprocessor.substitute_vars('\'$x\'', env)
            self.assertEqual('$x', result)
            result = Preprocessor.substitute_vars('\"$x\"', env)
            self.assertEqual('10', result)
            result = Preprocessor.substitute_vars('\'$var_name\"$x\"kek\'', env)
            self.assertEqual('$var_name\"$x\"kek', result)
            result = Preprocessor.substitute_vars('\"$var_name\'$x\'kek\"', env)
            self.assertEqual('kek\'10\'kek', result)
            result = Preprocessor.substitute_vars('\'$var_name\'$x\'kek\'', env)
            self.assertEqual('$var_name10kek', result)
            result = Preprocessor.substitute_vars('\"$var_name\"$x\"kek\"', env)
            self.assertEqual('kek10kek', result)
            result = Preprocessor.substitute_vars('kek\'$var_name\'kek', env)
            self.assertEqual('kek$var_namekek', result)
            result = Preprocessor.substitute_vars('kek\"$var_name\"kek', env)
            self.assertEqual('kekkekkek', result)
            result = Preprocessor.substitute_vars('$x$var_name', env)
            self.assertEqual('10kek', result)
            result = Preprocessor.substitute_vars('\'$x$var_name\'', env)
            self.assertEqual('$x$var_name', result)
            result = Preprocessor.substitute_vars('\"$x$var_name\"', env)
            self.assertEqual('10kek', result)
            result = Preprocessor.substitute_vars('\"kek$xl\"', env)
            self.assertEqual('kek', result)
            result = Preprocessor.substitute_vars('\"kek$var_name 10\"', env)
            self.assertEqual('kekkek 10', result)
            result = Preprocessor.substitute_vars('\"\"\"$var_name\"\"\"', env)
            self.assertEqual('kek', result)
            result = Preprocessor.substitute_vars('\'\'\'$var_name\'\'\'', env)
            self.assertEqual('$var_name', result)

        def test_exceptions(self):
            env = Environment()
            self.assertRaises(ParserException,
                              Preprocessor.substitute_vars, '\'xx', env)
            self.assertRaises(ParserException,
                              Preprocessor.substitute_vars, '\"xx', env)
            self.assertRaises(ParserException,
                              Preprocessor.substitute_vars, '\"x\'x', env)

