import tdl
from src.entity import EntityFabric
from src.map_utils import GameMap
from src.utils import *
from src.screen_handler import *
from src.world.characters.level import Level
from src.game_messages import Message


class ObjectsHolder:

    def init_objects(self):
        self.player = EntityFabric.create_player()
        self.entities = [self.player]
        self.map = GameMap(self.player)
        self.map.make_map(self.entities)
        self.level = Level()

    def get_blocking_entities_at_location(self, destination_x, destination_y):
        f = lambda e: e.blocks and e.x == destination_x and e.y == destination_y
        return find(f, self.entities)

    def player_move(self, action):
        dx, dy = action
        destination_x = self.player.x + dx
        destination_y = self.player.y + dy
        attack_results = []
        if self.map.walkable[destination_x, destination_y]:
            target = self.get_blocking_entities_at_location(destination_x, destination_y)
            if target:
                attack_results = self.player.fighter.attack(target)
            else:
                self.player.move(dx, dy)
        return attack_results

    def player_pickup(self):
        message = Message('There is nothing here to pick up.', UISettings.colors.get('yellow'))
        pickup_results = {'message': message}
        item = find(lambda e: e.item and self.player.overlap(e), self.entities)
        if item:
            pickup_results.update(self.player.inventory.add_item(item))
            if pickup_results.get('item_added'):
                self.entities.remove(item)
        return [pickup_results]

    def player_climb_up(self):
        recompute = False
        text = 'There are no stairs here.'
        color = UISettings.colors.get('yellow')
        stairs_entity = find(lambda e: e.stairs and self.player.overlap(e), self.entities)
        if stairs_entity:
            self.map, self.entities = self.map.next_floor(self.player, stairs_entity.stairs.floor)
            recompute = True
            text = 'You take a moment to rest, and recover your strength.'
            color = UISettings.colors.get('light_violet')
        return [{'message': Message(text, color)}], recompute

    def player_level_up(self, level_up):
        if level_up == 'hp':
            self.player.fighter.base_max_hp += 20
            self.player.fighter.hp += 20
        elif level_up == 'str':
            self.player.fighter.base_power += 1
        elif level_up == 'def':
            self.player.fighter.base_defense += 1

    def kill_entity(self, dead_entity):
        player_dead = False
        if dead_entity == self.player:
            player_dead = True
            message = Message('You died!', UISettings.colors.get('red'))
        else:
            message = Message('{0} is dead!'.format(dead_entity.name.capitalize()),
                                    UISettings.colors.get('orange'))
        dead_entity.make_dead()
        return message, player_dead

    def enemies_move(self, state):
        enemy_turn_results = []
        for entity in self.entities:
            if entity.ai:
                enemy_turn_results.extend(entity.ai.take_turn(self.player, self))
        return enemy_turn_results
