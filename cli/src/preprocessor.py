"""
The Preprocessor class substitutes variables into the given string
and removes redundant quotes if needed.
Examples:
    x=10
    var_name=kek

    $x              ->    10
    "$x"            ->    10
    '$x'            ->    $x
    kek'$var_name'kek     ->    kek$var_namekek
    kek"$var_name"kek     ->    kekkekkek

    "$x"'$var_name'    ->    10$var_name
    '$x'"$var_name"    ->    $xkek

    '$var_name"$x"kek'      ->    $var_name"$x"kek
    "$var_name'$x'kek"      ->    kek'10'kek

    "$var_name"$x"kek"      ->    kek10kek
    '$var_name'$x'kek'      ->    $var_name10kek

"""

from src.parser import *


class ParserException(Exception):
    """An exception raising while parsing. """
    pass


class Preprocessor:

    @staticmethod
    def find_var(str):
        """
        Finds the variable name after the '$' symbol to space,
        some quote or the end of the string.
        :param str: the string after the '$' symbol.
        :return: the variable name and the rest of the string.
        """
        next_ix = 0
        while next_ix < len(str):
            if str[next_ix].isspace() or str[next_ix] in ('$', '\'', '\"'):
                break
            next_ix += 1
        var_name = str[0:next_ix]
        str = str[next_ix:]
        return var_name, str

    @staticmethod
    def substitute_vars(input, env):
        """
        The main static method that substitutes variables from the current environment
        if their names are in the string and removes redundant quotes if needed.
        :param input: the input string.
        :param env: the Environment instance with variables.
        :return: the preprocessed string.
        """
        result = ''
        while input:
            if input[0] == '$':
                var_name, input = Preprocessor.find_var(input[1:])
                var_value = env.get_var_value(var_name)
                result += var_value
            elif input[0] == '\"':
                next_ix = input[1:].find('\"')
                if next_ix == -1:
                    raise ParserException('End of line: missing second quote.')
                in_quotes = input[1:next_ix + 1]
                ix = in_quotes.find('\'')
                if ix != -1:
                    in_quotes = Preprocessor.quotes_in_quotes(in_quotes, env)
                    input = input[next_ix + 1:-1]
                else:
                    in_quotes = Preprocessor.substitute_vars(in_quotes, env)
                    input = input[next_ix + 2:]
                result += in_quotes
            elif input[0] == '\'':
                next_ix = input[1:].find('\'')
                if next_ix == -1:
                    raise ParserException('End of line: missing second quote2.')
                result += input[1:next_ix+1]
                input = input[next_ix + 2:]
            else:
                result += input[0]
                input = input[1:]
        return result

    @staticmethod
    def quotes_in_quotes(input, env):
        """
        Processes the string with '\'' quotes within '\"' quotes,
        i.e. when substitution is needed.
        For example:
        "text'text'text"
        Splits the input string by quotes and processes parts.
        :param input: the string without the first quote.
        :param env: the Environment instance with variables.
        :return: the preprocessed string.
        """
        other_quote = '\''
        ix = input.find(other_quote)
        first_part = input[0:ix]
        first_part = Preprocessor.substitute_vars(first_part, env)
        ix_next = input[ix + 1:].find(other_quote)
        if ix_next != -1:
            ix_next += ix + 1
            second_part = input[ix + 1:ix_next]
            second_part = Preprocessor.substitute_vars(second_part, env)
            third_part = input[ix_next + 1:]
            third_part = Preprocessor.substitute_vars(third_part, env)
            in_quotes = other_quote + second_part + other_quote
            return first_part + in_quotes + third_part
        return input

