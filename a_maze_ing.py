from dataclasses import dataclass
import random
import sys
from parser import load_config, MazeConfig

# create the maze with cell and backtrack recursive
import os

if sys.platform in ('linux', 'darwin'):
    CLEAR = 'clear'
elif sys.platform == 'win32':
    CLEAR = 'cls'
else:
    print('Plateforme non supportée', file=sys.stderr)
    exit(1)


def clear_term() -> None:
    os.system(CLEAR)


class Color:
    def __init__(self) -> None:
        self.index = 0
        self.color = [15, 226, 46, 21, 208]

    def current(self) -> int:
        return self.color[self.index]

    def next_color(self) -> None:
        self.index = (self.index + 1) % len(self.color)


@dataclass
class Cell:
    north: bool = True
    east: bool = True
    south: bool = True
    west: bool = True
    visited: bool = False


class Grid:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.cells: list[list[Cell]] = []

        for y in range(height):
            row: list[Cell] = []
            for x in range(width):
                row.append(Cell())
            self.cells.append(row)

    def get_cell(self, x: int, y: int):
        return self.cells[y][x]


PATTERN_42 = [
    "#...###",
    "#.....#",
    "###.###",
    "..#.#..",
    "..#.###"
]


def stamp_42_pattern(
        grid: Grid, entry: tuple[int, int], exit_pos: tuple[int, int],
        show_pattern: bool = False) -> list[tuple[int, int]]:
    if show_pattern:
        if grid.width < 7 or grid.height < 5:
            print("Maze too small to display the '42' pattern.")
            return []
        offset_x = (grid.width - 7) // 2
        offset_y = (grid.height - 5) // 2
        pattern_cells: list[tuple[int, int]] = []
        for row, line in enumerate(PATTERN_42):
            for col, char in enumerate(line):
                if char == "#":
                    pattern_cells.append((offset_x + col, offset_y + row))
        if entry in pattern_cells or exit_pos in pattern_cells:
            print("Entry or exit overlaps the '42' pattern, skipping it.")
            return []
        for x, y in pattern_cells:
            cell = grid.get_cell(x, y)
            cell.visited = True
        return pattern_cells
    pattern_cells = []
    return pattern_cells


def remove_wall(grid: Grid, x1: int, y1: int, x2: int, y2: int) -> None:
    cell1 = grid.get_cell(x1, y1)
    cell2 = grid.get_cell(x2, y2)

    dx = x2 - x1
    dy = y2 - y1

    if dx == 1 and dy == 0:
        cell1.east = False
        cell2.west = False
    elif dx == -1 and dy == 0:
        cell1.west = False
        cell2.east = False
    elif dx == 0 and dy == 1:
        cell1.south = False
        cell2.north = False
    elif dx == 0 and dy == -1:
        cell1.north = False
        cell2.south = False


def get_neighbors(grid: Grid, x: int, y: int) -> list[tuple[int, int]]:
    neighbors: list[tuple[int, int]] = []

    candidates = [
        (x + 1, y),
        (x - 1, y),
        (x, y - 1),
        (x, y + 1),
    ]

    for nx, ny in candidates:
        if 0 <= nx < grid.width and 0 <= ny < grid.height:
            neighbors.append((nx, ny))

    return neighbors


def random_remove(grid: Grid, rng: random.Random, percent: float, pattern_cells: list[tuple[int, int]]) -> None:
    attempts: int = int(percent * (grid.width * grid.height))
    for i in range(attempts):
        x = rng.randint(0, grid.width - 1)
        y = rng.randint(0, grid.height - 1)
        valid_cells = get_neighbors(grid, x, y)
        nx, ny = rng.choice(valid_cells)
        if (x, y) in pattern_cells or (nx, ny) in pattern_cells:
            continue
        remove_wall(grid, x, y, nx, ny)


