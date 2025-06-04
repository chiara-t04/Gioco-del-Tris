from typing import List
from constants import EMPTY_CELL


class Board:
    def __init__(self) -> None:
        self._grid: List[List[str]] = [[EMPTY_CELL for _ in range(3)] for _ in range(3)]

    def make_move(self, row: int, col: int, symbol: str) -> bool:
        if self.is_valid_move(row, col):
            self._grid[row][col] = symbol
            return True
        return False

    def is_valid_move(self, row: int, col: int) -> bool:
        return 0 <= row < 3 and 0 <= col < 3 and self._grid[row][col] == EMPTY_CELL

    def is_full(self) -> bool:
        for row in self._grid:
            if EMPTY_CELL in row:
                return False
        return True

    def check_winner(self, symbol: str) -> bool:
        return (self._check_rows(symbol) or
                self._check_columns(symbol) or
                self._check_diagonals(symbol))

    def _check_rows(self, symbol: str) -> bool:
        for row_cells in self._grid: 
            if all(cell == symbol for cell in row_cells):
                return True
        return False

    def _check_columns(self, symbol: str) -> bool:
        for col in range(3):
            if all(self._grid[row][col] == symbol for row in range(3)):
                return True
        return False

    def _check_diagonals(self, symbol: str) -> bool:
        if (self._grid[0][0] == symbol and
            self._grid[1][1] == symbol and
            self._grid[2][2] == symbol):
            return True
        if (self._grid[0][2] == symbol and
            self._grid[1][1] == symbol and
            self._grid[2][0] == symbol):
            return True
        return False

    def get_grid(self) -> List[List[str]]:
        return self._grid

    def reset(self) -> None:
        self._grid = [[EMPTY_CELL for _ in range(3)] for _ in range(3)]
