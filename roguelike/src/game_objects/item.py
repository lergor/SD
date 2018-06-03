from src.messages import Message
from src.utils import UISettings


class Item:
    """
    It's a class for items in the game.
    Has static methods for items, for example, heal for a healing potion.
    """

    def __init__(self, use_function=None, targeting=False, targeting_message=None, **kwargs):
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.function_kwargs = kwargs

    @staticmethod
    def heal(*args, **kwargs):
        entity = args[0]
        amount = kwargs.get('amount')
        if entity.fighter.hp == entity.fighter.max_hp:
            consumed = False
            text, color = 'You are already at full health', UISettings.yellow
        else:
            entity.fighter.heal(amount)
            consumed = True
            text, color = 'Your wounds start to feel better!', UISettings.green
        return [{'consumed': consumed, 'message': Message(text, color)}]
