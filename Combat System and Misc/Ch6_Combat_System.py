# combat_system.py

import random
from Ch6_Weapons_System import WEAPONS
from Ch6_Player_Build import PlayerBuild   # Only needed if you use type checks (optional)

class CombatSystem:

    @staticmethod
    def calculate_dodge_chance(player, weapon_name):
        dex = player.skills["Dexterity"]
        luck = player.skills["Luck"]
        weapon = WEAPONS[weapon_name]

        base_dodge = 0.03 * dex
        weight = weapon.get("weight", 2)
        weapon_bonus = max(0.0, 0.08 - 0.02 * weight)
        luck_bonus = 0.015 * luck

        return min(base_dodge + weapon_bonus + luck_bonus, 0.70)

    @staticmethod
    def calculate_block_chance(player, weapon_name):
        if weapon_name != "Shield":
            return 0
        base_block = 0.30
        luck_bonus = 0.015 * player.skills["Luck"]
        return min(base_block + luck_bonus, 0.60)

    @staticmethod
    def calculate_damage(player, weapon_name):
        str_stat = player.skills["Strength"]
        dex = player.skills["Dexterity"]
        luck = player.skills["Luck"]
        weapon = WEAPONS[weapon_name]

        base_damage = 2 + (0.8 * str_stat) + (0.2 * dex)

        if weapon_name == "Sword":
            base_damage += 1
        elif weapon_name == "Spear":
            base_damage += 2
        elif weapon_name == "Bow":
            base_damage += 3
        elif weapon_name == "Shield":
            base_damage = 1
        elif weapon_name == "Magic Staff":
            base_damage += 4 + (0.5 * player.skills["Intelligence"])

        crit_chance = min(0.03 * luck, 1.0)
        if random.random() < crit_chance:
            return int(base_damage * 1.5), True

        return int(base_damage), False

    @staticmethod
    def calculate_defense(player, weapon_name):
        luck = player.skills["Luck"]
        weapon = WEAPONS[weapon_name]

        defense = 1 + (0.2 * luck)

        if weapon_name == "Shield":
            defense += weapon["defense"]

        return int(defense)

    @staticmethod
    def perform_attack(attacker, defender, attacker_weapon, defender_weapon):
        dodge_chance = CombatSystem.calculate_dodge_chance(defender, defender_weapon)

        if random.random() < dodge_chance:
            return {"hit": False, "dodge": True}

        damage, crit = CombatSystem.calculate_damage(attacker, attacker_weapon)

        block_chance = CombatSystem.calculate_block_chance(defender, defender_weapon)
        if random.random() < block_chance:
            damage = max(0, damage - CombatSystem.calculate_defense(defender, defender_weapon))
            return {
                "hit": True, "dodge": False, "block": True,
                "crit": crit, "damage": damage
            }

        defense = CombatSystem.calculate_defense(defender, defender_weapon)
        final_damage = max(0, damage - defense)

        return {
            "hit": True, "dodge": False, "block": False,
            "crit": crit, "damage": final_damage
        }
