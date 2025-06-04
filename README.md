# Gioco del Tris ( con Streamlit & Console)

Un'applicazione Python del classico **Gioco del Tris (Tic-Tac-Toe)** con:
- Interfaccia **Streamlit** per il gioco da browser
- Modalità **console**
- Bot con **3 livelli di difficoltà**
- Integrazione con **Ollama** per strategie AI avanzate
- Design pattern **Observer** per aggiornamenti automatici del gioco

---

##  Caratteristiche Principali

- Gioca contro un **bot intelligente** con difficoltà: *facile*, *medio*, *difficile*
- In modalità *difficile*, il bot si appoggia all'intelligenza artificiale Ollama
- Interfaccia **web** realizzata con [Streamlit](https://streamlit.io/)
-  Modalità **testuale** eseguibile da terminale
- Sistema Observer/Subject per notificare lo stato del gioco
- Pulito, testabile e facilmente estendibile

---

##  Struttura del Progetto

```
.
├── main.py               # Interfaccia Streamlit
├── console_game.py       # Modalità da terminale
├── game.py               # Logica del gioco e turni
├── board.py              # Rappresentazione del tabellone
├── player.py             # Classe astratta Player
├── human_player.py       # Implementazione Player umano
├── bot_player.py         # Implementazione Bot con strategie
├── observer.py           # Pattern Observer (Subject & Observer)
├── constants.py          # Costanti simboliche del gioco
```

---

##  Requisiti

Installa le dipendenze:

```bash
pip install streamlit requests
```

---

##  Esecuzione

###  Interfaccia Web (Streamlit)

```bash
streamlit run main.py
```

###  Modalità Console

```bash
python console_game.py
```

---

##  Integrazione con Ollama (opzionale)

Per abilitare la difficoltà **"difficile"**, è necessario installare e avviare **Ollama**:

```bash
ollama run llama3
```

Non accessibile su `http://localhost:11434`.  
La modalità “difficile” non può funzionare perché Ollama non è accessibile da remoto (Streamlit Cloud)

---

##  Design Pattern Utilizzati

- **Strategy Pattern**: seleziona dinamicamente la strategia del bot (*Easy*, *Medium*, *Hard*)
- **Observer Pattern**: aggiorna dinamicamente l’interfaccia (*console* o *Streamlit*) quando il turno cambia
- **Facade**: `OllamaMoveFacade` incapsula la comunicazione con l’AI esterna

---



##  Autori

- Sviluppato come progetto educativo per mostrare l'uso di **Streamlit**, **design pattern** e **AI integration**.

---

## 📜 Licenza

Questo progetto è open-source e disponibile sotto licenza MIT.
