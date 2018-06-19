from tdl.map import Map
from random import randint
from src.game_objects.entity import EntityFactory
from src.utils import *
from numpy.random import choice


logger = get_logger(__name__)


class GameMap(Map):
    """
    The class that represents a map of the game on the current level.
    Also initiates and places all entities on the map.
    """

    def __init__(self, entities, level=1):
        super().__init__(UISettings.map_width, UISettings.map_height)
        self.player = entities[0]
        self.entities = entities
        self.dungeon_level = level
        self.explored = [[False for y in range(UISettings.map_height)]
                         for x in range(UISettings.map_width)]
        logger.info('Map created: level {}.'.format(level))
        self.__make_map()

    def __make_map(self):
        rooms = []
        for r in range(UISettings.max_rooms):
            new_room = Room()
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                self.__mark_on_map(new_room)
                if len(rooms) > 0:
                    self.__connect_rooms(rooms[-1], new_room)
                self.__place_entities(new_room)
                rooms.append(new_room)
        self.player.x, self.player.y = rooms[0].center()
        x, y = rooms[-1].center()
        down_stairs = EntityFactory.create_entity('Stairs', x, y)
        logger.info('Rooms created: {}.'.format(len(rooms)))
        self.entities.append(down_stairs)

    def __mark_on_map(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.walkable[x, y] = True
                self.transparent[x, y] = True

    def __connect_rooms(self, room1, room2):
        x1, y1 = room1.center()
        x2, y2 = room2.center()
        if randint(0, 1):
            self.__create_h_tunnel(x1, x2, y1)
            self.__create_v_tunnel(y1, y2, x2)
        else:
            self.__create_v_tunnel(y1, y2, x1)
            self.__create_h_tunnel(x1, x2, y2)

    def __create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.walkable[x, y] = True
            self.transparent[x, y] = True

    def __create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.walkable[x, y] = True
            self.transparent[x, y] = True

    def __place_entities(self, room):
        monsters_per_room = self.__from_dungeon_level([[2, 1], [3, 4], [5, 7]])
        items_per_room = self.__from_dungeon_level([[1, 1], [2, 4]])
        monster_chances = {
            'Spider': 80,
            'Bat': self.__from_dungeon_level([[15, 3], [30, 5], [60, 7]]),
            'Snake': self.__from_dungeon_level([[0, 3], [10, 5], [50, 7], [80, 10]])
        }
        item_chances = {
            'Healing potion': 35,
            'Sword': self.__from_dungeon_level([[5, 4]]),
            'Shield': self.__from_dungeon_level([[15, 8]])
        }
        num = len(self.entities)
        self.__place(room, monsters_per_room, monster_chances)
        logger.info('Monsters created: {}.'.format(len(self.entities) - num))
        num = len(self.entities)
        self.__place(room, items_per_room, item_chances)
        logger.info('Items created: {}.'.format(len(self.entities) - num))

    def __from_dungeon_level(self, table):
        for (value, level_value) in reversed(table):
            if self.dungeon_level >= level_value:
                return value
        return 0

    def __place(self, room, num_per_room, chances):
        amount = randint(0, num_per_room)
        for i in range(amount):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in self.entities if entity.x == x and entity.y == y]):
                monster_choice = self.__choice_from_dict(chances)
                monster = EntityFactory.create_entity(monster_choice, x, y)
                self.entities.append(monster)

    def __choice_from_dict(elf, choice_dict):
        choices = list(choice_dict.keys())
        chances = list(choice_dict.values())
        decimal_chances = [chance / sum(chances) for chance in chances]
        return choice(choices, p=decimal_chances)

    def recompute(self):
        to_draw = []
        self.compute_fov(self.player.x, self.player.y, 'BASIC', 10)
        for x, y in self:
            wall = not self.transparent[x, y]
            if self.fov[x, y]:
                color = UISettings.light_ground
                if wall:
                    color = UISettings.light_wall
                self.explored[x][y] = True
                to_draw.append((x, y, color))
            elif self.explored[x][y]:
                if wall:
                    color = UISettings.dark_wall
                else:
                    color = UISettings.dark_ground
                to_draw.append((x, y, color))
        return to_draw


class Room:
    """
    The class for one room in the dungeon.
    """

    def __init__(self):
        w = randint(UISettings.room_min_size, UISettings.room_max_size)
        h = randint(UISettings.room_min_size, UISettings.room_max_size)
        self.x1 = randint(0, UISettings.map_width - w - 1)
        self.y1 = randint(0, UISettings.map_height - h - 1)
        self.x2 = self.x1 + w
        self.y2 = self.y1 + h

    def center(self):
        return int((self.x1 + self.x2) / 2), int((self.y1 + self.y2) / 2)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
