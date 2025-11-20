# main.py

from Ch6_Player_Build import PlayerBuild
from Ch6_Weapons_System import choose_weapon
from Ch6_Combat_System import CombatSystem

def main():
    print("== Arena Builder ==")

    player = PlayerBuild(points=12)
    player.distribute_points()

    print(f"\nTotal number of possible skill distributions: {player.stars_and_bars_count()}")

    weapon = choose_weapon()
    print(f"\nYou chose: {weapon}")

if __name__ == "__main__":
    main()
