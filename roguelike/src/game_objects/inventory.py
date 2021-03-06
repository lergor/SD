from src.messages import Message
from src.utils import UISettings


class Inventory:
    """
    The class that holds all inventory which the entity owns.
    It can add, drop, use and remove items.
    """

    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        text = 'You cannot carry any more, your inventory is full'
        color = UISettings.yellow
        added = None
        if len(self.items) < self.capacity:
            added = item
            self.items.append(item)
            text = 'You pick up the {0}!'.format(item.name)
            color = UISettings.blue
        return {'item_added': added, 'message': Message(text, color)}

    def use(self, index, **kwargs):
        results = []
        if index < len(self.items):
            item_entity = self.items[index]
            item_component = item_entity.item
            if item_component.use_function is None:
                equippable_component = item_entity.equippable
                if equippable_component:
                    results.append({'equip': item_entity})
                else:
                    text = 'The {0} cannot be used'.format(item_entity.name)
                    results.append({'message': Message(text, UISettings.yellow)})
            else:
                if item_component.targeting and \
                        not (kwargs.get('target_x') or kwargs.get('target_y')):
                    results.append({'targeting': item_entity})
                else:
                    kwargs = {**item_component.function_kwargs, **kwargs}
                    item_use_results = item_component.use_function(self.owner, **kwargs)
                    for item_use_result in item_use_results:
                        if item_use_result.get('consumed'):
                            self.remove_item(item_entity)
                    results.extend(item_use_results)
        return results

    def remove_item(self, item):
        self.items.remove(item)

    def drop_item(self, index):
        results = []
        if index < len(self.items):
            item = self.items[index]
            if self.owner.equipment.main_hand == item \
                    or self.owner.equipment.off_hand == item:
                self.owner.equipment.toggle_equip(item)
            item.x = self.owner.x
            item.y = self.owner.y
            self.remove_item(item)
            message = Message('You dropped the ' + item.name, UISettings.yellow)
            results.append({'item_dropped': item, 'message': message})
        return results
