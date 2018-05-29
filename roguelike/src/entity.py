import math
from src.utils import UISettings, RenderOrder, EquipmentSlots
from src.world.characters.equipment import Equipment
from src.world.characters.equippable import Equippable
from src.world.characters.fighter import Fighter
from src.world.characters.inventory import Inventory
from src.world.characters.item import Item

from src.world.characters.level import Level


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, x, y, char, color, name, blocks=False, render_order=RenderOrder.CORPSE, fighter=None, ai=None,
                 item=None, inventory=None, stairs=None, level=None, equipment=None, equippable=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order
        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.level = level
        self.equipment = equipment
        self.equippable = equippable

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.stairs:
            self.stairs.owner = self

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

    def move_towards(self, ui, target_x, target_y):
        path = ui.map.compute_path(self.x, self.y, target_x, target_y)
        if path:
            dx = path[0][0] - self.x
            dy = path[0][1] - self.y

            if ui.map.walkable[path[0][0], path[0][1]] and \
                    not ui.get_blocking_entities_at_location(self.x + dx, self.y + dy):
                self.move(dx, dy)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

    def draw(self, map, console):
        if map.fov[self.x, self.y] or (self.stairs and map.explored[self.x][self.y]):
            console.draw_char(self.x, self.y, self.char, self.color, bg=None)

    def overlap(self, entity):
        return self.x == entity.x and self.y == entity.y

    def make_dead(self):
        self.char = '%'
        self.color = UISettings.colors.get('dark_red')
        self.blocks = False
        self.fighter = None
        self.ai = None
        self.name = 'remains of ' + self.name
        self.render_order = RenderOrder.CORPSE


class EntityFabric:

    @staticmethod
    def create_player():
        fighter_component = Fighter(hp=100, defense=1, power=2)
        inventory_component = Inventory(26)
        level_component = Level()
        equipment_component = Equipment()
        player = Entity(0, 0, '@', (255, 255, 255), 'Player', blocks=True,
                             render_order=RenderOrder.ACTOR,
                             fighter=fighter_component, inventory=inventory_component,
                             level=level_component,
                             equipment=equipment_component)
        equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
        dagger = Entity(0, 0, '-', UISettings.colors.get('sky'), 'Dagger',
                        equippable=equippable_component)
        player.inventory.add_item(dagger)
        player.equipment.toggle_equip(dagger)
        return player

    @staticmethod
    def make_entity():
        pass

