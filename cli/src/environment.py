"""
The abstraction of environment. Stores all variables
that appeared during CLI running and current directory.
"""
import os


class Environment:
    """
    The class that contains the current environment and variables of processes.
    """
    def __init__(self):
        """
        Sets list of available commands,
        the empty dictionary as storage and current working directory.
        """
        self.commands = ['cat', 'echo', 'exit', 'pwd', 'wc']
        self.__vars_values = dict()
        self.__current_working_directory = os.getcwd()

    def get_var_value(self, var_name):
        """Returns the value of given variable."""
        return self.__vars_values.get(var_name, '')

    def set_var_value(self, var_name, value):
        """Sets the new value of variable."""
        self.__vars_values[var_name] = value

    def get_cwd(self):
        """Returns the current working directory."""
        return str(self.__current_working_directory)
