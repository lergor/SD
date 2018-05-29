from src.game_messages import Message
from src.utils import UISettings


class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        text = 'You cannot carry any more, your inventory is full'
        color = UISettings.colors.get('yellow')
        added = None
        if len(self.items) < self.capacity:
            added = item
            self.items.append(item)
            text = 'You pick up the {0}!'.format(item.name)
            color = UISettings.colors.get('blue')
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
                    results.append({'message': Message('The {0} cannot be used'.format(item_entity.name),
                                                       UISettings.colors.get('yellow'))})
            else:
                if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                    results.append({'targeting': item_entity})
                else:
                    kwargs = {**item_component.function_kwargs, **kwargs}
                    item_use_results = item_component.use_function(self.owner, UISettings.colors, **kwargs)

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

            if self.owner.equipment.main_hand == item or self.owner.equipment.off_hand == item:
                self.owner.equipment.toggle_equip(item)

            item.x = self.owner.x
            item.y = self.owner.y

            self.remove_item(item)
            results.append({'item_dropped': item, 'message': Message('You dropped the {0}'.format(item.name),
                                                                     UISettings.colors.get('yellow'))})

        return results
