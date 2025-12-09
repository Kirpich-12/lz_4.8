import random


def base_solved_grid() -> list[list[int]]:
    """сетка 9 * 9."""

    grid = []

    for r in range(9):
        row = []
        for c in range(9):
            value = (r * 3 + r // 3 + c) % 9 + 1
            row.append(value)
        grid.append(row)
    return grid

def shuffle_stacks_cols(g):
    # переставляем блоки столбцов
    cols = [0, 1, 2]
    random.shuffle(cols)
    mat = [[None] * 9 for _ in range(9)]
    for new_b, b in enumerate(cols):
        chosen = list(range(b * 3, b * 3 + 3))
        random.shuffle(chosen)
        for r in range(9):
            for i, c in enumerate(chosen):
                mat[r][new_b * 3 + i] = g[r][c]
    return mat

def shuffle_bands_rows(g):
    # переставляем блоки строк (0-2,3-5,6-8)
    bands = [0, 1, 2]
    random.shuffle(bands)
    new = []
    for b in bands:
        rows = list(range(b * 3, b * 3 + 3))
        random.shuffle(rows)
        for r in rows:
            new.append(g[r])
    return new


def shuffle_grid(grid:list[list[int]]) -> list[list[int]]:
    """Перемешиваем цифры"""
    g = [row[:] for row in grid]
    g = shuffle_bands_rows(g)
    g = shuffle_stacks_cols(g)

    #доп перемешивание
    perm = list(range(1, 10))
    random.shuffle(perm)
    mapping = {i + 1: perm[i] for i in range(9)}
    g = [[mapping[val] for val in row] for row in g]

    return g


def make_puzzle(remove_count:int) -> list[list[int]]:
    solved = shuffle_grid(base_solved_grid())
    # копируем
    puzzle = [row[:] for row in solved]
    coords = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(coords)
    removed = 0
    for (r, c) in coords:
        if removed >= remove_count:
            break
        # удаляем
        puzzle[r][c] = 0
        removed += 1
    return puzzle, solved


def is_conflict(grid:list[list[int]], row:int, col:int, val:int) -> bool:
    """Проверка"""
    # строка
    for c in range(9):
        if c != col and grid[row][c] == val:
            return True
    # столбец
    for r in range(9):
        if r != row and grid[r][col] == val:
            return True
    # блок
    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if (r != row or c != col) and grid[r][c] == val:
                return True
    return False

def is_win(grid:list[list[int]], solved:list[list[int]]) -> bool:
    return grid == solved