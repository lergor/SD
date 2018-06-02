import textwrap
from src.utils import UISettings


class Message:
    def __init__(self, text, color=(255, 255, 255)):
        self.text = text
        self.color = color


class MessageLog:

    def __init__(self):
        self.messages = []
        self.x = UISettings.message_x
        self.width = UISettings.message_width
        self.height = UISettings.message_height

    def add_message(self, message):
        if message and message.text:
            msg_lines = textwrap.wrap(message.text, self.width)
            for line in msg_lines:
                if len(self.messages) == self.height:
                    del self.messages[0]
                self.messages.append(Message(line, message.color))
