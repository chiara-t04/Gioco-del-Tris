import streamlit as st
import random
import time
import sys
import os
from openai import OpenAI
from typing import List, Tuple, Optional # Importa i tipi necessari

# Costanti del Gioco
HUMAN_SYMBOL: str = "X"
AI_SYMBOL: str = "O"
EMPTY_CELL: str = ""

# ATTENZIONE: NON lasciare la tua API key direttamente nel codice per la produzione.
# Utilizza st.secrets o variabili d'ambiente.
client = OpenAI()

# Classi del Gioco

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
        for row_cells in self._grid: # Rinominato per chiarezza, 'row' era ambiguo
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

class HumanPlayer(Player):
    def __init__(self, name: str, symbol: str) -> None:
        super().__init__(name, symbol)

    def make_move(self, board: Board) -> Optional[Tuple[int, int]]:
        # Come discusso, la logica della mossa umana è gestita dall'UI di Streamlit
        # e non direttamente da questo metodo.
        pass

class BotPlayer(Player):
    def __init__(self, name: str, symbol: str, difficulty: str = "easy") -> None:
        super().__init__(name, symbol)
        self._difficulty: str = difficulty

    def make_move(self, board: Board) -> Optional[Tuple[int, int]]:
        time.sleep(0.5) # Simula il "pensiero" del bot
        if self._difficulty == "easy":
            return self._get_easy_move(board)
        elif self._difficulty == "medium":
            return self._get_medium_move(board)
        elif self._difficulty == "hard":
            return self._get_hard_move(board)
        else:
            return self._get_easy_move(board)

    def _get_easy_move(self, board: Board) -> Optional[Tuple[int, int]]:
        available_moves: List[Tuple[int, int]] = []
        grid = board.get_grid()
        for r in range(3):
            for c in range(3):
                if grid[r][c] == EMPTY_CELL:
                    available_moves.append((r, c))
        return random.choice(available_moves) if available_moves else None

    def _get_medium_move(self, board: Board) -> Optional[Tuple[int, int]]:
        current_grid: List[List[str]] = [row[:] for row in board.get_grid()]

        # Controlla se il bot può vincere in questa mossa
        for r in range(3):
            for c in range(3):
                if current_grid[r][c] == EMPTY_CELL:
                    current_grid[r][c] = self.get_symbol()
                    # Creiamo una board temporanea per la simulazione
                    temp_board = Board()
                    temp_board._grid = [row[:] for row in current_grid] # Copia lo stato
                    if temp_board.check_winner(self.get_symbol()):
                        return (r, c)
                    current_grid[r][c] = EMPTY_CELL # Reset per la prossima iterazione

        # Controlla se l'avversario può vincere e bloccalo
        opponent_symbol: str = HUMAN_SYMBOL if self.get_symbol() == AI_SYMBOL else AI_SYMBOL
        for r in range(3):
            for c in range(3):
                if current_grid[r][c] == EMPTY_CELL:
                    current_grid[r][c] = opponent_symbol
                    temp_board = Board()
                    temp_board._grid = [row[:] for row in current_grid] # Copia lo stato
                    if temp_board.check_winner(opponent_symbol):
                        return (r, c)
                    current_grid[r][c] = EMPTY_CELL # Reset per la prossima iterazione

        return self._get_easy_move(board) # Se non ci sono mosse di vittoria o blocco, fa una mossa facile

    def _get_hard_move(self, board: Board) -> Optional[Tuple[int, int]]:
        """
        Ottiene la mossa tramite l'API di OpenAI.
        Invia lo stato della board e chiede a GPT di suggerire la mossa migliore.
        """
        grid: List[List[str]] = board.get_grid()
        board_str: str = self._format_board_for_ai(grid)
        current_player_symbol: str = self.get_symbol()

        prompt: str = f"""Sei un giocatore di Tic-Tac-Toe (Tris) e il tuo simbolo è '{current_player_symbol}'.
La board attuale è:
{board_str}

Le celle sono numerate da 0 a 2 per riga e colonna (es. (0,0) è in alto a sinistra, (2,2) è in basso a destra).
Indica la tua prossima mossa migliore come "riga,colonna" (es. "0,1" per la cella in alto centrale).
Assicurati che la mossa sia valida (la cella deve essere vuota).

Rispondi solo con la riga e la colonna separate da una virgola, senza testo aggiuntivo.
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Sei un esperto giocatore di Tic-Tac-Toe."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=5,
                temperature=0
            )

            move_str: str = response.choices[0].message.content.strip()
            row, col = map(int, move_str.split(','))

            if board.is_valid_move(row, col):
                return (row, col)
            else:
                st.warning(f"L'AI ha suggerito una mossa non valida ({row},{col}). Torno alla mossa 'medium'.")
                return self._get_medium_move(board)

        except Exception as e:
            st.error(f"Errore durante la comunicazione con OpenAI: {e}. Il bot userà la difficoltà 'medium'.")
            return self._get_medium_move(board)

    def _format_board_for_ai(self, grid: List[List[str]]) -> str:
        """Formatta la board in una stringa leggibile dall'AI."""
        formatted_board: str = ""
        for r_idx, row_cells in enumerate(grid): # Rinominato per chiarezza
            formatted_board += " ".join([cell if cell != EMPTY_CELL else "_" for cell in row_cells])
            if r_idx < 2:
                formatted_board += "\n"
        return formatted_board


