from src.input_handler import *
from src.obj_holder import *
from src.utils import *
from src.messages import *
from src.world.characters.inventory import *
from src.ui_holder import *


class Game:

    def __init__(self):
        self.input_handler = InputHandler()
        self.state = GameStates.MENU
        self.obj_holder = ObjectsHolder()
        self.ui_holder = UIHolder(self)
        self.message_log = MessageLog()

    def run(self):
        self.obj_holder.init_objects()
        self.ui_holder.init_ui()

        while not tdl.event.is_window_closed() and not self.state == GameStates.EXIT:

            if self.state == GameStates.MENU:
                self.ui_holder.show(ScreenType.MAIN)
                flags = self.input_handler.catch_and_process_input(self.state)
                if flags.new_game:
                    self.state = GameStates.PLAYER_TURN
                elif flags.info:
                    self.state = GameStates.INFO
                elif flags.exit:
                    self.state = GameStates.EXIT
            else:
                self.ui_holder.clear_view()
                self.__start_game()
                self.state = GameStates.MENU

    def __change_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state

    def __start_game(self):
        self.recompute = True
        self.previous_state = self.state

        while not tdl.event.is_window_closed() \
                and self.state not in {GameStates.PLAYER_DEAD, GameStates.EXIT}:
            self.ui_holder.renew_view()
            self.recompute = False
            flags = self.input_handler.catch_and_process_input(self.state)

            if flags.show_character_screen:
                self.__change_state(GameStates.CHARACTER_SCREEN)

            if flags.exit:
                if self.state in {GameStates.SHOW_INVENTORY,
                                  GameStates.DROP_INVENTORY,
                                  GameStates.CHARACTER_SCREEN}:
                    self.state = self.previous_state
                else:
                    self.__change_state(GameStates.EXIT)

            if self.state in {GameStates.PLAYER_TURN,
                              GameStates.SHOW_INVENTORY,
                              GameStates.DROP_INVENTORY}:
                self.player_turn(flags)

            if self.state == GameStates.ENEMY_TURN:
                self.enemy_turn()

            if self.state == GameStates.LEVEL_UP:
                self.ui_holder.show(ScreenType.LEVEL_UP, player=self.obj_holder.player)

    def player_turn(self, flags):
        player_turn_results, action_result = [], []

        if flags.move:
            action_result = self.obj_holder.player_move(flags.move)
            self.recompute = not action_result
            self.__change_state(GameStates.ENEMY_TURN)

        if flags.pickup and self.state == GameStates.PLAYER_TURN:
            action_result = self.obj_holder.player_pickup()

        if flags.take_stairs:
            action_result, self.recompute = self.obj_holder.player_climb_up()
            if self.recompute:
                self.ui_holder.clear_view()
                self.ui_holder.renew_view()

        if flags.wait:
            self.__change_state(GameStates.ENEMY_TURN)

        if flags.show_inventory:
            self.__change_state(GameStates.SHOW_INVENTORY)

        if flags.drop_inventory:
            self.__change_state(GameStates.DROP_INVENTORY)

        if flags.inventory_index and self.previous_state != GameStates.PLAYER_DEAD:
            if self.state == GameStates.SHOW_INVENTORY:
                action_result = self.obj_holder.player.inventory.use(flags.inventory_index)
            elif self.state == GameStates.DROP_INVENTORY:
                action_result = self.obj_holder.player.inventory.drop_item(flags.inventory_index)

        if flags.level_up:
            self.obj_holder.player_level_up(flags.level_up)
            self.state = self.previous_state

        player_turn_results.extend(action_result)
        self.__process_results(player_turn_results)

    def enemy_turn(self):
        turn_results = self.obj_holder.enemies_move(self.state)
        self.__process_results(turn_results)
        self.__change_state(GameStates.PLAYER_TURN)

    def __process_results(self, turn_results):
        for turn_result in turn_results:
            flags = Flags(turn_result)
            self.message_log.add_message(flags.message)

            if flags.dead_entity:
                message, player_dead = self.obj_holder.kill_entity(flags.dead_entity)
                if player_dead:
                    self.__change_state(GameStates.PLAYER_DEAD)
                self.message_log.add_message(message)

            if flags.item_added or flags.item_consumed or flags.item_dropped:
                if flags.item_dropped:
                    self.obj_holder.entities.append(flags.item_dropped)
                self.__change_state(GameStates.ENEMY_TURN)

            if flags.equip:
                equip_results = self.obj_holder.player.equipment.toggle_equip(flags.equip)
                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')
                    if equipped:
                        self.message_log.add_message(Message('You equipped the {0}'.format(
                            equipped.name)))
                    if dequipped:
                        self.message_log.add_message(Message('You dequipped the {0}'.format(
                            dequipped.name)))
                self.__change_state(GameStates.ENEMY_TURN)

            if flags.xp:
                leveled_up = self.obj_holder.player.level.add_xp(flags.xp)
                message = Message('You gain {0} experience points.'.format(flags.xp))
                self.message_log.add_message(message)

                if leveled_up:
                    text = 'Your battle skills grow stronger! You reached level {0}'.format(
                        self.obj_holder.player.level.current_level) + '!'
                    self.message_log.add_message(Message(text, UISettings.colors.get('yellow')))
                    print('LEVEL_UP')
                    self.__change_state(GameStates.LEVEL_UP)