def create_maze(grid: Grid, start_x: int, start_y: int, rng: random.Random) -> None:
    start_cell = grid.get_cell(start_x, start_y)
    start_cell.visited = True

    stack: list[tuple[int, int]] = [(start_x, start_y)]
    while stack:
        current_x, current_y = stack[-1]
        neighbors = get_neighbors(grid, current_x, current_y)
        unvisited = []
        for nx, ny in neighbors:
            neighbor_cell = grid.get_cell(nx, ny)
            if not neighbor_cell.visited:
                unvisited.append((nx, ny))
        if unvisited:
            next_x, next_y = rng.choice(unvisited)
            remove_wall(grid, current_x, current_y, next_x, next_y)
            next_cell = grid.get_cell(next_x, next_y)
            next_cell.visited = True
            stack.append((next_x, next_y))
        else:
            stack.pop()


def find_shortest_path(grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
    queue = [start]
    visited = {start}
    came_from = {}
    while queue:
        current = queue.pop(0)

        if current == goal:
            break
        current_x, current_y = current
        cell = grid.get_cell(current_x, current_y)
        reachable = []
        if not cell.north:
            reachable.append((current_x, current_y - 1))
        if not cell.south:
            reachable.append((current_x, current_y + 1))
        if not cell.east:
            reachable.append((current_x + 1, current_y))
        if not cell.west:
            reachable.append((current_x - 1, current_y))

        for neighbor in reachable:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)

    path = [goal]
    while path[-1] != start:
        path.append(came_from[path[-1]])

    path.reverse()
    return path


def path_to_directions(path: list[tuple[int, int]]) -> str:
    directions = ""
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i+1]
        dx = x2 - x1
        dy = y2 - y1

        if dx == 1 and dy == 0:
            directions += "E"
        elif dx == -1 and dy == 0:
            directions += "W"
        elif dx == 0 and dy == 1:
            directions += "S"
        elif dx == 0 and dy == -1:
            directions += "N"

    return directions


def cell_to_hex(cell: Cell) -> str:
    value = 0
    value += int(cell.north) * 1
    value += int(cell.east) * 2
    value += int(cell.south) * 4
    value += int(cell.west) * 8

    return format(value, "X")


def maze_to_hex(grid: Grid) -> str:
    output = ""
    for row in grid.cells:
        line = ""
        for cell in row:
            line += cell_to_hex(cell)
        output += line + "\n"
    return output


def write_output_file(
    grid: Grid,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
    path: list[tuple[int, int]],
    output_path: str,
) -> None:
    maze_str = maze_to_hex(grid)
    directions = path_to_directions(path)

    entry_x, entry_y = entry
    exit_x, exit_y = exit_pos

    with open(output_path, "w") as f:
        f.write(maze_str)
        f.write("\n")
        f.write(f"{entry_x},{entry_y}\n")
        f.write(f"{exit_x},{exit_y}\n")
        f.write(f"{directions}\n")


def build_char_grid(grid: Grid) -> list[list[bool]]:
    h = 2 * grid.height + 1
    w = 2 * grid.width + 1
    chars: list[list[bool]] = []
    for y in range(h):
        row: list[bool] = []
        for x in range(w):
            row.append(False)
        chars.append(row)
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            chars[y][x] = True
    return chars


def pixel_to_cell(row: int, col) -> tuple[int, int]:
    y = (row - 1) // 2
    x = (col - 1) // 2
    return x, y


def fill_wall(grid: Grid, chars: list[list[bool]]):
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.get_cell(x, y)
            if cell.north:
                chars[2 * y][2 * x + 1] = True
            if cell.west:
                chars[2 * y + 1][2 * x] = True
            if y == grid.height - 1 and cell.south:
                chars[2 * y + 2][2 * x + 1] = True
            if x == grid.width - 1 and cell.east:
                chars[2 * y + 1][2 * x + 2] = True


