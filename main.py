import streamlit as st
import openai
from typing import List, Tuple, Optional
from constants import HUMAN_SYMBOL, AI_SYMBOL, EMPTY_CELL
from board import Board
from human_player import HumanPlayer
from bot_player import BotPlayer
from game import Game

openai.api_key='sk-proj-oM72ZMoNV9NfbfhEfDkuP4Z02jyo3bE2qVWnpCodjbOhWHVq6DK39tdrz-4j5E9GFN1X5h9KET3BlbkFJzan2YwCE7tNxRKkjf2tjxP_jz7pbq6wfKEKyHBPxAuP3nJ02e5yRgBT3ElaeNvaolBL7L8l-UA'


def initialize_session_state() -> None:
    """Inizializza lo stato del gioco in st.session_state."""
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
        st.session_state.player_name = ""
        st.session_state.player_symbol = HUMAN_SYMBOL
        st.session_state.bot_difficulty = "facile" 
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
import streamlit

st.set_page_config(layout="centered", page_title="Tris con Streamlit")

st.title("🎲 Gioco del Tris 🎲")

initialize_session_state()

# Schermata di configurazione iniziale 
if not st.session_state.game_started:
    st.header("Configura la tua partita")

    player_name_input: str = st.text_input("Scegli il tuo Nickname:", st.session_state.player_name if st.session_state.player_name else "Giocatore")
    player_symbol_radio: str = st.radio("Scegli il tuo Simbolo:", ("X", "O"), index=0 if st.session_state.player_symbol == "X" else 1)
    
    bot_difficulty_options = {"facile": "facile", "medio": "medio", "difficile": "difficile"}
    bot_difficulty_select: str = st.selectbox(
        "Difficoltà della Partita:", 
        list(bot_difficulty_options.keys()), 
        index=list(bot_difficulty_options.keys()).index(st.session_state.bot_difficulty)
    )

    if st.button("Inizia Partita", type="primary"):
        st.session_state.player_name = player_name_input
        st.session_state.player_symbol = player_symbol_radio
        st.session_state.bot_difficulty = bot_difficulty_select 
        st.session_state.game_started = True
        start_new_game()
else:
    # Schermata di gioco 
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
