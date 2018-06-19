

class BasicMonster:
    """
    The monsters in dungeons that hunt the hero and injury it.
    """

    def take_turn(self, target, obj_keeper):
        results = []
        monster = self.owner
        if obj_keeper.map.fov[monster.x, monster.y]:
            if monster.distance_to(target) >= 2:
                monster.move_towards(obj_keeper, target.x, target.y)
            elif target.fighter and target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
        return results
