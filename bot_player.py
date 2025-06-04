from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from board import Board
from constants import EMPTY_CELL, HUMAN_SYMBOL, AI_SYMBOL
import random
import time
import streamlit as st
import requests
import logging
from player import Player
import re

#Classi per le difficoltà
class MoveStrategy(ABC):
    @abstractmethod
    def get_move(self, board: Board, bot: 'BotPlayer') -> Optional[Tuple[int, int]]:
        pass


class EasyMoveStrategy(MoveStrategy):
    def get_move(self, board: Board, bot: 'BotPlayer') -> Optional[Tuple[int, int]]:
        available_moves: List[Tuple[int, int]] = []
        grid = board.get_grid()
        for r in range(3):
            for c in range(3):
                if grid[r][c] == EMPTY_CELL:
                    available_moves.append((r, c))
        return random.choice(available_moves) if available_moves else None


class MediumMoveStrategy(MoveStrategy):
    def get_move(self, board: Board, bot: 'BotPlayer') -> Optional[Tuple[int, int]]:
        current_grid: List[List[str]] = [row[:] for row in board.get_grid()]

        for r in range(3):
            for c in range(3):
                if current_grid[r][c] == EMPTY_CELL:
                    current_grid[r][c] = bot.get_symbol()
                    temp_board = Board()
                    temp_board._grid = [row[:] for row in current_grid]
                    if temp_board.check_winner(bot.get_symbol()):
                        return (r, c)
                    current_grid[r][c] = EMPTY_CELL

        opponent_symbol: str = HUMAN_SYMBOL if bot.get_symbol() == AI_SYMBOL else AI_SYMBOL
        for r in range(3):
            for c in range(3):
                if current_grid[r][c] == EMPTY_CELL:
                    current_grid[r][c] = opponent_symbol
                    temp_board = Board()
                    temp_board._grid = [row[:] for row in current_grid]
                    if temp_board.check_winner(opponent_symbol):
                        return (r, c)
                    current_grid[r][c] = EMPTY_CELL

        return EasyMoveStrategy().get_move(board, bot)


