# Ch6_Weapons_System.py

WEAPONS = {
    "Sword":  {"range": 1, "str_req": 2, "dex_req": 2, "weight": 1, "base_damage_mod": 1},
    "Spear":  {"range": 2, "str_req": 3, "dex_req": 1, "weight": 2, "base_damage_mod": 2},
    "Bow":    {"range": None, "dex_req": 4, "str_req": 1, "weight": 1, "base_damage_mod": 3},
    "Shield": {"range": 1, "str_req": 1, "defense": 2, "weight": 3, "base_damage_mod": 0},

}

def choose_weapon():
    print("\nChoose a weapon:")
    for i, w in enumerate(WEAPONS):
        print(f"{i+1}. {w}")

    while True:
        try:
            choice = int(input("Weapon number: ")) - 1
            if 0 <= choice < len(WEAPONS):
                return list(WEAPONS.keys())[choice]
            print("Invalid choice.")
        except ValueError:
            print("Enter a valid number.")
