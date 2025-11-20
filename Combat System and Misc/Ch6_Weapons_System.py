# weapons.py

WEAPONS = {
    "Sword":       {"range": 1, "str_req": 2, "dex_req": 2, "weight": 1},
    "Spear":       {"range": 2, "str_req": 3, "dex_req": 1, "weight": 2},
    "Bow":         {"range": 5, "str_req": 1, "dex_req": 4, "weight": 1},
    "Shield":      {"range": 1, "str_req": 1, "defense": 2, "weight": 3},
    "Magic Staff": {"range": 4, "int_req": 5, "weight": 2},
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
