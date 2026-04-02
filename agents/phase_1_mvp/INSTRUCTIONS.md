# Fase 1 – MVP Core
**Agente assegnato:** BACKEND + DB + TELEGRAM + TEST
**Prerequisiti:** Fase 0 completata (STATUS = ✅ DONE)
**Sblocca:** Fase 2

---

## Obiettivo
Sistema funzionante end-to-end: dal raw evento Binance fino alla bozza Telegram con possibilità di approvare/modificare/eliminare.

---

## Task da eseguire in ordine

> Le task con la stessa indentazione possono essere eseguite in parallelo.

```
F1-01  DB Models                    ← inizia subito (dipende solo da F0)
F1-02  Event Models                 ← inizia subito
  F1-03  CCXT Client                ← dopo F1-02
  F1-04  Binance Listener           ← dopo F1-02
    F1-05  Event Normalizer         ← dopo F1-04
      F1-06  Trade Engine           ← dopo F1-05 + F1-01
        F1-07  Template Engine      ← dopo F1-06
          F1-08  Telegram Bot       ← dopo F1-07 + F1-01
            F1-09  Handlers         ← dopo F1-08
              F1-10  Dispatcher     ← dopo F1-09
                F1-11  main.py      ← dopo tutto
F1-12  Test unitari                 ← dopo F1-05, F1-06, F1-07
F1-13  Test integrazione            ← dopo F1-11 + F1-12
```

---

## Dettaglio task

### F1-01 – Modelli DB
**File:** `src/db/models.py`
**Agente:** DB
Verificare che esistano e siano corretti: `Trader`, `Trade`, `Position`, `TelegramDraft`, `TraderConfig`, `TraderTemplate`.
Eseguire migration:
```bash
PYTHONPATH=. python -c "
import asyncio
from src.db.session import init_db, create_tables
from src.config import Settings
init_db(Settings().database_url)
asyncio.run(create_tables())
print('Tabelle create OK')
"
```

---

### F1-02 – Modelli evento
**File:** `src/events/types.py`, `src/events/models.py`
**Agente:** BACKEND
Verificare che `EventType`, `Side`, `TradeEvent` siano importabili e istanziabili.
```bash
PYTHONPATH=. python -c "
from src.events.types import EventType, Side
from src.events.models import TradeEvent
from datetime import datetime, timezone
e = TradeEvent(EventType.OPEN, 'BTCUSDT', Side.LONG, 0.1, 40000, datetime.now(tz=timezone.utc), 'trader_1')
print('TradeEvent OK:', e)
"
```

---

### F1-03 – CCXT Client
**File:** `src/exchange/ccxt_client.py`
**Agente:** BACKEND
Verificare che la classe si istanzi senza errori (non richiede API reale):
```bash
PYTHONPATH=. python -c "
from src.exchange.ccxt_client import CCXTClient
c = CCXTClient('binance', 'fake_key', 'fake_secret', sandbox=True)
print('CCXTClient OK')
"
```

---

### F1-04 – Binance Listener
**File:** `src/exchange/binance_listener.py`
**Agente:** BACKEND
Verificare istanziazione (non avviare il WS reale):
```bash
PYTHONPATH=. python -c "
import asyncio
from src.exchange.binance_listener import BinanceListener
async def fake_cb(e): pass
l = BinanceListener('t1', 'k', 's', fake_cb)
print('BinanceListener OK')
"
```

---

### F1-05 – Event Normalizer
**File:** `src/events/normalizer.py`
**Agente:** BACKEND
```bash
PYTHONPATH=. pytest tests/unit/test_normalizer.py -v
```

---

### F1-06 – Trade Engine
**File:** `src/trade_engine/engine.py`, `src/trade_engine/position.py`
**Agente:** BACKEND
```bash
PYTHONPATH=. pytest tests/unit/test_trade_engine.py -v
```

---

### F1-07 – Template Engine
**File:** `src/templates/engine.py`, `src/templates/renderer.py`, `src/templates/default/*.j2`
**Agente:** BACKEND
```bash
PYTHONPATH=. pytest tests/unit/test_templates.py -v
```

---

### F1-08 – Telegram Bot setup
**File:** `src/telegram/bot.py`, `src/telegram/keyboards.py`
**Agente:** TELEGRAM
```bash
PYTHONPATH=. python -c "
from src.telegram.keyboards import draft_keyboard
kb = draft_keyboard(1)
print('Keyboard OK:', kb)
"
```

---

### F1-09 – Handlers Telegram
**File:** `src/telegram/handlers.py`
**Agente:** TELEGRAM
Verificare importazione senza errori:
```bash
PYTHONPATH=. python -c "from src.telegram.handlers import router; print('Router OK')"
```

---

### F1-10 – Dispatcher
**File:** `src/dispatcher/dispatcher.py`
**Agente:** TELEGRAM
```bash
PYTHONPATH=. python -c "from src.dispatcher.dispatcher import MessageDispatcher; print('Dispatcher OK')"
```

---

### F1-11 – Entry point main.py
**File:** `src/main.py`
**Agente:** BACKEND
Verificare che il modulo sia importabile (non avviare il server):
```bash
PYTHONPATH=. python -c "import src.main; print('main.py OK')"
```

---

### F1-12 – Test unitari
**File:** `tests/unit/`
**Agente:** TEST
```bash
PYTHONPATH=. pytest tests/unit/ -v --tb=short
```
**Soglia:** 100% pass richiesto.

---

### F1-13 – Test integrazione
**File:** `tests/integration/`
**Agente:** TEST
```bash
PYTHONPATH=. pytest tests/integration/ -v --tb=short
```

---

## Test di chiusura fase

```bash
# Suite completa unitari + integrazione
PYTHONPATH=. pytest tests/unit/ tests/integration/ -v --tb=short

# E2E pipeline (smoke test)
PYTHONPATH=. pytest tests/e2e/test_full_pipeline.py -v

# Linter
PYTHONPATH=. ruff check src/ tests/
```

**Risultato atteso:** tutti i test devono passare prima di chiudere la fase.

---

## Dipendenze bloccanti per Fase 2
- F2-01 richiede: F1-01 (DB models), F0-02 (config)
- F2-02 richiede: F1-06 (Trade Engine, Position)
