from typing import Optional, Tuple
from player import Player
from board import Board


class HumanPlayer(Player):
    def __init__(self, name: str, symbol: str) -> None:
        super().__init__(name, symbol)

    def make_move(self, board: Board) -> Optional[Tuple[int, int]]:
        # la logica della mossa umana è gestita dall'UI di Streamlit
        # e non direttamente da questo metodo.
        pass
