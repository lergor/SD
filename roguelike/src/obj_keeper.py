from src.entity import EntityFactory
from src.map import GameMap
from src.screen_switcher import *
from src.messages import Message


logger = get_logger(__name__)


class ObjectsKeeper:
    """
    Manages all objects of the game such as map and entities.
    Performs actions of the objects mostly for the player.
    """

    def init_objects(self):
        self.player = EntityFactory.create_entity('Player')
        self.entities = [self.player]
        self.map = GameMap(self.entities)
        logger.info('Created player: ({}, {})'.format(self.player.x, self.player.y))
        self.level = 1

    def get_blocking_entities_at(self, destination_x, destination_y):
        f = lambda e: e.blocks and e.x == destination_x and e.y == destination_y
        return find(f, self.entities)

    def player_move(self, action):
        dx, dy = action
        destination_x = self.player.x + dx
        destination_y = self.player.y + dy
        attack_results = []
        if self.map.walkable[destination_x, destination_y]:
            target = self.get_blocking_entities_at(destination_x, destination_y)
            if target:
                attack_results = self.player.fighter.attack(target)
            else:
                self.player.move(dx, dy)
        logger.info('Player: ({}, {})'.format(self.player.x, self.player.y))
        return attack_results

    def player_pickup(self):
        message = Message('There is nothing here to pick up.', UISettings.yellow)
        pickup_results = {'message': message}
        item = find(lambda e: e.item and self.player.overlap(e), self.entities)
        if item:
            pickup_results.update(self.player.inventory.add_item(item))
            if pickup_results.get('item_added'):
                logger.info('Player picks up {}'.format(item.name))
                self.entities.remove(item)
        return [pickup_results]

    def player_climb_up(self):
        recompute = False
        text = 'There are no stairs here.'
        color = UISettings.yellow
        stairs_entity = find(lambda e: e.stairs and self.player.overlap(e), self.entities)
        if stairs_entity:
            recompute = True
            text = 'You take a moment to rest, and recover your strength.'
            logger.info('Player goes downstairs: ({}, {})'.format(self.player.x, self.player.y))
            color = UISettings.light_violet
            self.next_floor()
        return [{'message': Message(text, color)}], recompute

    def next_floor(self):
        self.entities = [self.player]
        self.level += 1
        self.map = GameMap(self.entities, self.level)

    def player_level_up(self, level_up):
        if level_up == 'hp':
            self.player.fighter.base_max_hp += 20
            self.player.fighter.hp += 20
            ability = 'health'
        elif level_up == 'str':
            self.player.fighter.base_power += 1
            ability = 'power'
        elif level_up == 'def':
            self.player.fighter.base_defense += 1
            ability = 'defense'
        message = Message('Your {0} became stronger!'.format(ability), UISettings.green)
        logger.info('Player improves ' + ability)
        return [{'message': message}]

    def player_add_xp(self, xp):
        leveled_up = self.player.level.add_xp(xp)
        message = Message('You gain {0} experience points.'.format(xp))
        if leveled_up:
            level = self.player.level.current_level
            text = 'Your battle skills grow stronger! You reached level {0}'.format(level) + '!'
            logger.info('Player reached level {}'.format(level))
            message = Message(text, UISettings.yellow)
        return leveled_up, message

    def player_toggle_equip(self, equip):
        messages = []
        equip_results = self.player.equipment.toggle_equip(equip)
        for equip_result in equip_results:
            for action in ['equipped', 'dequipped']:
                item = equip_result.get(action)
                if item:
                    messages.append(Message('You {0} the {1}'.format(action,
                        item.name)))
                    logger.info('Player {} the {}'.format(action, item.name))
        return messages

    def player_inventory(self, index, state):
        action_result = []
        if state == GameStates.SHOW_INVENTORY:
            action_result = self.player.inventory.use(index)
        elif state == GameStates.DROP_INVENTORY:
            action_result = self.player.inventory.drop_item(index)
        return action_result

    def kill_entity(self, dead_entity):
        player_dead = False
        message = Message('{0} is dead!'.format(dead_entity.name.capitalize()),
                          UISettings.orange)
        logger.info('{} is dead.'.format(dead_entity.name))
        if dead_entity == self.player:
            player_dead = True
            message = Message('You died!', UISettings.red)
        dead_entity.make_dead()
        return message, player_dead

    def enemies_move(self):
        enemy_turn_results = []
        for entity in self.entities:
            if entity.ai:
                enemy_turn_results.extend(entity.ai.take_turn(self.player, self))
        return enemy_turn_results
