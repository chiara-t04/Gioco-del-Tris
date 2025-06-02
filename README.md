# 🎲 Gioco del Tris (Tic-Tac-Toe) con AI

Un'implementazione moderna del classico gioco del Tris costruita con **Streamlit** e **Python**, che include un'intelligenza artificiale con tre livelli di difficoltà, inclusa l'integrazione con **OpenAI GPT**.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)


## 📋 Indice

- [Caratteristiche](#-caratteristiche)
- [Architettura](#-architettura)
- [Struttura del Progetto](#-struttura-del-progetto)
- [Installazione](#-installazione)
- [Configurazione](#-configurazione)
- [Utilizzo](#-utilizzo)
- [Documentazione Tecnica](#-documentazione-tecnica)

## ✨ Caratteristiche

- **🎮 Interfaccia web interattiva** con Streamlit
- **🤖 AI con 3 livelli di difficoltà:**
  - **Facile**: Mosse casuali
  - **Medio**: Strategia di vittoria e blocco
  - **Difficile**: Integrazione con OpenAI GPT-4
- **👤 Personalizzazione giocatore**: Nome e simbolo (X/O) personalizzabili
- **🎯 Sistema di validazione**: Controlli automatici delle mosse
- **🏆 Rilevamento automatico**: Vittoria, pareggio, e fine partita
- **🔄 Gestione turni**: Alternanza automatica tra giocatori
- **📱 Design responsive**: Funziona su desktop e mobile

## 🏗️ Architettura

Il progetto segue i principi di **programmazione orientata agli oggetti** e **separazione delle responsabilità**:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Game      │ ◄──┤   Players    │ ►  │   Board     │
│ (Controller)│    │  (Logic)     │    │  (Model)    │
└─────────────┘    └──────────────┘    └─────────────┘
       ▲                   ▲                   ▲
       │                   │                   │
┌─────────────────────────────────────────────────────┐
│              Streamlit UI (View)                    │
└─────────────────────────────────────────────────────┘
```

### Classi Principali

- **`Board`**: Gestisce la griglia di gioco, validazione mosse, controllo vittorie
- **`Player`** (astratta): Classe base per tutti i giocatori
- **`HumanPlayer`**: Implementazione per giocatore umano
- **`BotPlayer`**: Implementazione AI con algoritmi di difficoltà variabile
- **`Game`**: Controller principale che coordina il flusso di gioco

## 📁 Struttura del Progetto

```
tris_game/
├── 📄 main.py              # Applicazione Streamlit principale
├── 📄 constants.py         # Costanti del gioco
├── 📄 board.py            # Classe Board (modello della griglia)
├── 📄 player.py           # Classe base Player
├── 📄 human_player.py     # Implementazione giocatore umano
├── 📄 bot_player.py       # Implementazione AI bot
├── 📄 game.py             # Controller principale del gioco
├── 📁 tests/              # Suite di test
│   ├── 📄 test_board.py   # Test per la classe Board
│   ├── 📄 test_players.py # Test per le classi Player
│   └── 📄 test_game.py    # Test per la classe Game
├── 📄 requirements.txt    # Dipendenze di produzione
├── 📄 requirements-test.txt # Dipendenze per testing
├── 📄 mypy.ini           # Configurazione type checking
├── 📄 Makefile           # Automazione comandi
└── 📄 README.md          # Questa documentazione
```

## 🚀 Installazione

### Prerequisiti

- Python 3.8 o superiore
- pip (package manager Python)

### Installazione Rapida

```bash
# 1. Clona il repository
git clone <repository-url>
cd tris_game

# 2. Installa le dipendenze
pip install -r requirements.txt

# 3. Avvia l'applicazione
streamlit run main.py
```

## ⚙️ Configurazione

### Configurazione OpenAI (per difficoltà "Difficile")

1. **Ottieni una API Key** da [OpenAI](https://platform.openai.com/api-keys)

2. **Configura la chiave** (⚠️ **IMPORTANTE per la sicurezza**):

   **Metodo Sicuro (Raccomandato):**
   ```bash
   # Crea file .env
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```
   
   Poi modifica `main.py`:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   openai.api_key = os.getenv('OPENAI_API_KEY')
   ```

3. **Installa python-dotenv** (se usi il metodo sicuro):
   ```bash
   pip install python-dotenv
   ```

## 🎮 Utilizzo

### Avvio dell'Applicazione

```bash
streamlit run main.py
```

L'applicazione si aprirà automaticamente nel browser all'indirizzo `http://localhost:8501`

### Come Giocare

1. **📝 Configurazione Iniziale:**
   - Inserisci il tuo nickname
   - Scegli il tuo simbolo (X o O)
   - Seleziona la difficoltà del bot:
     - **Facile**: Il bot fa mosse casuali
     - **Medio**: Il bot cerca di vincere o bloccare
     - **Difficile**: Il bot usa OpenAI per mosse ottimali

2. **🎯 Gameplay:**
   - Clicca su una cella vuota per fare la tua mossa
   - Il bot farà automaticamente la sua mossa
   - Il primo a fare tris (3 simboli in fila) vince!

3. **🔄 Nuova Partita:**
   - **"Nuova Partita"**: Cambia configurazione
   - **"Ricomincia Stessa Partita"**: Mantieni le impostazioni

### Comandi da Terminale

```bash
# Avvia l'app
streamlit run main.py

# Forza ricaricamento
# Premi 'R' nel terminale mentre l'app è in esecuzione

# Ferma l'app
# Premi Ctrl+C nel terminale
```

## 📚 Documentazione Tecnica

### Algoritmi del Bot

#### 🟢 Facile (`_get_easy_move`)
```python
# Trova tutte le celle vuote e sceglie casualmente
available_moves = [(r,c) for r,c in empty_cells]
return random.choice(available_moves)
```

#### 🟡 Medio (`_get_medium_move`)
```python
# 1. Controlla se può vincere
for each empty_cell:
    if simulate_move(bot_symbol) results in win:
        return winning_move

# 2. Controlla se deve bloccare l'avversario
for each empty_cell:
    if simulate_move(opponent_symbol) results in win:
        return blocking_move

# 3. Fallback a mossa casuale
return easy_move()
```

#### 🔴 Difficile (`_get_hard_move`)
```python
# 1. Formatta board per AI
board_string = format_board_for_ai(grid)

# 2. Invia prompt a OpenAI
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

# 3. Valida risposta
if is_valid_move(ai_move):
    return ai_move
else:
    return medium_move()  # Fallback
```

### Architettura delle Classi

```python
# Gerarchia di ereditarietà
Player (ABC)
├── HumanPlayer
└── BotPlayer

# Composizione
Game
├── player1: HumanPlayer
├── player2: BotPlayer
└── board: Board
```

### Gestione dello Stato in Streamlit

```python
# Session state management
st.session_state = {
    'game_started': bool,
    'player_name': str,
    'player_symbol': str,
    'bot_difficulty': str,
    'board_obj': Board,
    'game_obj': Game,
    'current_player_obj': Player,
    # ... altri stati
}
```

### Controllo Vittorie

Il controllo delle vittorie verifica:
- **Righe**: 3 simboli uguali in orizzontale
- **Colonne**: 3 simboli uguali in verticale  
- **Diagonali**: 3 simboli uguali in diagonale (principale e secondaria)

```python
def check_winner(symbol):
    return (_check_rows(symbol) or 
            _check_columns(symbol) or 
            _check_diagonals(symbol))
```
