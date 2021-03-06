from src.messages import Message
from src.utils import get_logger

logger = get_logger(__name__)


class Fighter:
    """
    The role of Fighter for an entity.
    Fighter has a health points, a power, a defense.
    Fighter can attack, be healed and take damage from enemies.
    """

    def __init__(self, hp, defense, power, xp=0):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp

    @property
    def max_hp(self):
        bonus = 0
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        return self.base_max_hp + bonus

    @property
    def power(self):
        bonus = 0
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        return self.base_power + bonus

    @property
    def defense(self):
        bonus = 0
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        return self.base_defense + bonus

    def take_damage(self, amount):
        results = []
        self.hp -= amount
        if self.hp <= 0:
            results.append({'dead': self.owner, 'xp': self.xp})
        return results

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []
        damage = self.power - target.fighter.defense
        text = '{0} attacks {1} but does no damage.'.format(
            self.owner.name.capitalize(), target.name)
        if damage > 0:
            text = '{0} attacks {1} for {2} hit points.'.format(
                self.owner.name.capitalize(), target.name, str(damage))
            results.extend(target.fighter.take_damage(damage))
        logger.info(text)
        results.append({'message': Message(text)})
        return results
