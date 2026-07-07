from dataclasses import dataclass
import random
import sys
from parser import load_config

# create the maze with cell and backtrack recursive


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

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)

    config = load_config(sys.argv[1])

    grid = Grid(config.width, config.height)
    rng = random.Random(config.seed)

    start_x, start_y = config.entry
    create_maze(grid, start_x, start_y, rng)
    path = find_shortest_path(grid, config.entry, config.exit)
    write_output_file(grid, config.entry, config.exit, path, config.output_file)
    print(f"Maze generated with seed={config.seed}")

if __name__ == "__main__":
    main()