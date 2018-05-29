from tdl.map import Map
from random import randint
from src.utils import UISettings, RenderOrder
from src.world.characters.ai import BasicMonster
from src.world.characters.equipment import EquipmentSlots
from src.world.characters.equippable import Equippable
from src.world.characters.fighter import Fighter
from src.world.characters.item import Item
from src.world.characters.stairs import Stairs
from src.entity import Entity
from src.game_messages import Message
from src.item_functions import cast_confuse, cast_fireball, cast_lightning, heal
from src.random_utils import from_dungeon_level, random_choice_from_dict




class GameMap(Map):

    def __init__(self, player, dungeon_level=1):
        super().__init__(UISettings.map_width, UISettings.map_height)
        self.explored = [[False for y in range(UISettings.map_height)]
                         for x in range(UISettings.map_width)]
        self.dungeon_level = dungeon_level
        self.player = player
        self.fabric = MapFabric(self)

    def make_map(self, entities):
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(UISettings.max_rooms):
            new_room = self.fabric.make_draft()
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                self.fabric.create_map(new_room)
                new_x, new_y = new_room.center()
                center_of_last_room_x = new_x
                center_of_last_room_y = new_y
                if num_rooms == 0:
                    self.player.x = new_x
                    self.player.y = new_y
                else:
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()
                    if randint(0, 1) == 1:
                        self.fabric.create_h_tunnel(prev_x, new_x, prev_y)
                        self.fabric.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.fabric.create_v_tunnel(prev_y, new_y, prev_x)
                        self.fabric.create_h_tunnel(prev_x, new_x, new_y)

                place_entities(new_room, entities, self.dungeon_level, UISettings.colors)
                rooms.append(new_room)
                num_rooms += 1

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', (255, 255, 255), 'Stairs',
                             render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

    def next_floor(self, player, level):
        game_map = GameMap(self.dungeon_level)
        entities = [player]
        self.make_map(entities)
        player.fighter.heal(player.fighter.max_hp // 2)
        return game_map, entities


class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return center_x, center_y

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


def place_entities(room, entities, dungeon_level, colors):
    max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], dungeon_level)
    max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], dungeon_level)

    # Get a random number of monsters
    number_of_monsters = randint(0, max_monsters_per_room)
    number_of_items = randint(0, max_items_per_room)

    monster_chances = {
        'orc': 80,
        'troll': from_dungeon_level([[15, 3], [30, 5], [60, 7]], dungeon_level)
    }

    item_chances = {
        'healing_potion': 35,
        'sword': from_dungeon_level([[5, 4]], dungeon_level),
        'shield': from_dungeon_level([[15, 8]], dungeon_level),
        'lightning_scroll': from_dungeon_level([[25, 4]], dungeon_level),
        'fireball_scroll': from_dungeon_level([[25, 6]], dungeon_level),
        'confusion_scroll': from_dungeon_level([[10, 2]], dungeon_level)
    }

    for i in range(number_of_monsters):
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)

        if not any([entity for entity in entities if entity.x == x and entity.y == y]):
            monster_choice = random_choice_from_dict(monster_chances)

            if monster_choice == 'orc':
                fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
                ai_component = BasicMonster()

                monster = Entity(x, y, 'V', colors.get('desaturated_green'), 'Orc', blocks=True,
                                 render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
            else:
                fighter_component = Fighter(hp=30, defense=2, power=8, xp=100)
                ai_component = BasicMonster()

                monster = Entity(x, y, 'T', colors.get('darker_green'), 'Troll', blocks=True,
                                 render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)

            entities.append(monster)

    for i in range(number_of_items):
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)

        if not any([entity for entity in entities if entity.x == x and entity.y == y]):
            item_choice = random_choice_from_dict(item_chances)

            if item_choice == 'healing_potion':
                item_component = Item(use_function=heal, amount=40)
                item = Entity(x, y, '!', colors.get('violet'), 'Healing Potion', render_order=RenderOrder.ITEM,
                              item=item_component)
            elif item_choice == 'sword':
                equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
                item = Entity(x, y, '/', colors.get('sky'), 'Sword', equippable=equippable_component)
            elif item_choice == 'shield':
                equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                item = Entity(x, y, '[', colors.get('darker_orange'), 'Shield', equippable=equippable_component)
            elif item_choice == 'fireball_scroll':
                item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                    'Left-click a target tile for the fireball, or right-click to cancel.', colors.get('light_cyan')),
                                      damage=25, radius=3)
                item = Entity(x, y, '#', colors.get('red'), 'Fireball Scroll', render_order=RenderOrder.ITEM,
                              item=item_component)
            elif item_choice == 'confusion_scroll':
                item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
                    'Left-click an enemy to confuse it, or right-click to cancel.', colors.get('light_cyan')))
                item = Entity(x, y, '#', colors.get('light_pink'), 'Confusion Scroll', render_order=RenderOrder.ITEM,
                              item=item_component)
            else:
                item_component = Item(use_function=cast_lightning, damage=20, maximum_range=5)
                item = Entity(x, y, '#', colors.get('yellow'), 'Lightning Scroll', render_order=RenderOrder.ITEM,
                              item=item_component)

            entities.append(item)


class MapFabric:
    def __init__(self, game_map):
        self.game_map = game_map

    def make_draft(self):
        w = randint(UISettings.room_min_size, UISettings.room_max_size)
        h = randint(UISettings.room_min_size, UISettings.room_max_size)
        x = randint(0, UISettings.map_width - w - 1)
        y = randint(0, UISettings.map_height - h - 1)
        return Rect(x, y, w, h)

    def create_map(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.game_map.walkable[x, y] = True
                self.game_map.transparent[x, y] = True

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.game_map.walkable[x, y] = True
            self.game_map.transparent[x, y] = True

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.game_map.walkable[x, y] = True
            self.game_map.transparent[x, y] = True