from typing import Optional, Tuple
from board import Board


class Player:
    def __init__(self, name: str, symbol: str) -> None:
        self._name: str = name
        self._symbol: str = symbol

    def get_name(self) -> str:
        return self._name

    def get_symbol(self) -> str:
        return self._symbol

    def make_move(self, board: Board) -> Optional[Tuple[int, int]]:
        raise NotImplementedError("Questo metodo deve essere implementato dalle sottoclassi.")
