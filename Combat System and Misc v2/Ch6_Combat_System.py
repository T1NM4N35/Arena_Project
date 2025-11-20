# Ch6_Combat_System.py

import random
from Ch6_Weapons_System import WEAPONS

# -------------------------
# Geometry helpers
# -------------------------
def dx_dy(a, b):
    return b[0] - a[0], b[1] - a[1]

def is_horizontal(a, b):
    return a[1] == b[1]

def is_vertical(a, b):
    return a[0] == b[0]

def is_diagonal(a, b):
    dx, dy = dx_dy(a, b)
    return abs(dx) == abs(dy) and dx != 0

def manhattan(a, b):
    dx, dy = dx_dy(a, b)
    return abs(dx) + abs(dy)

def adjacent_any(a, b):
    dx, dy = dx_dy(a, b)
    return max(abs(dx), abs(dy)) == 1 and not (dx == 0 and dy == 0)

def adjacent_cardinal(a, b):
    dx, dy = dx_dy(a, b)
    return abs(dx) + abs(dy) == 1

def straight_cardinal_exact(a, b, dist):
    dx, dy = dx_dy(a, b)
    return (abs(dx) == dist and dy == 0) or (abs(dy) == dist and dx == 0)

def in_straight_or_diagonal(a, b):
    return is_horizontal(a, b) or is_vertical(a, b) or is_diagonal(a, b)

# -------------------------
# Combat System
# -------------------------
class CombatSystem:

    @staticmethod
    def calculate_dodge_chance(player, weapon_name):
        dex = player.skills.get("Dexterity", 0)
        luck = player.skills.get("Luck", 0)
        weapon = WEAPONS[weapon_name]

        base_dodge = 0.03 * dex
        weight = weapon.get("weight", 2)
        weapon_bonus = max(0.0, 0.08 - 0.02 * weight)
        luck_bonus = 0.015 * luck

        return min(base_dodge + weapon_bonus + luck_bonus, 0.70)

    @staticmethod
    def calculate_block_chance(player, weapon_name):
        if weapon_name != "Shield":
            return 0.0
        base_block = 0.30
        luck_bonus = 0.015 * player.skills.get("Luck", 0)
        return min(base_block + luck_bonus, 0.60)

    @staticmethod
    def calculate_damage(player, weapon_name):
        str_stat = player.skills.get("Strength", 0)
        dex = player.skills.get("Dexterity", 0)
        luck = player.skills.get("Luck", 0)
        weapon = WEAPONS[weapon_name]

        base_damage = 2 + (0.8 * str_stat) + (0.2 * dex)
        base_damage += weapon.get("base_damage_mod", 0)

        # Shield has lower damage (we'll ensure by base_damage_mod=0 and low final)
        if weapon_name == "Shield":
            base_damage = max(1, int(base_damage * 0.6))

        crit_chance = min(0.03 * luck, 1.0)
        crit = random.random() < crit_chance

        if crit:
            final = int(base_damage * 1.5)
        else:
            final = int(base_damage)

        return final, crit

    @staticmethod
    def calculate_defense(player, weapon_name):
        luck = player.skills.get("Luck", 0)
        weapon = WEAPONS[weapon_name]

        defense = 1 + (0.2 * luck)
        if weapon_name == "Shield":
            defense += weapon.get("defense", 0)

        return int(defense)

    # ---------- New: geometry-based hit test ----------
    @staticmethod
    def can_hit_on_grid(attacker_pos, target_pos, weapon_name, grid):
        """Return True if weapon_name can reach target_pos from attacker_pos on grid."""
        # Sword: adjacent any direction
        if weapon_name == "Sword":
            return adjacent_any(attacker_pos, target_pos)

        # Shield: adjacent cardinal only
        if weapon_name == "Shield":
            return adjacent_cardinal(attacker_pos, target_pos)

        # Spear: exactly 2 cardinal spaces
        if weapon_name == "Spear":
            return straight_cardinal_exact(attacker_pos, target_pos, dist=2)

        # Bow: must be in straight or diagonal line AND have line of sight
        if weapon_name == "Bow":
            if not in_straight_or_diagonal(attacker_pos, target_pos):
                return False
            # Use grid.line_of_sight to check blocking; grid expects coords as (x,y)
            return grid.line_of_sight(attacker_pos, target_pos)
        # Magic Staff: range 4 in any direction with LoS
        if weapon_name == "Magic Staff":
            if manhattan(attacker_pos, target_pos) > 4:
                return False
            return grid.line_of_sight(attacker_pos, target_pos)

        return False

    @staticmethod
    def perform_attack(attacker, defender, attacker_weapon, defender_weapon, attacker_pos, defender_pos, grid):
        """
        Combines geometry + existing dodge/block/defense/damage logic.
        attacker, defender are PlayerBuild-like objects.
        attacker_pos and defender_pos are (x,y) tuples.
        grid is an instance of Grid (for LoS).
        """
        # 1) Check if weapon can reach the target position on the grid
        if not CombatSystem.can_hit_on_grid(attacker_pos, defender_pos, attacker_weapon, grid):
            return {"hit": False, "reason": "out_of_range_or_blocked"}

        # 2) Dodge check (defender may dodge based on their dex/luck and defender weapon)
        dodge_chance = CombatSystem.calculate_dodge_chance(defender, defender_weapon)
        if random.random() < dodge_chance:
            return {"hit": False, "dodge": True}

        # 3) Damage roll
        damage, crit = CombatSystem.calculate_damage(attacker, attacker_weapon)

        # 4) Block check (shield)
        block_chance = CombatSystem.calculate_block_chance(defender, defender_weapon)
        if random.random() < block_chance:
            # Blocking reduces damage by defender's defense (which includes shield)
            damage = max(0, damage - CombatSystem.calculate_defense(defender, defender_weapon))
            return {"hit": True, "dodge": False, "block": True, "crit": crit, "damage": damage}

        # 5) Apply normal defense
        defense = CombatSystem.calculate_defense(defender, defender_weapon)
        final_damage = max(0, damage - defense)

        return {"hit": True, "dodge": False, "block": False, "crit": crit, "damage": final_damage}
