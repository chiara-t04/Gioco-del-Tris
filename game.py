import random
from typing import Optional
from board import Board
from human_player import HumanPlayer
from bot_player import BotPlayer
from player import Player
from observer import Subject,Observer

class Game(Subject):
    def __init__(self, player1: HumanPlayer, player2: BotPlayer, board: Board) -> None:
        self.board: Board = board
        self.player1: HumanPlayer = player1
        self.player2: BotPlayer = player2
        self.current_player_obj: Optional[Player] = None
        self._observers = []

    def initialize_turn(self) -> None:
        if random.choice([True, False]):
            self.current_player_obj = self.player1
        else:
            self.current_player_obj = self.player2

    def switch_player(self) -> None:
        self.current_player_obj = self.player2 if self.current_player_obj == self.player1 else self.player1
        self.notify() #chiama il metodo update degli observer, quidni stampa non appena il gioco inizia 
        
    def check_game_over(self) -> Optional[str]:
        winner_symbol: Optional[str] = None
        if self.board.check_winner(self.player1.get_symbol()):
            winner_symbol = self.player1.get_symbol()
        elif self.board.check_winner(self.player2.get_symbol()):
            winner_symbol = self.player2.get_symbol()

        if winner_symbol:
            return winner_symbol
        elif self.board.is_full():
            return "draw"
        return None
    
    def attach(self, observer: 'Observer') -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: 'Observer') -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)

