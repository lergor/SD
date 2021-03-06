from src.input_handler.input_handler import *
from src.game_objects.obj_keeper import *
from src.utils import *
from src.messages import *
from src.ui.ui_master import *


logger = get_logger(__name__)


class Game:
    """
    The main class of whole game.
    Holds InputHandler, ObjectsKeeper, UIMaster, MessageLog instances.
    Provides the correct process of the game. Has method run with an infinite loop.
    Processes the user input and manages all actions in the game.
    To start the game create the instance of the Game class and call the method 'run':

    game = Game()
    game.run()
    """

    def __init__(self):
        self.input_handler = InputHandler()
        self.state = GameStates.MENU
        self.obj_keeper = ObjectsKeeper()
        self.ui_master = UIMaster(self)
        self.message_log = MessageLog()

    def run(self):
        self.ui_master.init_ui()

        while not tdl.event.is_window_closed() and not self.state == GameStates.EXIT:

            if self.state == GameStates.MENU or self.state == GameStates.INFO:
                self.ui_master.show(self.state)
                flags = self.input_handler.catch_and_process_input(self.state)
                if flags.new_game:
                    self.__change_state(GameStates.PLAYER_TURN)
                elif flags.show_info_screen:
                    self.__change_state(GameStates.INFO)
                elif flags.exit:
                    if self.state != GameStates.INFO:
                        self.__change_state(GameStates.EXIT)
                    else:
                        self.__change_state(self.previous_state)
            elif self.state == GameStates.PLAYER_TURN:
                self.ui_master.clear_view()
                self.obj_keeper.init_objects()
                self.previous_state = GameStates.MENU
                self.__start_game()
                self.state = GameStates.MENU
                self.obj_keeper.player = None

    def __change_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state

    def __start_game(self):
        logger.info('Game started.')
        self.recompute = True

        while not tdl.event.is_window_closed() \
                and self.state != GameStates.EXIT:
            self.ui_master.renew_view()
            self.recompute = False
            flags = self.input_handler.catch_and_process_input(self.state)

            if flags.exit:
                if self.state in {GameStates.SHOW_INVENTORY,
                                  GameStates.DROP_INVENTORY,
                                  GameStates.CHARACTER_SCREEN,
                                  GameStates.INFO}:
                    logger.info(str(self.state) + ' --> ' + str(self.previous_state))
                    self.__change_state(self.previous_state)

                else:
                    self.__change_state(GameStates.EXIT)
                    logger.info('Game ended.')

            if self.state in {GameStates.PLAYER_TURN,
                              GameStates.SHOW_INVENTORY,
                              GameStates.DROP_INVENTORY,
                              GameStates.LEVEL_UP,
                              GameStates.INFO}:
                self.__player_turn(flags)

            if self.state == GameStates.ENEMY_TURN:
                self.__enemies_turn()

            if self.state in {GameStates.LEVEL_UP,
                              GameStates.SHOW_INVENTORY,
                              GameStates.DROP_INVENTORY,
                              GameStates.INFO}:
                self.ui_master.show(self.state, player=self.obj_keeper.player)

    def __player_turn(self, flags):
        player_turn_results, action_result = [], []

        if flags.show_inventory:
            self.__change_state(GameStates.SHOW_INVENTORY)

        if flags.drop_inventory:
            self.__change_state(GameStates.DROP_INVENTORY)

        if flags.show_character_screen:
            self.__change_state(GameStates.CHARACTER_SCREEN)

        if flags.show_info_screen:
            self.__change_state(GameStates.INFO)

        if flags.move:
            action_result = self.obj_keeper.player_move(flags.move)
            self.recompute = not action_result
            self.__change_state(GameStates.ENEMY_TURN)

        if flags.pickup and self.state == GameStates.PLAYER_TURN:
            action_result = self.obj_keeper.player_pickup()

        if flags.take_stairs:
            action_result, self.recompute = self.obj_keeper.player_go_downstairs()
            if self.recompute:
                self.ui_master.clear_view()

        if flags.wait:
            self.__change_state(GameStates.ENEMY_TURN)

        if flags.inventory_index is not None and self.previous_state != GameStates.PLAYER_DEAD:
            action_result = self.obj_keeper.player_inventory(flags.inventory_index, self.state)

        if flags.level_up:
            action_result = self.obj_keeper.player_level_up(flags.level_up)
            self.state = self.previous_state

        player_turn_results.extend(action_result)
        self.__process_player_results(player_turn_results)

    def __enemies_turn(self):
        turn_results = self.obj_keeper.enemies_move()
        self.__process_enemies_results(turn_results)

    def __process_enemies_results(self, turn_results):
        for turn_result in turn_results:
            flags = Flags(turn_result)
            self.message_log.add_message(flags.message)

            if flags.dead_entity:
                message, player_dead = self.obj_keeper.kill_entity(flags.dead_entity)
                self.message_log.add_message(message)
                if player_dead:
                    self.__change_state(GameStates.PLAYER_DEAD)
                    break
        else:
            self.__change_state(GameStates.PLAYER_TURN)

    def __process_player_results(self, turn_results):
        for turn_result in turn_results:
            flags = Flags(turn_result)
            self.message_log.add_message(flags.message)

            if flags.dead_entity:
                message, player_dead = self.obj_keeper.kill_entity(flags.dead_entity)
                if player_dead:
                    self.__change_state(GameStates.PLAYER_DEAD)
                    break
                self.message_log.add_message(message)

            if flags.item_added or flags.item_consumed or flags.item_dropped:
                if flags.item_dropped:
                    self.obj_keeper.entities.append(flags.item_dropped)
                self.__change_state(GameStates.ENEMY_TURN)

            if flags.equip:
                messages = self.obj_keeper.player_toggle_equip(flags.equip)
                for message in messages:
                    self.message_log.add_message(message)
                self.__change_state(GameStates.ENEMY_TURN)

            if flags.xp:
                leveled_up, message = self.obj_keeper.player_add_xp(flags.xp)
                self.message_log.add_message(message)
                if leveled_up:
                    self.__change_state(GameStates.LEVEL_UP)