# Classe Game
class Game:
    def __init__(self, player1: HumanPlayer, player2: BotPlayer, board: Board) -> None:
        self.board: Board = board
        self.player1: HumanPlayer = player1
        self.player2: BotPlayer = player2
        self.current_player_obj: Optional[Player] = None

    def initialize_turn(self) -> None:
        if random.choice([True, False]):
            self.current_player_obj = self.player1
        else:
            self.current_player_obj = self.player2

    def switch_player(self) -> None:
        self.current_player_obj = self.player2 if self.current_player_obj == self.player1 else self.player1

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

# Streamlit

def initialize_session_state() -> None:
    """Inizializza lo stato del gioco in st.session_state."""
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
        st.session_state.player_name = ""
        st.session_state.player_symbol = HUMAN_SYMBOL
        st.session_state.bot_difficulty = "easy"
        st.session_state.board_obj = Board()
        st.session_state.player1_obj = None
        st.session_state.player2_obj = None
        st.session_state.game_obj = None
        st.session_state.winner = None
        st.session_state.draw = False
        st.session_state.message = ""

def start_new_game() -> None:
    """Resetta il gioco e lo prepara per una nuova partita."""
    if st.session_state.game_started:
        st.session_state.board_obj.reset()
        st.session_state.winner = None
        st.session_state.draw = False
        st.session_state.message = ""

        if st.session_state.player1_obj is None or \
           st.session_state.player1_obj.get_name() != st.session_state.player_name or \
           st.session_state.player1_obj.get_symbol() != st.session_state.player_symbol:
            st.session_state.player1_obj = HumanPlayer(st.session_state.player_name, st.session_state.player_symbol)

        ai_symbol: str = AI_SYMBOL if st.session_state.player_symbol == HUMAN_SYMBOL else HUMAN_SYMBOL
        # Ricrea il BotPlayer per aggiornare la difficoltà se cambiata
        if st.session_state.player2_obj is None or \
           st.session_state.player2_obj._difficulty != st.session_state.bot_difficulty or \
           st.session_state.player2_obj.get_symbol() != ai_symbol:
            st.session_state.player2_obj = BotPlayer("Bot", ai_symbol, st.session_state.bot_difficulty)


        st.session_state.game_obj = Game(st.session_state.player1_obj, st.session_state.player2_obj, st.session_state.board_obj)
        st.session_state.game_obj.initialize_turn()
    else:
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        initialize_session_state()

    st.rerun()

def handle_player_move(row: int, col: int) -> None:
    """Gestisce la mossa del giocatore umano attraverso l'oggetto Game."""
    game: Game = st.session_state.game_obj

    if game.check_game_over():
        st.session_state.message = "La partita è terminata. Clicca 'Nuova Partita' per giocare ancora."
        return

    if game.current_player_obj == game.player1:
        if game.board.make_move(row, col, game.player1.get_symbol()):
            game_result: Optional[str] = game.check_game_over()
            if game_result:
                announce_result(game_result)
            else:
                game.switch_player()
                st.rerun()
        else:
            st.session_state.message = "Mossa non valida. La cella è già occupata o fuori limite."
    else:
        st.session_state.message = "Non è il tuo turno!"

