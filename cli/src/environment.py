import pathlib
import os

class Environment:
    """
    The class that contains current environment and variables of processes.
    """
    def __init__(self):
        self.commands = {'cat', 'echo', 'exit', 'pwd', 'wc'}
        self.__vars_values = dict()
        self.__current_working_directory = pathlib.Path(os.getcwd())

    def get_var_value(self, var_name):
        """Returns the value of variable."""
        return self.__vars_values.get(var_name, '')

    def set_var_value(self, var_name, value):
        """Sets variable's value."""
        self.__vars_values[var_name] = value

    def get_cwd(self):
        """Returns the current working directory."""
        return str(self.__current_working_directory)

