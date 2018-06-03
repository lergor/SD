import textwrap
from src.utils import UISettings


class Message:
    """
    The container for one message, holds its text and color.
    """

    def __init__(self, text='', color=(255, 255, 255)):
        self.text = text
        self.color = color


class MessageLog:
    """
    The container for all game messages.
    """

    def __init__(self):
        self.messages = []
        self.x = UISettings.message_x
        self.__width = UISettings.message_width
        self.__height = UISettings.message_height

    def add_message(self, message):
        if message and message.text:
            msg_lines = textwrap.wrap(message.text, self.__width)
            for line in msg_lines:
                if len(self.messages) == self.__height:
                    del self.messages[0]
                self.messages.append(Message(line, message.color))
