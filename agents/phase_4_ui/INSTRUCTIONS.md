# Fase 4 – Web UI
**Agente assegnato:** BACKEND + TEST
**Prerequisiti:** Fase 3 completata (STATUS = ✅ DONE)
**Sblocca:** —

---

## Obiettivo
Aggiungere un layer HTTP (FastAPI) con endpoint REST per gestione traders, storico trade e template. Dashboard web minimale.

---

## Task da eseguire

### F4-01 – Setup FastAPI
**File:** `src/api/__init__.py`, `src/api/main.py`
**Agente:** BACKEND

Aggiungere FastAPI e Uvicorn a `pyproject.toml`:
```toml
"fastapi>=0.110",
"uvicorn[standard]>=0.27",
```

Creare `src/api/main.py` con:
- `app = FastAPI(title="Telegram Signals API")`
- `GET /health` → `{"status": "ok"}`
- Include router per traders, trades, templates

```bash
PYTHONPATH=. python -c "from src.api.main import app; print('FastAPI app OK')"
```

---

### F4-02 – API REST: traders e trades
**File:** `src/api/routers/traders.py`, `src/api/routers/trades.py`, `src/api/schemas.py`
**Agente:** BACKEND

Endpoint da implementare:
- `GET /traders` → lista tutti i trader
- `POST /traders` → crea trader (body: nome, api keys, chat ids)
- `GET /traders/{id}/trades` → storico trade con paginazione
- `GET /traders/{id}/positions` → posizioni aperte
- `GET /trades/{id}` → singolo trade con dettagli

```bash
PYTHONPATH=. python -c "
from fastapi.testclient import TestClient
from src.api.main import app
client = TestClient(app)
r = client.get('/health')
assert r.status_code == 200
print('API health OK')
"
```

---

### F4-03 – API REST: template management
**File:** `src/api/routers/templates.py`
**Agente:** BACKEND

Endpoint:
- `GET /traders/{id}/templates` → lista template del trader
- `PUT /traders/{id}/templates/{event_type}` → crea/aggiorna template
- `DELETE /traders/{id}/templates/{event_type}` → ripristina default
- `POST /traders/{id}/templates/preview` → preview rendering con dati mock

```bash
PYTHONPATH=. python -c "from src.api.routers.templates import router; print('Templates router OK')"
```

---

### F4-04 – Dashboard frontend
**File:** `src/api/templates/` (HTML), `src/api/static/` (CSS/JS)
**Agente:** BACKEND

Pagine minime:
1. `/` → dashboard con ultimi 10 trade e PnL totale
2. `/templates` → lista template per trader con editor inline
3. `/trades` → storico con filtro per trader e data

Usare Jinja2 server-side (già dipendenza) + HTMX per interattività.
**Nessun framework JS pesante (no React/Vue).**

```bash
PYTHONPATH=. python -c "
from fastapi.testclient import TestClient
from src.api.main import app
client = TestClient(app)
r = client.get('/')
assert r.status_code == 200
print('Dashboard OK')
"
```

---

### F4-05 – Test API
**File:** `tests/unit/test_api.py`
**Agente:** TEST

Creare il file. Testare con `TestClient` e DB in memoria:
```python
from fastapi.testclient import TestClient
```

Test obbligatori:
- `GET /health` → 200
- `POST /traders` → 201 con trader creato
- `GET /traders` → lista con il trader appena creato
- `PUT /traders/{id}/templates/OPEN` → template salvato
- `POST /traders/{id}/templates/preview` → testo renderizzato

```bash
PYTHONPATH=. pytest tests/unit/test_api.py -v
```

---

## Test di chiusura fase

```bash
# Tutti i test
PYTHONPATH=. pytest tests/ -v

# Linter
PYTHONPATH=. ruff check src/api/

# Verifica avvio server (non bloccare — timeout 3s)
PYTHONPATH=. timeout 3 uvicorn src.api.main:app --host 0.0.0.0 --port 8000 || true
```

---

## Note finali
- Questa è l'ultima fase. Al completamento eseguire **tutta** la suite E2E.
- Aggiornare `GAPS_RISKS.md` con qualsiasi funzionalità rimasta fuori scope.
