# Fase 0 – Setup & Fondamenta
**Agente assegnato:** SETUP
**Prerequisiti:** nessuno
**Sblocca:** Fase 1

---

## Obiettivo
Preparare l'ambiente di sviluppo, le dipendenze e la connessione al database in modo che tutti gli altri agenti possano iniziare a lavorare.

---

## Task da eseguire

### F0-01 – Struttura directory progetto
**File da creare/verificare:**
- `pyproject.toml` con tutte le dipendenze (già presente — verificare)
- `.env.example` (già presente — verificare)
- `.gitignore` (già presente — verificare)
- Tutte le directory `src/`, `tests/`, `config/`, `scripts/` (già presenti)

**Azione:** verificare che la struttura corrisponda esattamente a `REPO_STRUCTURE.md`. Segnare in `GAPS_RISKS.md` qualsiasi discrepanza.

**Test di verifica:**
```bash
python -c "import src"
python -c "from pyproject_hooks import quiet_subprocess_runner"
```

---

### F0-02 – File di configurazione e Settings
**File target:** `src/config.py`

**Azione:**
1. Verificare che `src/config.py` legga correttamente da `.env`
2. Creare `.env` da `.env.example` se non esiste
3. Verificare che tutti i campi abbiano default sicuri per dev

**Test di verifica:**
```bash
python -c "
from src.config import Settings
s = Settings()
print('Config OK:', s.database_url)
"
```

**Errore atteso se manca `.env`:** pydantic-settings deve comunque caricare i default senza crashare.

---

### F0-03 – Database e sessione async
**File target:** `src/db/session.py`, `src/db/models.py`

**Azione:**
1. Verificare che `init_db()` e `create_tables()` funzionino con SQLite
2. Eseguire `create_tables()` e verificare che le tabelle vengano create
3. Verificare che `get_session()` restituisca una sessione async valida

**Test di verifica:**
```bash
python -c "
import asyncio
from src.db.session import init_db, create_tables
from src.config import Settings
s = Settings()
init_db(s.database_url)
asyncio.run(create_tables())
print('DB OK')
"
```

---

## Test di chiusura fase

Eseguire **tutti** prima di segnare la fase come DONE:

```bash
# 1. Import tutti i moduli senza errori
PYTHONPATH=. python -c "
import src.config
import src.db.models
import src.db.session
import src.events.types
import src.events.models
print('Tutti i moduli importano correttamente')
"

# 2. DB setup completo
PYTHONPATH=. python -c "
import asyncio
from src.db.session import init_db, create_tables
from src.config import Settings
init_db(Settings().database_url)
asyncio.run(create_tables())
print('DB setup OK')
"

# 3. Linter
PYTHONPATH=. ruff check src/config.py src/db/
```

---

## Dipendenze bloccanti per Fase 1
I seguenti task di Fase 1 **non possono iniziare** finché questa fase non è DONE:
- F1-01 (richiede DB funzionante)
- F1-06 (richiede Settings)
- F1-08 (richiede Settings per bot token)
