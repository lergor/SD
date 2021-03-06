import math
from src.utils import UISettings, RenderOrder, EquipmentSlots
from src.game_objects.monster import BasicMonster
from src.game_objects.equipment import Equipment, Equippable
from src.game_objects.fighter import Fighter
from src.game_objects.inventory import Inventory
from src.game_objects.item import Item
from src.game_objects.level import Level


class Entity:
    """
    The main class for all entities in the game. It contains all
    accessories of the entity and methods for interactions
    with other entities and essential behavior on the high level.
    """

    def __init__(self, x, y, char, color, name,
                 render_order=RenderOrder.CORPSE, **kwargs):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.render_order = render_order
        self.__set_all(**kwargs)

    def __set_all(self, **kwargs):
        self.blocks = kwargs.get('blocks')
        self.fighter = kwargs.get('fighter')
        self.ai = kwargs.get('ai')
        self.item = kwargs.get('item')
        self.inventory = kwargs.get('inventory')
        self.stairs = kwargs.get('stairs')
        self.level = kwargs.get('level')
        self.equipment = kwargs.get('equipment')
        self.equippable = kwargs.get('equippable')
        if self.fighter:
            self.fighter.owner = self
        if self.ai:
            self.ai.owner = self
        if self.item:
            self.item.owner = self
        if self.inventory:
            self.inventory.owner = self
        if self.level:
            self.level.owner = self
        if self.equipment:
            self.equipment.owner = self
        if self.equippable:
            self.equippable.owner = self
            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def move_towards(self, obj_keeper, target_x, target_y):
        path = obj_keeper.map.compute_path(self.x, self.y, target_x, target_y)
        if path:
            dx = path[0][0] - self.x
            dy = path[0][1] - self.y
            if obj_keeper.map.walkable[path[0][0], path[0][1]] and \
                    not obj_keeper.get_blocking_entities_at(self.x + dx, self.y + dy):
                self.move(dx, dy)

    def distance_to(self, other):
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

    def draw(self, map, console):
        if map.fov[self.x, self.y] or (self.stairs and map.explored[self.x][self.y]):
            console.draw_char(self.x, self.y, self.char, self.color, bg=None)

    def overlap(self, entity):
        return self.x == entity.x and self.y == entity.y

    def make_dead(self):
        if self.fighter and self.level:
            self.__update_info()
        self.char = '%'
        self.color = UISettings.dark_red
        self.blocks = False
        self.fighter = None
        self.ai = None
        self.name = 'remains of ' + self.name
        self.render_order = RenderOrder.CORPSE

    def get_info(self):
        if self.fighter and self.level:
            self.__update_info()
        return self.last_info

    def __update_info(self):
        self.last_info = ['Character Information',
                          'Level: {0}'.format(self.level.current_level),
                          'Experience: {0}'.format(self.level.current_xp),
                          'Experience to next level: {0}'.format(self.level.experience_to_next_level),
                          'Maximum HP: {0}'.format(self.fighter.max_hp),
                          'Attack: {0}'.format(self.fighter.power),
                          'Defense: {0}'.format(self.fighter.defense)]


class EntityFactory:
    """
    The static factory that creates entities.
    """

    @staticmethod
    def __create_player():
        fighter_component = Fighter(hp=100, defense=1, power=2)
        inventory_component = Inventory(26)
        level_component = Level()
        equipment_component = Equipment()
        player = Entity(0, 0, '@', UISettings.white, 'Player', blocks=True,
                             render_order=RenderOrder.PLAYER,
                             fighter=fighter_component, inventory=inventory_component,
                             level=level_component,
                             equipment=equipment_component)
        equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
        dagger = Entity(0, 0, '-', UISettings.sky, 'Dagger',
                        equippable=equippable_component)
        player.inventory.add_item(dagger)
        player.equipment.toggle_equip(dagger)
        return player

    @staticmethod
    def __make_stairs(x, y):
        return Entity(x, y, '>', UISettings.white, 'Stairs',
                      stairs=True, render_order=RenderOrder.STAIRS)

    @staticmethod
    def __make_monster(name, x, y):
        if name == 'Spider':
            hp, defense, power, xp = 20, 0, 4, 35
            symbol, color = 'x', UISettings.desaturated_green
        if name == 'Bat':
            hp, defense, power, xp = 25, 1, 6, 50
            symbol, color = 'V', UISettings.my_green
        if name == 'Snake':
            hp, defense, power, xp = 30, 2, 8, 70
            symbol, color = 'S', UISettings.darker_green
        fighter_component = Fighter(hp=hp, defense=defense, power=power, xp=xp)
        ai_component = BasicMonster()
        return Entity(x, y, symbol, color, name, blocks=True, ai=ai_component,
                      render_order=RenderOrder.MONSTER, fighter=fighter_component)

    @staticmethod
    def __make_item(name, x, y):
        item_component, equippable_component = None, None
        if name == 'Healing potion':
            item_component = Item(use_function=Item.heal, amount=40)
            sym, color = '+', UISettings.violet
        if name == 'Sword':
            equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=4)
            sym, color = 'T', UISettings.sky
        if name == 'Shield':
            equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=2)
            sym, color = 'O', UISettings.darker_orange
        return Entity(x, y, sym, color, name, render_order=RenderOrder.ITEM,
                      item=item_component, equippable=equippable_component)

    @staticmethod
    def create_entity(name, x=0, y=0):
        if name == 'Player':
            return EntityFactory.__create_player()
        if name == 'Stairs':
            return EntityFactory.__make_stairs(x, y)
        if name in {'Spider', 'Snake', 'Bat'}:
            return EntityFactory.__make_monster(name, x, y)
        if name in {'Healing potion', 'Sword', 'Shield'}:
            return EntityFactory.__make_item(name, x, y)
