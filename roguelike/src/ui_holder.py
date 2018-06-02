import tdl

from src.screen_handler import ScreenHandler
from src.utils import UISettings, GameStates


class UIHolder:

    def __init__(self, game):
        self.game = game

    def init_ui(self):
        tdl.set_font(UISettings.game_font, greyscale=True, altLayout=True)
        self.root_console = tdl.init(UISettings.screen_width, UISettings.screen_height,
                                     UISettings.window_title)
        self.console = tdl.Console(UISettings.screen_width, UISettings.screen_height)
        self.panel = tdl.Console(UISettings.screen_width, UISettings.panel_height)
        self.screen_handler = ScreenHandler(self.console, self.root_console)

    def show(self, screen_type, **kwargs):
        self.screen_handler.show(screen_type, **kwargs)

    def clear_view(self):
        self.root_console.clear()
        self.console.clear()
        self.panel.clear()

    def renew_view(self):
        self.render_all()
        tdl.flush()
        self.clear_all_entities()

    def clear_all_entities(self):
        for entity in self.game.obj_holder.entities:
            self.console.draw_char(entity.x, entity.y, ' ', entity.color, bg=None)

    def render_bar(self, x, y, name, value, maximum):
        bar_width = int(float(value) / maximum * UISettings.bar_width)
        self.panel.draw_rect(x, y, UISettings.bar_width, 1, None, bg=UISettings.colors.get('darker_red'))
        if bar_width > 0:
            self.panel.draw_rect(x, y, bar_width, 1, None, bg=UISettings.colors.get('light_red'))
        text = name + ': ' + str(value) + '/' + str(maximum)
        x_centered = x + int((UISettings.bar_width - len(text)) / 2)

        self.panel.draw_str(x_centered, y, text, fg=UISettings.colors.get('white'), bg=None)

    def render_all(self):
        map = self.game.obj_holder.map
        player = self.game.obj_holder.player
        entities = self.game.obj_holder.entities
        message_log = self.game.message_log
        state = self.game.state
        if self.game.recompute:
            map.compute_fov(player.x, player.y,fov=UISettings.fov_algorithm,
                            radius=UISettings.fov_radius, light_walls=UISettings.fov_light_walls)

            for x, y in map:
                wall = not map.transparent[x, y]

                if map.fov[x, y]:
                    if wall:
                        color = UISettings.colors.get('light_wall')
                    else:
                        color = UISettings.colors.get('light_ground')
                    self.console.draw_char(x, y, None, fg=None, bg=color)
                    map.explored[x][y] = True
                elif map.explored[x][y]:
                    if wall:
                        color = UISettings.colors.get('dark_wall')
                    else:
                        color = UISettings.colors.get('dark_ground')
                    self.console.draw_char(x, y, None, fg=None, bg=color)

        entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

        for entity in entities_in_render_order:
            entity.draw(map, self.console)
        if player.fighter:
            self.console.draw_str(1, UISettings.screen_height - 2, 'HP: {0:02}/{1:02}'.format(
                player.fighter.hp, player.fighter.max_hp))

        self.root_console.blit(self.console, 0, 0, UISettings.screen_width, UISettings.screen_height, 0, 0)

        self.panel.clear(fg=UISettings.colors.get('white'), bg=UISettings.colors.get('black'))
        y = 1
        for message in message_log.messages:
            self.panel.draw_str(message_log.x, y, message.text, bg=None, fg=message.color)
            y += 1
        if  player.fighter:
            self.render_bar(1, 1, 'HP', player.fighter.hp, player.fighter.max_hp)

        self.panel.draw_str(1, 3, 'Dungeon Level: {0}'.format(map.dungeon_level),
                            fg=UISettings.colors.get('white'), bg=None)

        self.root_console.blit(self.panel, 0, UISettings.panel_y, UISettings.screen_width,
                               UISettings.panel_height, 0, 0)

        if state in {GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY}:
            self.screen_handler.inventory_menu(player)

        elif state == GameStates.CHARACTER_SCREEN:
            self.screen_handler.character_screen(self.root_console, player, 30, 10,
                                                 UISettings.screen_width, UISettings.screen_height)

