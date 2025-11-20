# Ch6_Grid.py

class Grid:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height

        # Initialize grid with dots for empty spaces
        self.grid = [["." for _ in range(width)] for _ in range(height)]

        # Dictionary: {"PlayerName": (x, y)}
        self.positions = {}

    # --------------------------------------------------
    # PLACEMENT
    # --------------------------------------------------
    def place(self, name, x, y):
        """Place a player on the grid (no overlap allowed)."""
        if (x, y) in self.positions.values():
            raise ValueError("Space already occupied.")

        self.positions[name] = (x, y)
        self.grid[y][x] = name[0].upper()

    # --------------------------------------------------
    # MOVEMENT
    # --------------------------------------------------
    def move(self, name, dx, dy):
        """Move a player by (dx, dy)."""
        if name not in self.positions:
            raise ValueError(f"{name} not found on grid.")

        x, y = self.positions[name]
        nx, ny = x + dx, y + dy

        # Check bounds
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            print("Movement blocked: outside grid.")
            return False

        # Check collision
        if (nx, ny) in self.positions.values():
            print("Movement blocked: space occupied.")
            return False

        # Apply movement
        self.grid[y][x] = "."
        self.grid[ny][nx] = name[0].upper()
        self.positions[name] = (nx, ny)
        return True

    # --------------------------------------------------
    # GET POSITION
    # --------------------------------------------------
    def get_position(self, name):
        return self.positions.get(name, None)

    # --------------------------------------------------
    # GRID VISUAL
    # --------------------------------------------------
    def display(self):
        print("\n=== GRID ===")
        for row in self.grid:
            print(" ".join(row))
        print()

    # --------------------------------------------------
    # LINE OF SIGHT (for bow)
    # --------------------------------------------------
    def line_of_sight(self, start, end):
        """Check if there are obstacles between two grid points."""
        (x1, y1) = start
        (x2, y2) = end

        dx = x2 - x1
        dy = y2 - y1

        # normalize steps: step_x, step_y each in {-1, 0, 1}
        step_x = 0 if dx == 0 else dx // abs(dx)
        step_y = 0 if dy == 0 else dy // abs(dy)

        # If not straight/diagonal line, no LoS considered (caller should check)
        if not (step_x == 0 or step_y == 0 or abs(step_x) == abs(step_y)):
            return False

        x, y = x1 + step_x, y1 + step_y

        while (x, y) != (x2, y2):
            # If any non-dot cell (occupied), block line of sight.
            if self.grid[y][x] != ".":
                return False
            x += step_x
            y += step_y

        return True