class OllamaMoveFacade:
    def __init__(self, bot: 'BotPlayer') -> None:
        self.bot = bot

    def get_move(self, board: Board) -> Optional[Tuple[int, int]]:
        if not self.bot._check_ollama_available():
            st.warning("Ollama non disponibile. Uso strategia media.")
            return MediumMoveStrategy().get_move(board, self.bot)

        grid = board.get_grid()
        board_representation = self.bot._format_board_for_ai(grid)
        opponent_symbol = HUMAN_SYMBOL if self.bot.get_symbol() == AI_SYMBOL else AI_SYMBOL
        available_moves = [f"({r},{c})" for r in range(3) for c in range(3) if grid[r][c] == EMPTY_CELL]

        prompt = f"""Board state (your symbol: {self.bot.get_symbol()}):
{board_representation}

Available moves: {', '.join(available_moves)}

Return ONLY the coordinates as "(row,col)" (example: "(1,2)"). Only one tuple. No explanation."""

        try:
            with st.spinner("🦙 Llama sta pensando..."):
                payload = {                                     #modo in cui sto mandando il messaggio all'indirizzo (pecchetto da mandare)
                    "model": self.bot._model,
                    "prompt": prompt,
                    "stream": False,                            #legge tutto e poi ti risponde
                    "options": {"temperature": 0.1, "top_p": 0.9, "num_predict": 10}  #temperature: quanto cambia la risposta ogni volta che la generi (indice di creatività)
                }                                                                     #top_p: considero opzioni sensate, equilibrio tra qualità e controllo
                response = requests.post(self.bot._ollama_url, json=payload, timeout=30) #num_predict: lunghezza massima della risposta 

                if response.status_code == 200:
                    result = response.json()
                    move_str = result['response'].strip()
                    '''
                    st.write(f"🦙 Llama risponde: '{move_str}'")
                    with open('llama_responses.log', 'a', encoding='utf-8') as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Llama risposta: '{move_str}'\n")
                    '''

                    parsed_move = None

                    if move_str:
                        # Pulizia base
                        text = move_str.strip().replace(" ", "").lower()
                        
                        # Rimuovi parentesi se ci sono
                        text = text.replace("(", "").replace(")", "")
                        
                        # Cerca la virgola
                        if "," in text:
                            parts = text.split(",")
                            if len(parts) >= 2:
                                try:
                                    # Prendi solo i primi caratteri che sono numeri
                                    row_str = ""
                                    col_str = ""
                                    
                                    # Estrai il primo numero
                                    for char in parts[0]:
                                        if char.isdigit():
                                            row_str += char
                                            break
                                    
                                    # Estrai il secondo numero  
                                    for char in parts[1]:
                                        if char.isdigit():
                                            col_str += char
                                            break
                                    
                                    if row_str and col_str:
                                        row = int(row_str)
                                        col = int(col_str)
                                        
                                        # Controlla che siano nel range valido
                                        if 0 <= row <= 2 and 0 <= col <= 2:
                                            parsed_move = (row, col)
                                            
                                except ValueError:
                                    pass
                        
                        # Se non ha funzionato con la virgola, prova a cercare due numeri consecutivi
                        if not parsed_move:
                            numbers = []
                            for char in text:
                                if char.isdigit():
                                    num = int(char)
                                    if 0 <= num <= 2:
                                        numbers.append(num)
                                        if len(numbers) == 2:
                                            break
                            
                            if len(numbers) == 2:
                                parsed_move = (numbers[0], numbers[1])

                    if parsed_move and board.is_valid_move(parsed_move[0], parsed_move[1]):
                        st.success(f"🦙 Llama sceglie: {parsed_move}")
                        return parsed_move
                    else:
                        if parsed_move:
                            st.warning(f"Mossa non valida: {parsed_move}")
                        else:
                            st.warning(f"Formato non riconosciuto: '{move_str}'")
                        
                        # Fallback
                        st.info("🔄 Uso strategia media come fallback")
                        return self._get_medium_move(board)
                else:
                    st.error(f"Errore Ollama: {response.status_code}")
                    return self._get_medium_move(board)
        except Exception as e:
            st.error(f"Errore connessione Ollama: {e}")

        st.info("🔄 Uso strategia media come fallback")
        return MediumMoveStrategy().get_move(board, self.bot)


class HardMoveStrategy(MoveStrategy):
    def get_move(self, board: Board, bot: 'BotPlayer') -> Optional[Tuple[int, int]]:
        return OllamaMoveFacade(bot).get_move(board)


#Classe Bot
class BotPlayer(Player):
    def __init__(self, name: str, symbol: str, difficulty: str = "facile") -> None:
        super().__init__(name, symbol)
        self._difficulty = difficulty
        self._ollama_url = "http://localhost:11434/api/generate"
        self._model = "llama3.2:1b" 
        self._strategy = self._select_strategy(difficulty)

    def _select_strategy(self, difficulty: str) -> MoveStrategy:
        if difficulty == "facile":
            return EasyMoveStrategy()
        elif difficulty == "medio":
            return MediumMoveStrategy()
        elif difficulty == "difficile":
            return HardMoveStrategy()
        else:
            return EasyMoveStrategy()

    def make_move(self, board: Board) -> Optional[Tuple[int, int]]:
        time.sleep(0.5)
        return self._strategy.get_move(board, self)

    def _check_ollama_available(self) -> bool:
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5) #richiesta a questo indirizzo 
            return response.status_code == 200 
        except:
            return False

    def _format_board_for_ai(self, grid: List[List[str]]) -> str:
        representation = "   0   1   2\n"
        representation += " ┌───┬───┬───┐\n"
        for r in range(3):
            representation += f"{r}│"
            for c in range(3):
                cell = grid[r][c]
                representation += f" {cell if cell != EMPTY_CELL else '-'} "
                if c < 2:
                    representation += "│"
            representation += "│\n"
            if r < 2:
                representation += " ├───┼───┼───┤\n"
        representation += " └───┴───┴───┘\n"
        
        representation += f"\nYour symbol: {self.get_symbol()}\n"
        representation += "Coordinates: (row,col) where row=0-2 (top to bottom), col=0-2 (left to right)\n"
                    
        return representation