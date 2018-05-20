import tdl

from src.entity import EntityFabric
from src.game_states import GameStates
from src.map_utils import GameMap
from src.utils import *
from src.screen_handler import *

class UIHolder:

    def init_ui(self):
        self.player = EntityFabric.create_player()
        self.entities = [self.player]
        self.map = GameMap(self.player)
        self.map.make_map(self.entities)
        tdl.set_font(UISettings.game_font, greyscale=True, altLayout=True)
        self.root_console = tdl.init(UISettings.screen_width, UISettings.screen_height,
                                     UISettings.window_title)
        self.console = tdl.Console(UISettings.screen_width, UISettings.screen_height)
        self.panel = tdl.Console(UISettings.screen_width, UISettings.panel_height)
        self.screen_handler = ScreenHandler(self.console, self.root_console)

    def show(self, screen_type):
        self.screen_handler.show(screen_type)

    def clear_view(self):
        self.root_console.clear()
        self.console.clear()
        self.panel.clear()

    def clear_all(self):
        for entity in self.entities:
            self.console.draw_char(entity.x, entity.y, ' ', entity.color, bg=None)

    def render_all(self, fov_recompute, message_log, state):
        if fov_recompute:
            self.map.compute_fov(self.player.x, self.player.y, 
                                 fov=UISettings.fov_algorithm,
                                 radius=UISettings.fov_radius,
                                 light_walls=UISettings.fov_light_walls)
            
            for x, y in self.map:
                wall = not self.map.transparent[x, y]

                if self.map.fov[x, y]:
                    if wall:
                        color = UISettings.colors.get('light_wall')
                    else:
                        color = UISettings.colors.get('light_ground')
                    self.console.draw_char(x, y, None, fg=None, bg=color)
                    self.map.explored[x][y] = True
                elif self.map.explored[x][y]:
                    if wall:
                        color = UISettings.colors.get('dark_wall')
                    else:
                        color = UISettings.colors.get('dark_ground')
                    self.console.draw_char(x, y, None, fg=None, bg=color)

        entities_in_render_order = sorted(self.entities, key=lambda x: x.render_order.value)

        for entity in entities_in_render_order:
            entity.draw(self.map, self.console)

        self.console.draw_str(1, UISettings.screen_height - 2, 'HP: {0:02}/{1:02}'.format(
            self.player.fighter.hp, self.player.fighter.max_hp))

        self.root_console.blit(self.console, 0, 0, UISettings.screen_width, UISettings.screen_height, 0, 0)

        self.panel.clear(fg=UISettings.colors.get('white'), bg=UISettings.colors.get('black'))
        y = 1
        for message in message_log.messages:
            self.panel.draw_str(message_log.x, y, message.text, bg=None, fg=message.color)
            y += 1

        self.render_bar(1, 1, 'HP', self.player.fighter.hp, self.player.fighter.max_hp)

        self.panel.draw_str(1, 3, 'Dungeon Level: {0}'.format(self.map.dungeon_level),
                            fg=UISettings.colors.get('white'), bg=None)

        self.root_console.blit(self.panel, 0, UISettings.panel_y, UISettings.screen_width,
                               UISettings.panel_height, 0, 0)

        if state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
            self.screen_handler.inventory_menu(self.player)

        elif state == GameStates.CHARACTER_SCREEN:
            self.screen_handler.character_screen(self.root_console, self.player, 30, 10,
                                              UISettings.screen_width, UISettings.screen_height)

    def render_bar(self, x, y, name, value, maximum):
        bar_width = int(float(value) / maximum * UISettings.bar_width)
        self.panel.draw_rect(x, y, UISettings.bar_width, 1, None, bg=UISettings.colors.get('darker_red'))
        if bar_width > 0:
            self.panel.draw_rect(x, y, bar_width, 1, None, bg=UISettings.colors.get('light_red'))
        text = name + ': ' + str(value) + '/' + str(maximum)
        x_centered = x + int((UISettings.bar_width - len(text)) / 2)

        self.panel.draw_str(x_centered, y, text, fg=UISettings.colors.get('white'), bg=None)


    def get_blocking_entities_at_location(self, destination_x, destination_y):
        for entity in self.entities:
            if entity.blocks and entity.x == destination_x and entity.y == destination_y:
                return entity
        return None

    def player_move(self, action):
        dx, dy = action
        destination_x = self.player.x + dx
        destination_y = self.player.y + dy

        if self.map.walkable[destination_x, destination_y]:
            attack_results = None
            target = self.get_blocking_entities_at_location(destination_x, destination_y)
            if target:
                attack_results = self.player.fighter.attack(target)
            else:
                self.player.move(dx, dy)
            return attack_results

    def pickup(self):
        pickup_results = None
        for entity in self.entities:
            if entity.item and entity.x == self.player.x and entity.y == self.player.y:
                pickup_results = self.player.inventory.add_item(entity, UISettings.colors)
                break
        return pickup_results

