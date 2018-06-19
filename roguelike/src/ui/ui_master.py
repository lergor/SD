import tdl
from src.ui.screen_switcher import ScreenSwitcher
from src.utils import UISettings


class UIMaster:
    """
    The class that draws all entities and manage actions with the graphics.
    """

    def __init__(self, game):
        self.__game = game

    def init_ui(self):
        tdl.set_font(UISettings.game_font, greyscale=True, altLayout=True)
        self.__root_console = tdl.init(UISettings.screen_width, UISettings.screen_height,
                                       UISettings.window_title)
        self.__console = tdl.Console(UISettings.screen_width, UISettings.screen_height)
        self.__panel = tdl.Console(UISettings.screen_width, UISettings.panel_height)
        self.__screen_switcher = ScreenSwitcher(self.__console, self.__root_console)

    def show(self, screen_type, player=None):
        self.__screen_switcher.show(screen_type, player)

    def clear_view(self):
        self.__root_console.clear()
        self.__console.clear()
        self.__panel.clear()

    def renew_view(self):
        self.__render_all()
        tdl.flush()
        self.__clear_all_entities()

    def __clear_all_entities(self):
        for entity in self.__game.obj_keeper.entities:
            self.__console.draw_char(entity.x, entity.y, ' ', entity.color, bg=None)

    def __draw_all_entities(self):
        map = self.__game.obj_keeper.map
        entities = self.__game.obj_keeper.entities
        entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
        for entity in entities_in_render_order:
            entity.draw(map, self.__console)

    def __render_bar(self, x, y, name, value, maximum):
        bar_width = int(float(value) / maximum * UISettings.bar_width)
        self.__panel.draw_rect(x, y, UISettings.bar_width, 1, None, bg=UISettings.darker_red)
        if bar_width > 0:
            self.__panel.draw_rect(x, y, bar_width, 1, None, bg=UISettings.light_red)
        text = name + ': ' + str(value) + '/' + str(maximum)
        x_centered = x + int((UISettings.bar_width - len(text)) / 2)
        self.__panel.draw_str(x_centered, y, text, fg=UISettings.white, bg=None)

    def __recompute(self):
        map = self.__game.obj_keeper.map
        if self.__game.recompute:
            to_draw = map.recompute()
            for x, y, color in to_draw:
                self.__console.draw_char(x, y, None, fg=None, bg=color)

    def __render_all(self):
        state = self.__game.state
        self.__recompute()
        self.__draw_all_entities()
        self.__draw_info()
        self.show(state, player=self.__game.obj_keeper.player)

    def __draw_info(self):
        map = self.__game.obj_keeper.map
        player = self.__game.obj_keeper.player
        if player.fighter:
            self.__console.draw_str(1, UISettings.screen_height - 2, 'HP: {0:02}/{1:02}'.format(
                player.fighter.hp, player.fighter.max_hp))
        self.__root_console.blit(self.__console, 0, 0, UISettings.screen_width, UISettings.screen_height, 0, 0)
        self.__panel.clear(fg=UISettings.white, bg=UISettings.black)
        self.__draw_messages()
        if player.fighter:
            self.__render_bar(1, 1, 'HP', player.fighter.hp, player.fighter.max_hp)
        self.__panel.draw_str(1, 3, 'Dungeon Level: {0}'.format(map.dungeon_level),
                              fg=UISettings.white, bg=None)
        self.__root_console.blit(self.__panel, 0, UISettings.panel_y, UISettings.screen_width,
                                 UISettings.panel_height, 0, 0)

    def __draw_messages(self):
        message_log = self.__game.message_log
        y = 1
        for message in message_log.messages:
            self.__panel.draw_str(message_log.x, y, message.text, bg=None, fg=message.color)
            y += 1
