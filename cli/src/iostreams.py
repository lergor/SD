"""
The abstraction of input and output streams for command usage.
"""

from io import StringIO
import os


class Stream:
    """
    The stream that contains input or/and commands executions results.
    """

    def __init__(self):
        """Creates StringIO for results storage."""
        self.__io_str = StringIO()

    def write(self, str):
        """Writes the input string."""
        self.__io_str.write(str)

    def write_line(self, string):
        """Write the input string with the newline symbol."""
        self.__io_str.write(string)
        self.__io_str.write(os.linesep)

    def get_value(self):
        """Returns current value of the Stream."""
        return self.__io_str.getvalue()
