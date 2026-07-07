from dataclasses import dataclass
import random

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


