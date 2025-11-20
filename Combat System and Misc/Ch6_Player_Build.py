# player_build.py

import math

SKILLS = ["Strength", "Dexterity", "Intelligence", "Charisma", "Luck"]

class PlayerBuild:
    def __init__(self, points=12):
        self.total_points = points
        self.skills = {skill: 0 for skill in SKILLS}

    def distribute_points(self):
        print(f"\nYou have {self.total_points} skill points to distribute.")
        remaining = self.total_points

        for skill in SKILLS:
            while True:
                try:
                    value = int(input(f"Assign points to {skill} (remaining {remaining}): "))
                    if 0 <= value <= remaining:
                        self.skills[skill] = value
                        remaining -= value
                        break
                    else:
                        print("Invalid amount. Try again.")
                except ValueError:
                    print("Please enter a number.")

        print("\nFinal skill distribution:")
        for skill, val in self.skills.items():
            print(f"  {skill}: {val}")

    def stars_and_bars_count(self):
        k = len(self.skills)
        n = self.total_points
        return math.comb(n + k - 1, k - 1)
