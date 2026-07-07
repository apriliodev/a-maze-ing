import sys
import random
from parser import load_config
from a_maze_ing import Grid, create_maze

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)

    config = load_config(sys.argv[1])

    grid = Grid(config.width, config.height)
    rng = random.Random(config.seed)

    start_x, start_y = config.entry
    create_maze(grid, start_x, start_y, rng)
    for row in grid.cells:
        for cell in row:
            print(cell)

    print(f"Maze generated with seed={config.seed}")
if __name__ == "__main__":
    main()