def handle_bot_move() -> None:
    """Gestisce la mossa del bot attraverso l'oggetto Game."""
    game: Game = st.session_state.game_obj

    if game.check_game_over():
        return

    if game.current_player_obj == game.player2:
        with st.spinner("Il Bot sta pensando alla sua mossa..."):
            bot_move: Optional[Tuple[int, int]] = game.player2.make_move(game.board)
        if bot_move:
            row, col = bot_move
            game.board.make_move(row, col, game.player2.get_symbol())
            game_result: Optional[str] = game.check_game_over()
            if game_result:
                announce_result(game_result)
            else:
                game.switch_player()
            st.rerun()
        else:
            st.session_state.message = "Il bot non ha trovato una mossa valida (dovrebbe essere impossibile)."
            game.switch_player()

def announce_result(result: str) -> None:
    """Annuncia il risultato del gioco."""
    if result == "draw":
        st.session_state.draw = True
        st.session_state.message = "Pareggio! Nessun vincitore."
    else:
        winner_name: str = st.session_state.player1_obj.get_name() if result == st.session_state.player1_obj.get_symbol() else st.session_state.player2_obj.get_name()
        st.session_state.winner = winner_name
        if result == st.session_state.player1_obj.get_symbol():
            st.session_state.message = f"🎉 {winner_name} ha vinto! 🎉"
        else:
            st.session_state.message = f"🤖 {winner_name} ha vinto! 🤖"

# --- Interfaccia Streamlit ---

st.set_page_config(layout="centered", page_title="Tris con Streamlit")

st.title("🎲 Tris (Tic-Tac-Toe) 🎲")

initialize_session_state()

# --- Schermata di configurazione iniziale ---
if not st.session_state.game_started:
    st.header("Configura la tua partita")

    player_name_input: str = st.text_input("Scegli il tuo Nickname:", st.session_state.player_name if st.session_state.player_name else "Giocatore")
    player_symbol_radio: str = st.radio("Scegli il tuo Simbolo:", ("X", "O"), index=0 if st.session_state.player_symbol == "X" else 1)
    bot_difficulty_select: str = st.selectbox("Difficoltà del Bot:", ("easy", "medium", "hard"), index=["easy", "medium", "hard"].index(st.session_state.bot_difficulty))

    if st.button("Inizia Partita", type="primary"):
        st.session_state.player_name = player_name_input
        st.session_state.player_symbol = player_symbol_radio
        st.session_state.bot_difficulty = bot_difficulty_select
        st.session_state.game_started = True
        start_new_game()
else:
    # --- Schermata di gioco ---
    game: Game = st.session_state.game_obj

    st.header(f"Partita in corso: {game.player1.get_name()} ({game.player1.get_symbol()}) vs {game.player2.get_name()} ({game.player2.get_symbol()})")

    st.write(f"Turno di: **{game.current_player_obj.get_name()}** ({game.current_player_obj.get_symbol()})")

    grid_cells: List[List[str]] = game.board.get_grid()
    cols_layout = st.columns(3) # Variabile per il layout delle colonne

    for r in range(3):
        with st.container():
            row_cols = st.columns(3)
            for c in range(3):
                with row_cols[c]:
                    cell_value: str = grid_cells[r][c]
                    button_label: str = cell_value if cell_value != EMPTY_CELL else " "
                    button_disabled: bool = (cell_value != EMPTY_CELL or
                                             game.check_game_over() is not None or
                                             game.current_player_obj != game.player1)

                    if st.button(button_label, key=f"cell_{r}_{c}", use_container_width=True, disabled=button_disabled):
                        handle_player_move(r, c)

    st.markdown("---")

    if st.session_state.message:
        st.subheader(st.session_state.message)

    col1_buttons, col2_buttons = st.columns(2)
    with col1_buttons:
        if st.button("Nuova Partita", type="primary"):
            st.session_state.game_started = False
            start_new_game()

    with col2_buttons:
        if st.button("Ricomincia Stessa Partita", type="secondary"):
            start_new_game()

    if (game.current_player_obj == game.player2 and game.check_game_over() is None):
        handle_bot_move()