from random import randint

from src.game_messages import Message


class BasicMonster:
    def take_turn(self, target, ui):
        results = []

        monster = self.owner

        if ui.map.fov[monster.x, monster.y]:
            if monster.distance_to(target) >= 2:
                monster.move_towards(ui, target.x, target.y)

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results


class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, ui, target):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, ui.game_map, ui.entities)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name))})

        return results
