"""
An input and output streams that command use.
"""

from io import StringIO
import os

class InputStream:
    """ An abstraction of command's input that command gets. """

    def __init__(self, input=None):
        self.__io_str = StringIO()
        if input:
            self.__io_str.write(input)

    def get_value(self):
        return self.__io_str.getvalue()


class OutputStream:
    """ An abstraction of command's output that contains it's result. """

    def __init__(self):
        self.__io_str = StringIO()

    def write(self, str):
        self.__io_str.write(str)

    def write_line(self, string):
        self.__io_str.write(string)
        self.__io_str.write(os.linesep)

    def get_value(self):
        return self.__io_str.getvalue()

    def convert_to_input(self):
        return InputStream(self.__io_str.getvalue())