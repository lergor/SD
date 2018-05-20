from src.input_handler import *
from src.death_functions import kill_monster, kill_player
from src.ui_holder import *
from src.utils import *
from src.game_messages import *
from src.map_utils import *
from src.world.characters.inventory import *



class Game:

    def __init__(self):
        self.input_handler = InputHandler()
        self.state = None
        self.message_log = None
        self.show_main_menu = True
        self.ui_holder = UIHolder()

    def catch_input(self):
        for event in tdl.event.get():
            if event.type == 'KEYDOWN':
                return event
        return None


    def run(self):
        self.ui_holder.init_ui()

        while not tdl.event.is_window_closed():
            user_input = self.catch_input()

            if self.show_main_menu:
                self.state = GameStates.MENU
                self.ui_holder.show(MenuType.MAIN)
                flags = self.input_handler.handle(user_input, self.state)
                if flags.new_game:
                    self.message_log = MessageLog()
                    self.state = GameStates.PLAYERS_TURN
                    self.show_main_menu = False
                elif flags.info:
                        pass
                elif flags.exit:
                    break
            else:
                self.ui_holder.clear_view()
                self.__start_game()
                self.show_main_menu = True

    def __start_game(self):
        tdl.set_font(UISettings.game_font, greyscale=True, altLayout=True)
        fov_recompute = True
        previous_game_state = self.state

        while not tdl.event.is_window_closed():
            self.ui_holder.render_all(fov_recompute, self.message_log, self.state)
            tdl.flush()
            self.ui_holder.clear_all()
            fov_recompute = False

            user_input = self.catch_input()
            flags = self.input_handler.handle(user_input, self.state)
            player_turn_results = []

            if flags.move and self.state == GameStates.PLAYERS_TURN:
                attack_results = self.ui_holder.player_move(flags.move)
                if attack_results:
                    player_turn_results.extend(attack_results)
                else:
                    fov_recompute = True
                    self.state = GameStates.ENEMY_TURN

            elif flags.wait:
                self.state = GameStates.ENEMY_TURN

            elif flags.pickup and self.state == GameStates.PLAYERS_TURN:
                pickup_results = self.ui_holder.pickup()
                if pickup_results:
                    player_turn_results.extend(pickup_results)
                else:
                    self.message_log.add_message(Message('There is nothing here to pick up.',
                                                    UISettings.colors.get('yellow')))

            if flags.show_inventory:
                previous_game_state = self.state
                self.state = GameStates.SHOW_INVENTORY

            if flags.drop_inventory:
                previous_game_state = self.state
                self.state = GameStates.DROP_INVENTORY

            if flags.inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and \
                    flags.inventory_index < len(self.ui_holder.player.inventory.items):
                item = self.ui_holder.player.inventory.items[flags.inventory_index]

                if self.state == GameStates.SHOW_INVENTORY:
                    player_turn_results.extend(self.ui_holder.player.inventory.use(item, UISettings.colors,
                                                                    entities=self.ui_holder.entities,
                                                                    game_map=self.ui_holder.map))
                elif self.state == GameStates.DROP_INVENTORY:
                    player_turn_results.extend(self.ui_holder.player.inventory.drop_item(item, UISettings.colors))

            if flags.take_stairs and self.state == GameStates.PLAYERS_TURN:
                for entity in self.entities:
                    if entity.stairs and entity.x == self.ui_holder.player.x and entity.y == self.ui_holder.player.y:
                        self.ui_holder.map, self.entities = self.ui_holder.map.next_floor(self.ui_holder.player,
                                                                                          self.message_log,
                                                                 entity.stairs.floor)
                        fov_recompute = True
                        self.ui_holder.console.clear()

                        break
                else:
                    self.message_log.add_message(Message('There are no stairs here.',
                                                    UISettings.colors.get('yellow')))

            if flags.level_up:
                if flags.level_up == 'hp':
                    self.ui_holder.player.fighter.base_max_hp += 20
                    self.ui_holder.player.fighter.hp += 20
                elif flags.level_up == 'str':
                    self.ui_holder.player.fighter.base_power += 1
                elif flags.level_up == 'def':
                    self.ui_holder.player.fighter.base_defense += 1

                self.state = previous_game_state

            if flags.show_character_screen:
                previous_game_state = self.state
                self.state = GameStates.CHARACTER_SCREEN

            if flags.exit:
                if self.state in {GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY,
                                  GameStates.CHARACTER_SCREEN}:
                    self.state = previous_game_state
                else:
                    return True

            if flags.fullscreen:
                tdl.set_fullscreen(not tdl.get_fullscreen())

            for player_turn_result in player_turn_results:
                message = player_turn_result.get('message')
                dead_entity = player_turn_result.get('dead')
                item_added = player_turn_result.get('item_added')
                item_consumed = player_turn_result.get('consumed')
                item_dropped = player_turn_result.get('item_dropped')
                equip = player_turn_result.get('equip')
                xp = player_turn_result.get('xp')

                if message:
                    self.message_log.add_message(message)

                if dead_entity:
                    if dead_entity == self.ui_holder.player:
                        message, self.state = kill_player(dead_entity, UISettings.colors)
                    else:
                        message = kill_monster(dead_entity, UISettings.colors)
                    self.message_log.add_message(message)

                if item_added:
                    self.entities.remove(item_added)

                    self.state = GameStates.ENEMY_TURN

                if item_consumed:
                    self.state = GameStates.ENEMY_TURN

                if item_dropped:
                    self.entities.append(item_dropped)
                    self.state = GameStates.ENEMY_TURN

                if equip:
                    equip_results = self.ui_holder.player.equipment.toggle_equip(equip)

                    for equip_result in equip_results:
                        equipped = equip_result.get('equipped')
                        dequipped = equip_result.get('dequipped')

                        if equipped:
                            self.message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

                        if dequipped:
                            self.message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

                    self.state = GameStates.ENEMY_TURN

                if xp:
                    leveled_up = self.ui_holder.player.level.add_xp(xp)
                    self.message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

                    if leveled_up:
                        self.message_log.add_message(Message(
                            'Your battle skills grow stronger! You reached level {0}'.format(
                                self.ui_holder.player.level.current_level) + '!',
                            UISettings.colors.get('yellow')))
                        previous_game_state = self.state
                        self.state = GameStates.LEVEL_UP

            if self.state == GameStates.ENEMY_TURN:
                for entity in self.ui_holder.entities:
                    if entity.ai:
                        enemy_turn_results = entity.ai.take_turn(self.ui_holder.player, self.ui_holder)

                        for enemy_turn_result in enemy_turn_results:
                            message = enemy_turn_result.get('message')
                            dead_entity = enemy_turn_result.get('dead')

                            if message:
                                self.message_log.add_message(message)

                            if dead_entity:
                                if dead_entity == self.ui_holder.player:
                                    message, self.state = kill_player(dead_entity, UISettings.colors)
                                else:
                                    message = kill_monster(dead_entity, UISettings.colors)

                                self.message_log.add_message(message)

                                if self.state == GameStates.PLAYER_DEAD:
                                    break

                        if self.state == GameStates.PLAYER_DEAD:
                            break
                        else:
                            self.state = GameStates.PLAYERS_TURN
