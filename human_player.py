from typing import Optional, Tuple
from player import Player
from board import Board


class HumanPlayer(Player):
    def __init__(self, name: str, symbol: str) -> None:
        super().__init__(name, symbol)

    def make_move(self, board: Board) -> Optional[Tuple[int, int]]:
         while True:
            try:
                move_str = input("Enter your move (row,col) [1-3]: ").strip() #chiede all'utente una mossa in formato '2,3'
                row, col = map(int, move_str.split(",")) #converte la stringa in due numeri interi
                row -= 1  # da 1-based a 0-based
                col -= 1
                if board.is_valid_move(row, col):
                    return (row, col)
                else:
                    print("Invalid move: cell already occupied or out of range.")
            except:
                print("Invalid input format. Please enter as: 2,3")

#per streamlit questa funzione va sovrascitta, perchè l'input avviene via interfaccia (non da terminale)