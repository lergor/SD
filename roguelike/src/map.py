from tdl.map import Map
from random import randint
from src.entity import EntityFabric
from src.utils import *
from numpy.random import choice


class GameMap(Map):

    def __init__(self, entities, level=1):
        super().__init__(UISettings.map_width, UISettings.map_height)
        self.player = entities[0]
        self.entities = entities
        self.dungeon_level = level
        self.explored = [[False for y in range(UISettings.map_height)]
                         for x in range(UISettings.map_width)]
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
                new_room.place_entities(self.dungeon_level, self.entities)
                rooms.append(new_room)
        self.player.x, self.player.y = rooms[0].center()
        down_stairs = EntityFabric.make_stairs(rooms[-1])
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


class Room:

    def __init__(self):
        w = randint(UISettings.room_min_size, UISettings.room_max_size)
        h = randint(UISettings.room_min_size, UISettings.room_max_size)
        self.x1 = randint(0, UISettings.map_width - w - 1)
        self.y1 = randint(0, UISettings.map_height - h - 1)
        self.x2 = self.x1 + w
        self.y2 = self.y1 + h
        self.center_x = int((self.x1 + self.x2) / 2)
        self.center_y = int((self.y1 + self.y2) / 2)

    def center(self):
        return self.center_x, self.center_y

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def place_entities(self, level, entities):
        monsters_per_room = self.__from_dungeon_level([[2, 1], [3, 4], [5, 7]], level)
        items_per_room = self.__from_dungeon_level([[1, 1], [2, 4]], level)
        monster_chances = {
            'Spider': 80,
            'Bat': self.__from_dungeon_level([[15, 3], [30, 5], [60, 7]], level),
            'Snake': self.__from_dungeon_level([[0, 3], [10, 5], [50, 7], [80, 10]], level)
        }
        # item_chances = {
        #     'Healing potion': 35,
        #     'Sword': self.__from_dungeon_level([[5, 4]], level),
        #     'Shield': self.__from_dungeon_level([[15, 8]], level)
        # }
        item_chances = {
            'Healing potion': 20,
            'Sword': 100,
            'Shield': 20
        }
        self.__place(monsters_per_room, monster_chances, entities)
        self.__place(items_per_room, item_chances, entities)

    def __from_dungeon_level(self, table, level):
        for (value, level_value) in reversed(table):
            if level >= level_value:
                return value
        return 0

    def __place(self, num_per_room, chances, entities):
        amount = randint(0, num_per_room)
        for i in range(amount):
            x = randint(self.x1 + 1, self.x2 - 1)
            y = randint(self.y1 + 1, self.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster_choice = self.__choice_from_dict(chances)
                monster = EntityFabric.make_entity(monster_choice, x, y)
                entities.append(monster)

    def __choice_from_dict(elf, choice_dict):
        choices = list(choice_dict.keys())
        chances = list(choice_dict.values())
        decimal_chances = [chance / sum(chances) for chance in chances]
        return choice(choices, p=decimal_chances)
