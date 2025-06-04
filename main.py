import streamlit as st
from typing import List, Tuple, Optional
from constants import HUMAN_SYMBOL, AI_SYMBOL, EMPTY_CELL
from board import Board
from human_player import HumanPlayer
from bot_player import BotPlayer
from game import Game

def initialize_session_state() -> None:
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
    if st.session_state.game_started:
        st.session_state.board_obj.reset()
        st.session_state.winner = None
        st.session_state.draw = False
        st.session_state.message = ""

        st.session_state.player1_obj = HumanPlayer(st.session_state.player_name, st.session_state.player_symbol)
        ai_symbol: str = AI_SYMBOL if st.session_state.player_symbol == HUMAN_SYMBOL else HUMAN_SYMBOL
        st.session_state.player2_obj = BotPlayer("Bot", ai_symbol, st.session_state.bot_difficulty)

        st.session_state.game_obj = Game(st.session_state.player1_obj, st.session_state.player2_obj, st.session_state.board_obj)
        st.session_state.game_obj.initialize_turn()
    else:
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        initialize_session_state()

    st.rerun()

def handle_player_move(row: int, col: int) -> None:
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
            st.session_state.message = "🚫 Mossa non valida!"
    else:
        st.session_state.message = "⏳ Attendi il turno del bot."

def handle_bot_move() -> None:
    game: Game = st.session_state.game_obj

    if game.check_game_over():
        return

    if game.current_player_obj == game.player2:
        with st.spinner("🤖 Il Bot sta pensando..."):
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
            st.session_state.message = "⚠️ Il bot non ha trovato una mossa valida."
            game.switch_player()

def announce_result(result: str) -> None:
    if result == "draw":
        st.session_state.draw = True
        st.session_state.message = "🤝 Pareggio! Nessun vincitore."
        st.balloons()
    else:
        winner_name: str = st.session_state.player1_obj.get_name() if result == st.session_state.player1_obj.get_symbol() else st.session_state.player2_obj.get_name()
        st.session_state.winner = winner_name
        if result == st.session_state.player1_obj.get_symbol():
            st.session_state.message = f"🎉 {winner_name} ha vinto! 🎉"
            st.balloons()
        else:
            st.session_state.message = f"🤖 {winner_name} ha vinto!"
            st.snow()

#Interfaccia Streamlit 
st.set_page_config(layout="centered", page_title="🎲 Gioco del Tris")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>✨ Gioco del Tris ✨</h1>", unsafe_allow_html=True)

initialize_session_state()

if not st.session_state.game_started:
    st.header("⚙️ Configura la partita")

    player_name_input: str = st.text_input("🎮 Nickname:", st.session_state.player_name or "Giocatore")
    player_symbol_radio: str = st.radio("🧩 Simbolo:", ("X", "O"), index=0 if st.session_state.player_symbol == "X" else 1)

    bot_difficulty_select: str = st.selectbox(
        "🧠 Difficoltà del Bot:", 
        ["facile", "medio", "difficile"], 
        index=["facile", "medio", "difficile"].index(st.session_state.bot_difficulty)
    )

    if st.button("🚀 Inizia la partita", type="primary"):
        st.session_state.player_name = player_name_input
        st.session_state.player_symbol = player_symbol_radio
        st.session_state.bot_difficulty = bot_difficulty_select
        st.session_state.game_started = True
        start_new_game()
else:
    game: Game = st.session_state.game_obj

    st.subheader(f"🆚 {game.player1.get_name()} ({game.player1.get_symbol()}) vs {game.player2.get_name()} ({game.player2.get_symbol()})")
    st.markdown(f"<h4 style='color:#4B9CD3;'>🎯 Turno: {game.current_player_obj.get_name()} ({game.current_player_obj.get_symbol()})</h4>", unsafe_allow_html=True)

    grid_cells: List[List[str]] = game.board.get_grid()
    for r in range(3):
        row_cols = st.columns(3)
        for c in range(3):
            cell_value: str = grid_cells[r][c]
            button_label: str = " " if cell_value == EMPTY_CELL else f"**{cell_value}**"
            style = "color: green;" if cell_value == "X" else "color: red;"
            disabled = (
                cell_value != EMPTY_CELL or
                game.check_game_over() is not None or
                game.current_player_obj != game.player1 #disabilita i bottoni se la cella è occupata o se non è il tuo turno
            )
            with row_cols[c]:
                if st.button(button_label, key=f"cell_{r}_{c}", disabled=disabled):
                    handle_player_move(r, c)

    st.markdown("---")
    if st.session_state.message:
        st.success(st.session_state.message)

    col1_buttons, col2_buttons = st.columns(2)
    with col1_buttons:
        if st.button("🔙 Torna al menù", type="primary"):
            st.session_state.game_started = False
            start_new_game()
    with col2_buttons:
        if st.button("🔄 Nuova Partita", type="secondary"):
            start_new_game()

    if game.current_player_obj == game.player2 and not game.check_game_over():
        handle_bot_move()
