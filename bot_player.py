import requests
import json
import time
import streamlit as st
from typing import List, Tuple, Optional, Dict, Any
from player import Player
from board import Board
from constants import EMPTY_CELL, HUMAN_SYMBOL, AI_SYMBOL
import random
import logging


class BotPlayer(Player):
    def __init__(self, name: str, symbol: str, difficulty: str = "facile") -> None:
        super().__init__(name, symbol)
        self._difficulty = difficulty
        self._ollama_url = "http://localhost:11434/api/generate"
        self._model = "llama3.2:1b"  # Modello leggero e veloce

    def _check_ollama_available(self) -> bool:
        """Verifica se Ollama è disponibile."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _get_hard_move_ollama(self, board: Board) -> Optional[Tuple[int, int]]:
        """Usa Ollama/Llama per ottenere la mossa migliore."""
        
        if not self._check_ollama_available():
            st.warning("⚠️ Ollama non disponibile. Uso strategia media.")
            return self._get_medium_move(board)
        
        grid: List[List[str]] = board.get_grid()
        board_str: str = self._format_board_for_ai(grid)

        opponent_symbol = HUMAN_SYMBOL if self.get_symbol() == AI_SYMBOL else AI_SYMBOL
        board_representation = self._create_detailed_board_representation(grid)
        available_moves = []
        for r in range(3):
            for c in range(3):
                if grid[r][c] == EMPTY_CELL:
                    available_moves.append(f"({r},{c})")
        
        prompt = f"""You are playing Tic-Tac-Toe. You are '{self.get_symbol()}' and your opponent is '{opponent_symbol}'.

CURRENT BOARD STATE:
{board_representation}

AVAILABLE MOVES: {', '.join(available_moves)}

CRITICAL: Your response must be EXACTLY in format "row,col" where row and col are numbers 0, 1, or 2.
Examples: "0,1" or "2,0" or "1,1". 

Choose your best move:"""

        try:
            with st.spinner("🦙 Llama sta pensando..."):
                payload = {
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 10
                    }
                }
                
                response = requests.post(
                    self._ollama_url,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    move_str = result['response'].strip()
                    
                    st.write(f"🦙 Llama risponde: '{move_str}'")
                    with open('llama_responses.log', 'a', encoding='utf-8') as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Llama risposta: '{result}'\n")
                    
                    # Parse della risposta
                    if ',' in move_str:
                        try:
                            # Estrai solo i numeri
                            parts = move_str.split(',')
                            row = int(parts[0].strip())
                            col = int(parts[1].strip())
                            
                            if board.is_valid_move(row, col):
                                st.success(f"🦙 Llama sceglie: ({row}, {col})")
                                return (row, col)
                            else:
                                st.warning(f"Llama ha suggerito mossa non valida: ({row},{col})")
                        except:
                            st.warning(f"Formato risposta Llama non riconosciuto: '{move_str}'")
                    
                    # Fallback
                    st.info("🔄 Uso strategia media come fallback")
                    return self._get_medium_move(board)
                else:
                    st.error(f"Errore Ollama: {response.status_code}")
                    return self._get_medium_move(board)
                    
        except Exception as e:
            st.error(f"Errore connessione Ollama: {e}")
            return self._get_medium_move(board)

    def make_move(self, board: Board) -> Optional[Tuple[int, int]]:
        time.sleep(0.5)
        
        if self._difficulty == "facile":
            return self._get_easy_move(board)
        elif self._difficulty == "medio":
            return self._get_medium_move(board)
        elif self._difficulty == "difficile":
            return self._get_hard_move_ollama(board)
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


    def _format_board_for_ai(self, grid: List[List[str]]) -> str:
        """Formatta la board in una stringa leggibile dall'AI."""
        formatted_board: str = ""
        for r_idx, row_cells in enumerate(grid): # Rinominato per chiarezza
            formatted_board += " ".join([cell if cell != EMPTY_CELL else "-" for cell in row_cells])
            if r_idx < 2:
                formatted_board += "\n"
        return formatted_board

    def _create_detailed_board_representation(self, grid: List[List[str]]) -> str:
        """Crea una rappresentazione dettagliata del board con coordinate."""
        representation = "   0   1   2\n"
        representation += " ┌───┬───┬───┐\n"
        
        for r in range(3):
            representation += f"{r}│"
            for c in range(3):
                cell = grid[r][c]
                if cell == EMPTY_CELL:
                    representation += f" - "
                else:
                    representation += f" {cell} "
                if c < 2:
                    representation += "│"
            representation += "│\n"
            if r < 2:
                representation += " ├───┼───┼───┤\n"
        
        representation += " └───┴───┴───┘\n"
        
        representation += f"\nYour symbol: {self.get_symbol()}\n"
        representation += "Coordinates: (row,col) where row=0-2 (top to bottom), col=0-2 (left to right)\n"
        
        return representation