def path_pixels(path: list[tuple[int, int]]) -> set[tuple[int, int]]:
    pixels: set[tuple[int, int]] = set()
    for x, y in path:
        pixels.add((2 * y + 1, 2 * x + 1))  # center of the cell
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        row = y1 + y2 + 1
        col = x1 + x2 + 1
        pixels.add((row, col))  # the passage between the two cells
    return pixels


def render(
    grid: Grid,
    chars,
    entry,
    exit_pos,
    wall_color: Color,
    pattern_cells: list[tuple[int, int]],
    show_pattern: bool = False,
    show_path: bool = False,
):
    shortest_path = find_shortest_path(grid, entry, exit_pos)
    highlighted = path_pixels(shortest_path) if show_path else set()
    color = wall_color.current()

    for row in range(len(chars)):
        row_pixels = []
        for col in range(len(chars[0])):
            if chars[row][col]:
                pixel_text = f"\033[48;5;{color}m  \033[0m"
            else:
                cell = pixel_to_cell(row, col)
                if cell == entry:
                    code: int | None = 201
                elif cell == exit_pos:
                    code = 196
                elif show_pattern and cell in pattern_cells:
                    code = 252
                elif show_path and (row, col) in highlighted:
                    code = 51
                else:
                    code = None
                if code is None:
                    pixel_text = "  "
                else:
                    pixel_text = f"\033[48;5;{code}m  \033[0m"
            row_pixels.append(pixel_text)
        line = "".join(row_pixels)
        print(line)


def generate_maze(config: MazeConfig, show_pattern: bool):

    grid = Grid(config.width, config.height)
    rng = random.Random(config.seed)
    pattern_cells = stamp_42_pattern(
        grid, config.entry, config.exit, show_pattern)
    create_maze(grid, config.entry[0], config.entry[1], rng)
    if config.perfect == False:
        random_remove(grid, rng, 0.4, pattern_cells)
    path = find_shortest_path(grid, config.entry, config.exit)
    chars = build_char_grid(grid)
    fill_wall(grid, chars)

    return grid, chars, path, pattern_cells


def print_config(config: MazeConfig) -> None:
    print("=== User Config ===\n")
    print(f"Width : {config.width}")
    print(f"Height: {config.height}")
    print(f"Entry: {config.entry}")
    print(f"Exit: {config.exit}")
    print(f"Output File: {config.output_file}")
    print(f"Perfect ?: {config.perfect}")
    print(f"Seed: {config.seed}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)

    show_pattern = False
    show_path = False
    show_config = False

    config = load_config(sys.argv[1])
    grid, chars, path, pattern_cells = generate_maze(config, show_pattern)
    write_output_file(grid, config.entry, config.exit,
                      path, config.output_file)
    color = Color()
    while True:
        clear_term()
        render(grid, chars, config.entry, config.exit,
               color, pattern_cells, show_pattern, show_path)
        if show_config:
            print()
            print_config(config)

        print("\n=== A-Maze-ing ==="
              "\n1. Re-generate a new maze"
              "\n2. Show/Hide path from entry to exit"
              "\n3. Rotate maze colors"
              "\n4. Show 42 pattern"
              "\n5. ON/OFF Perfect maze"
              "\n6. Show config"
              "\n7. Quit"
              )
        choice = input("Choice? (1-7): ")
        if choice == "1":
            config.seed = random.randint(0, 2**32 - 1)
            grid, chars, path, pattern_cells = generate_maze(
                config, show_pattern)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color.next_color()
        elif choice == "4":
            show_pattern = not show_pattern
            # config.seed = random.randint(0, 2**32 - 1)
            grid, chars, path, pattern_cells = generate_maze(
                config, show_pattern)
        elif choice == "5":
            config.perfect = not config.perfect
            grid, chars, path, pattern_cells = generate_maze(
                config, show_pattern)
        elif choice == "6":
            show_config = not show_config
        elif choice == "7":
            break
        else:
            print("Choice not in list.")
