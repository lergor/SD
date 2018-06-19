from src.utils import EquipmentSlots


class Equipment:
    """
    The class that holds both slots - the right hand ang the left one,
    and manages them and interactions with them.
    The Entity can toggle equipments it owns.
    """

    def __init__(self, main_hand=None, off_hand=None):
        self.main_hand = main_hand
        self.off_hand = off_hand

    @property
    def max_hp_bonus(self):
        bonus = 0
        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.max_hp_bonus
        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.max_hp_bonus

        return bonus

    @property
    def power_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.power_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.power_bonus

        return bonus

    @property
    def defense_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.defense_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.defense_bonus

        return bonus

    def toggle_equip(self, equip):
        results = []

        slot = equip.equippable.slot

        if slot == EquipmentSlots.MAIN_HAND:
            if self.main_hand == equip:
                self.main_hand = None
                results.append({'dequipped': equip})
            else:
                if self.main_hand:
                    results.append({'dequipped': self.main_hand})

                self.main_hand = equip
                results.append({'equipped': equip})
        elif slot == EquipmentSlots.OFF_HAND:
            if self.off_hand == equip:
                self.off_hand = None
                results.append({'dequipped': equip})
            else:
                if self.off_hand:
                    results.append({'dequipped': self.off_hand})

                self.off_hand = equip
                results.append({'equipped': equip})

        return results


class Equippable:
    """
    The class that holds an equipment in the right hand or in the left one.
    """

    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
