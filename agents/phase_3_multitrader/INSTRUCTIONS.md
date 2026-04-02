# Fase 3 – Multi-Trader
**Agente assegnato:** BACKEND + DB + TELEGRAM + TEST
**Prerequisiti:** Fase 2 completata (STATUS = ✅ DONE)
**Sblocca:** Fase 4

---

## Obiettivo
Supporto a più trader con isolamento completo: listener separati, template personalizzati per trader, canali Telegram distinti.

---

## Task da eseguire

### F3-01 – Modello Trader e FK su tabelle esistenti
**File:** `src/db/models.py`
**Agente:** DB

Verificare che esista `Trader` con tutti i campi e che `Trade`, `Position`, `TelegramDraft`, `TraderConfig` abbiano `trader_id` come FK.
Creare migration Alembic per le modifiche (se schema cambiato).

```bash
PYTHONPATH=. python -c "
from src.db.models import Trader, Trade, Position, TelegramDraft, TraderConfig, TraderTemplate
print('Tutti i modelli con trader_id OK')
"
```

**Attenzione:** se il DB SQLite esiste già con lo schema precedente, va ricreato:
```bash
rm -f telegram_signals.db
PYTHONPATH=. python -c "
import asyncio
from src.db.session import init_db, create_tables
from src.config import Settings
init_db(Settings().database_url)
asyncio.run(create_tables())
print('Schema multi-trader OK')
"
```

---

### F3-02 – ListenerManager: un listener per trader
**File:** `src/exchange/listener_manager.py`
**Agente:** BACKEND

Verificare importazione e logica di caricamento:
```bash
PYTHONPATH=. python -c "
import asyncio
from src.exchange.listener_manager import ListenerManager
async def fake_cb(e): pass
lm = ListenerManager(on_event=fake_cb)
print('ListenerManager OK')
"
```

**Nota:** il test completo richiede traders nel DB. Usare fixture nel test di integrazione.

---

### F3-03 – Template personalizzati per trader
**File:** `src/templates/template_store.py`
**Agente:** BACKEND

Creare `TemplateStore` con metodi:
- `get_template(trader_id, event_type) -> str | None`
- `set_template(trader_id, event_type, template_str)`
- `delete_template(trader_id, event_type)`

Aggiornare `TemplateRenderer` per cercare template custom prima del default.

```bash
PYTHONPATH=. python -c "
from src.templates.template_store import TemplateStore
print('TemplateStore OK')
"
```

---

### F3-04 – Canali Telegram separati per trader
**File:** `src/telegram/draft_manager.py`, `src/dispatcher/dispatcher.py`
**Agente:** TELEGRAM

Aggiornare `DraftManager.send_draft()` e `MessageDispatcher.dispatch()` per usare i canali del trader specifico (da DB) invece dei valori globali di config.

Verifica:
```bash
PYTHONPATH=. python -c "
from src.telegram.draft_manager import DraftManager
from src.dispatcher.dispatcher import MessageDispatcher
print('Moduli multi-canale OK')
"
```

---

### F3-05 – Comandi admin Telegram
**File:** `src/telegram/handlers.py`
**Agente:** TELEGRAM

Implementare:
- `/add_trader` → FSM wizard: chiede nome, api_key, api_secret, review_chat_id, channel_id → salva `Trader` su DB
- `/list_traders` → elenco traders con stato attivo/inattivo
- `/toggle_trader <id>` → abilita/disabilita

```bash
PYTHONPATH=. python -c "
from src.telegram.handlers import router
print('Handlers admin OK')
"
```

---

### F3-06 – Test multi-trader
**File:** `tests/integration/test_multi_trader.py`
**Agente:** TEST

Creare il file (non esiste ancora). Test da implementare:
1. Crea 2 trader nel DB
2. Simula eventi paralleli per entrambi
3. Verifica che le posizioni siano isolate
4. Verifica che i draft vadano ai canali corretti

```bash
PYTHONPATH=. pytest tests/integration/test_multi_trader.py -v
```

---

## Test di chiusura fase

```bash
# Suite completa
PYTHONPATH=. pytest tests/unit/ tests/integration/ -v

# E2E
PYTHONPATH=. pytest tests/e2e/ -v

# Linter
PYTHONPATH=. ruff check src/exchange/ src/telegram/ src/templates/
```

---

## Dipendenze bloccanti per Fase 4
- F4-01 richiede: F3-01 (Trader nel DB)
- F4-03 richiede: F3-03 (TemplateStore)
