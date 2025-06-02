import random
import time
import streamlit as st
import openai
from typing import List, Tuple, Optional
from player import Player
from board import Board
from constants import EMPTY_CELL, HUMAN_SYMBOL, AI_SYMBOL


class BotPlayer(Player):
    def __init__(self, name: str, symbol: str, difficulty: str = "facile") -> None:
        super().__init__(name, symbol)
        self._difficulty = difficulty

    def make_move(self, board: Board) -> Optional[Tuple[int, int]]:
        time.sleep(0.5) # Simula il "pensiero" del bot
        if self._difficulty == "facile":
            return self._get_easy_move(board)
        elif self._difficulty == "medio":
            return self._get_medium_move(board)
        elif self._difficulty == "difficile":
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
        return random.choice(available_moves) if available_moves else None #trova tutte le celle vuote e ne sceglie una a caso

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
            response = openai.chat.completions.create(
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
                st.warning(f"L'AI ha suggerito una mossa non valida ({row},{col}). Torno alla mossa 'medio'.")
                return self._get_medium_move(board)

        except Exception as e:
            st.error(f"Errore durante la comunicazione con OpenAI: {e}. Il bot userà la difficoltà 'medio'.")
            return self._get_medium_move(board)

    def _format_board_for_ai(self, grid: List[List[str]]) -> str:
        """Formatta la board in una stringa leggibile dall'AI."""
        formatted_board: str = ""
        for r_idx, row_cells in enumerate(grid): # Rinominato per chiarezza
            formatted_board += " ".join([cell if cell != EMPTY_CELL else "_" for cell in row_cells])
            if r_idx < 2:
                formatted_board += "\n"
        return formatted_board
