# main.py
from Ch6_Player_Build import PlayerBuild
from Ch6_Weapons_System import choose_weapon, WEAPONS
from Ch6_Combat_System import CombatSystem
from Ch6_Grid import Grid
import random

def print_help():
    print("""
Commands:
  w/a/s/d  - move up/left/down/right
  q        - quit
  f        - attack (attempt to hit the enemy)
  stats    - print player and enemy stats
  help     - show this message
""")

def simple_enemy_ai_move(grid, enemy_name, player_pos):
    # Enemy moves one step toward player (manhattan greedy)
    ex, ey = grid.get_position(enemy_name)
    px, py = player_pos
    dx = 0
    dy = 0
    if ex < px:
        dx = 1
    elif ex > px:
        dx = -1
    elif ey < py:
        dy = 1
    elif ey > py:
        dy = -1
    # try move; grid.move will print if blocked
    grid.move(enemy_name, dx, dy)

def main():
    print("== Arena Builder (Grid Combat Demo) ==")

    # create player
    player = PlayerBuild(points=12, name="Player")
    player.distribute_points()

    # choose player's weapon
    player_weapon = choose_weapon()
    print(f"\nYou chose: {player_weapon}")

    # create enemy with a simple preset build
    enemy = PlayerBuild(points=0, name="Enemy")
    enemy.hp = 20
    enemy.skills = {"Strength": 3, "Dexterity": 2, "Intelligence": 0, "Charisma": 0, "Luck": 1}
    enemy_weapon = random.choice(list(WEAPONS.keys()))

    # set up grid and place players
    grid = Grid(width=8, height=6)
    # choose starting positions (ensure they are empty)
    grid.place(player.name, 1, grid.height // 2)
    grid.place(enemy.name, grid.width - 2, grid.height // 2)

    print("Enemy weapon:", enemy_weapon)
    grid.display()
    print_help()

    # main loop
    while True:
        cmd = input("cmd> ").strip().lower()
        if cmd == "q":
            print("Quitting.")
            break
        if cmd == "help":
            print_help()
            continue
        if cmd == "stats":
            print(f"\nPlayer HP: {player.hp}, Weapon: {player_weapon}, Skills: {player.skills}")
            print(f"Enemy HP: {enemy.hp}, Weapon: {enemy_weapon}, Skills: {enemy.skills}")
            continue

        if cmd in ("w","a","s","d"):
            move_map = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
            dx, dy = move_map[cmd]
            moved = grid.move(player.name, dx, dy)
            if moved:
                # enemy turn: simple move toward player
                simple_enemy_ai_move(grid, enemy.name, grid.get_position(player.name))
            grid.display()
            continue

        if cmd == "f":
            attacker_pos = grid.get_position(player.name)
            defender_pos = grid.get_position(enemy.name)

            result = CombatSystem.perform_attack(
                attacker=player,
                defender=enemy,
                attacker_weapon=player_weapon,
                defender_weapon=enemy_weapon,
                attacker_pos=attacker_pos,
                defender_pos=defender_pos,
                grid=grid
            )

            if not result.get("hit", False):
                if result.get("dodge"):
                    print("Enemy dodged your attack!")
                elif result.get("reason") == "out_of_range_or_blocked":
                    print("Attack failed: target out of range or line-of-sight blocked.")
                else:
                    print("Attack missed or failed.")
            else:
                dmg = result.get("damage", 0)
                enemy.hp -= dmg
                s = f"You hit the enemy for {dmg} HP"
                if result.get("crit"):
                    s += " (CRIT!)"
                if result.get("block"):
                    s += " (enemy partially blocked)"
                print(s)
                if enemy.hp <= 0:
                    print("Enemy defeated — you win!")
                    grid.display()
                    break

            # enemy retaliates if alive
            if enemy.hp > 0:
                e_att_pos = grid.get_position(enemy.name)
                p_pos = grid.get_position(player.name)
                e_result = CombatSystem.perform_attack(
                    attacker=enemy,
                    defender=player,
                    attacker_weapon=enemy_weapon,
                    defender_weapon=player_weapon,
                    attacker_pos=e_att_pos,
                    defender_pos=p_pos,
                    grid=grid
                )
                if not e_result.get("hit", False):
                    if e_result.get("reason") == "out_of_range_or_blocked":
                        # move toward player instead
                        simple_enemy_ai_move(grid, enemy.name, p_pos)
                        print("Enemy moves closer.")
                    elif e_result.get("dodge"):
                        print("You dodged the enemy's attack.")
                    else:
                        print("Enemy's attack missed.")
                else:
                    dmg = e_result.get("damage", 0)
                    player.hp -= dmg
                    s = f"Enemy hits you for {dmg} HP"
                    if e_result.get("crit"):
                        s += " (CRIT!)"
                    if e_result.get("block"):
                        s += " (you partially blocked)"
                    print(s)
                    if player.hp <= 0:
                        print("You have been defeated...")
                        grid.display()
                        break

            grid.display()
            continue

        print("Unknown command. Type 'help' for commands.")

if __name__ == "__main__":
    main()
