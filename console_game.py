from board import Board
from human_player import HumanPlayer
from bot_player import BotPlayer
from game import Game
from typing import Optional
from observer import Observer

class ConsoleGame(Observer):
    def __init__(self):
        self.board = Board()
        self.human: Optional[HumanPlayer] = None
        self.bot: Optional[BotPlayer] = None
        self.game: Optional[Game] = None
    
    def update(self, subject) -> None:
        print(f"\n E' il turno di {subject.current_player_obj.get_name()} ({subject.current_player_obj.get_symbol()})")
        self.print_board()  #stampa turno corrente e tabellone aggiornato e viene chiamato ogni volta che Game chiama notify()

    def print_board(self):
        grid = self.board.get_grid()
        print("\n    1   2   3")
        print("  ┌───┬───┬───┐")
        for r in range(3):
            print(f"{r+1} │", end="")
            for c in range(3):
                cell = grid[r][c]
                symbol = cell if cell != " " else "-"
                print(f" {symbol} ", end="│")
            print()
            if r < 2:
                print("  ├───┼───┼───┤")
        print("  └───┴───┴───┘\n")

    def get_user_settings(self):
        print("\n Tris ")

        nickname = input("Enter your nickname: ").strip()
        while True:
            symbol = input("Choose your symbol (X or O): ").strip().upper() #caratteri di una stringa in maiuscolo
            if symbol in ("X", "O"):
                break
            print("Invalid symbol. Choose 'X' or 'O'.")

        while True:
            difficulty = input("Choose bot difficulty (facile, medio, difficile): ").strip().lower()
            if difficulty in ("facile", "medio", "difficile"):
                break
            print("Invalid difficulty. Choose from: facile, medio, difficile.")

        bot_symbol = "O" if symbol == "X" else "X"
        self.human = HumanPlayer(nickname, symbol)
        self.bot = BotPlayer("Computer", bot_symbol, difficulty=difficulty)
        self.game = Game(self.human, self.bot, self.board)
        self.game.initialize_turn()
        self.game.attach(self)  #registra l'observer nel game

    def play(self):
        self.get_user_settings()
        self.print_board()

        while True:
            current = self.game.current_player_obj
            print(f"Turn: {current.get_name()} ({current.get_symbol()})")

            move = current.make_move(self.board) #chiede al giocatore di fare la mossa
            if move and self.board.make_move(*move, current.get_symbol()):
                self.print_board()
                result = self.game.check_game_over()
                if result:
                    if result == "draw":
                        print("It's a draw!")
                    else:
                        winner = self.human.get_name() if result == self.human.get_symbol() else self.bot.get_name()
                        print(f"{winner} wins!")
                    break
                self.game.switch_player()
                
            else:
                print("Invalid move. Try again.")
        while True:
            again = input("Vuoi giocare un'altra partita? (s/n): ").strip().lower()
            if again == "s":
                self.board.reset()
                self.play()
                break
            elif again == "n":
                print(" Grazie per aver giocato!")
                break
            else:
                print(" Inserisci 's' per sì o 'n' per no.")

if __name__ == "__main__":
    game = ConsoleGame()
    game.play()
    

