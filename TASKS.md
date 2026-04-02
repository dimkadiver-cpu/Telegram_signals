# TASKS – Sistema Telegram Signals
> Task list completa per team di agenti. Ogni task è autonoma e assegnabile indipendentemente.
> Formato: `[ID] Titolo` → descrizione, input, output, dipendenze.

---

## Legenda stato
- `[ ]` = da fare
- `[~]` = in corso
- `[x]` = completato

## Legenda agente suggerito
- `SETUP` = configurazione repo/ambiente
- `BACKEND` = logica applicativa Python
- `DB` = database e modelli
- `TELEGRAM` = bot e UI Telegram
- `TEST` = testing
- `DEVOPS` = infrastruttura, CI/CD

---

# FASE 0 – Setup & Fondamenta

## F0-01 – Inizializza struttura progetto
**Agente:** SETUP
**Descrizione:** Crea la struttura di directory del progetto come definita in `REPO_STRUCTURE.md`. Inizializza `pyproject.toml` con dipendenze (aiogram, ccxt, python-binance, jinja2, sqlmodel, sqlalchemy, alembic, pydantic, python-dotenv, pytest, pytest-asyncio).
**Input:** `REPO_STRUCTURE.md`
**Output:** Struttura directory creata, `pyproject.toml`, `requirements.txt`, `.gitignore`, `.env.example`
**Dipendenze:** nessuna

## F0-02 – Configura file di configurazione
**Agente:** SETUP
**Descrizione:** Crea `config/config.example.yaml` con sezioni: `exchange` (api_key, api_secret, sandbox), `telegram` (bot_token, review_chat_id), `db` (url), `risk` (capital_usd, risk_pct). Crea classe `Settings` in `src/config.py` che legge da `.env` e/o YAML via pydantic-settings.
**Input:** PRD stack tecnico
**Output:** `config/config.example.yaml`, `src/config.py`, `.env.example`
**Dipendenze:** F0-01

## F0-03 – Setup database e migrazioni
**Agente:** DB
**Descrizione:** Configura SQLite (dev) / PostgreSQL (prod) con SQLAlchemy async. Inizializza Alembic in `src/db/migrations/`. Crea `src/db/session.py` con `AsyncSession` factory e `get_session()` dependency.
**Input:** `src/config.py`
**Output:** `src/db/session.py`, `src/db/migrations/env.py`, migration iniziale vuota
**Dipendenze:** F0-02

---

# FASE 1 – MVP Core

## F1-01 – Modelli DB: Trade, Position
**Agente:** DB
**Descrizione:** Definire in `src/db/models.py` i modelli SQLModel:
- `Trade`: id, trader_id, symbol, side, size, entry_price, exit_price, status, created_at, updated_at
- `Position`: id, trader_id, symbol, side, size, avg_entry, unrealized_pnl, status, created_at
- `TelegramDraft`: id, trade_id, chat_id, message_text, status (pending/approved/rejected/sent), created_at
**Input:** PRD Fase 1, schema pipeline
**Output:** `src/db/models.py`, migration Alembic
**Dipendenze:** F0-03

## F1-02 – Modelli evento normalizzato
**Agente:** BACKEND
**Descrizione:** Creare in `src/events/types.py` l'enum `EventType` (OPEN, CLOSE, ADD, REDUCE, SL_HIT, TP_HIT, LIQUIDATION). Creare in `src/events/models.py` il dataclass `TradeEvent` con campi: `event_type`, `symbol`, `side`, `size`, `price`, `timestamp`, `raw_data`, `trader_id`.
**Input:** PRD pipeline, Concept doc
**Output:** `src/events/types.py`, `src/events/models.py`
**Dipendenze:** F0-01

## F1-03 – Client REST CCXT
**Agente:** BACKEND
**Descrizione:** Implementare `src/exchange/ccxt_client.py`. Classe `CCXTClient` con metodi async: `get_ticker(symbol)`, `get_open_positions()`, `get_order_history(symbol, limit)`. Gestire autenticazione via config. Supporto iniziale Binance Futures.
**Input:** `src/config.py`, docs CCXT
**Output:** `src/exchange/ccxt_client.py`
**Dipendenze:** F0-02, F1-02

## F1-04 – Listener Binance WebSocket
**Agente:** BACKEND
**Descrizione:** Implementare `src/exchange/binance_listener.py`. Classe `BinanceListener` che si connette al User Data Stream Binance. In ascolto su eventi: `ORDER_TRADE_UPDATE` (futures). Per ogni evento chiama callback `on_event(raw_event: dict)`. Gestire reconnect automatico.
**Input:** `src/config.py`, Binance SDK docs
**Output:** `src/exchange/binance_listener.py`, `src/exchange/base_listener.py`
**Dipendenze:** F0-02, F1-02

## F1-05 – Event Normalizer
**Agente:** BACKEND
**Descrizione:** Implementare `src/events/normalizer.py`. Classe `EventNormalizer` con metodo `normalize(raw: dict, source: str) -> TradeEvent | None`. Converte evento raw Binance in `TradeEvent` standard. Filtrare eventi non rilevanti (es. ordini non filled). Mappare status ordine → `EventType`.
**Input:** `src/events/models.py`, `src/events/types.py`, esempi payload Binance
**Output:** `src/events/normalizer.py`
**Dipendenze:** F1-02, F1-04

## F1-06 – Trade Engine: gestione stato posizione
**Agente:** BACKEND
**Descrizione:** Implementare `src/trade_engine/engine.py`. Classe `TradeEngine` con metodo async `process_event(event: TradeEvent) -> Position`. Logica:
- OPEN → crea nuova Position
- ADD → aumenta size, ricalcola avg_entry
- REDUCE → diminuisce size
- CLOSE → chiude posizione, calcola realized PnL
- SL_HIT / TP_HIT → chiude con motivo
Persistere stato su DB.
**Input:** `src/events/models.py`, `src/db/models.py`
**Output:** `src/trade_engine/engine.py`, `src/trade_engine/position.py`
**Dipendenze:** F1-01, F1-02, F1-05

## F1-07 – Template Engine base
**Agente:** BACKEND
**Descrizione:** Implementare `src/templates/engine.py` con Jinja2 environment che carica template da `src/templates/default/`. Creare `src/templates/renderer.py` con `render(event_type, position, metrics=None) -> str`. Creare template `.j2` base per OPEN e CLOSE con placeholder: `{{ symbol }}`, `{{ side }}`, `{{ size }}`, `{{ entry_price }}`, `{{ timestamp }}`.
**Input:** `src/events/types.py`, `src/trade_engine/position.py`
**Output:** `src/templates/engine.py`, `src/templates/renderer.py`, `src/templates/default/open.j2`, `src/templates/default/close.j2`
**Dipendenze:** F1-06

## F1-08 – Bot Telegram: setup e draft
**Agente:** TELEGRAM
**Descrizione:** Implementare `src/telegram/bot.py` con setup aiogram `Bot` e `Dispatcher`. Creare `src/telegram/keyboards.py` con `InlineKeyboardMarkup` per azioni: `✅ Approva`, `✏️ Modifica`, `🗑 Elimina`. Implementare `src/telegram/draft_manager.py`: invia bozza al `review_chat_id` con keyboard e salva `TelegramDraft` su DB.
**Input:** `src/config.py`, `src/db/models.py`
**Output:** `src/telegram/bot.py`, `src/telegram/keyboards.py`, `src/telegram/draft_manager.py`
**Dipendenze:** F1-01, F0-02

## F1-09 – Handler Telegram: approva/modifica/elimina
**Agente:** TELEGRAM
**Descrizione:** Implementare `src/telegram/handlers.py` con callback handler per i 3 bottoni:
- **Approva**: aggiorna `TelegramDraft.status = approved`, chiama dispatcher
- **Modifica**: entra in stato `edit`, attende testo libero, aggiorna draft
- **Elimina**: aggiorna status `rejected`, elimina messaggio bozza
Usare FSM di aiogram per stato modifica.
**Input:** `src/telegram/bot.py`, `src/db/models.py`
**Output:** `src/telegram/handlers.py`
**Dipendenze:** F1-08

## F1-10 – Dispatcher: invio messaggio finale
**Agente:** TELEGRAM
**Descrizione:** Implementare `src/dispatcher/dispatcher.py`. Classe `MessageDispatcher` con metodo async `dispatch(draft: TelegramDraft)`. Invia il testo approvato al canale di destinazione (`target_channel_id` da config). Aggiorna `TelegramDraft.status = sent`. Gestire errori Telegram (flood, chat not found).
**Input:** `src/telegram/bot.py`, `src/db/models.py`, `src/config.py`
**Output:** `src/dispatcher/dispatcher.py`
**Dipendenze:** F1-09

## F1-11 – Entry point e orchestrazione async
**Agente:** BACKEND
**Descrizione:** Implementare `src/main.py`. Avviare in parallelo (asyncio.gather): `BinanceListener`, `aiogram Dispatcher`. Wiring: `BinanceListener.on_event` → `EventNormalizer` → `TradeEngine` → `TemplateRenderer` → `DraftManager`. Gestire shutdown graceful (SIGINT/SIGTERM).
**Input:** tutti i moduli precedenti
**Output:** `src/main.py`
**Dipendenze:** F1-04, F1-05, F1-06, F1-07, F1-08, F1-10

## F1-12 – Test unitari Fase 1
**Agente:** TEST
**Descrizione:** Scrivere test pytest per:
- `test_normalizer.py`: normalizzazione payload Binance mock → TradeEvent corretto
- `test_trade_engine.py`: sequenze OPEN→ADD→CLOSE, verifica stato Position
- `test_templates.py`: rendering template OPEN e CLOSE con dati mock
Usare fixture pytest-asyncio per test async.
**Input:** `src/events/`, `src/trade_engine/`, `src/templates/`
**Output:** `tests/unit/test_normalizer.py`, `tests/unit/test_trade_engine.py`, `tests/unit/test_templates.py`
**Dipendenze:** F1-05, F1-06, F1-07

## F1-13 – Test integrazione: pipeline exchange→telegram
**Agente:** TEST
**Descrizione:** Scrivere `tests/integration/test_exchange_to_engine.py`: simula eventi raw Binance (mock WebSocket), verifica che arrivino a Trade Engine e producano Position corretto. Scrivere `tests/integration/test_telegram_flow.py`: mock aiogram, verifica che draft venga creato e handler risponda correttamente ai callback.
**Input:** `src/main.py`, moduli F1
**Output:** `tests/integration/test_exchange_to_engine.py`, `tests/integration/test_telegram_flow.py`
**Dipendenze:** F1-11, F1-12

---

# FASE 2 – Metric Engine

## F2-01 – Modello RiskConfig
**Agente:** BACKEND
**Descrizione:** Creare `src/metrics/config.py` con classe `RiskConfig`: `capital_usd: float`, `risk_pct: float`, `max_leverage: float`. Caricare da `src/config.py`. Aggiungere a `src/db/models.py` tabella `TraderConfig` per persistere config per trader.
**Input:** PRD Fase 2, `src/config.py`
**Output:** `src/metrics/config.py`, aggiornamento `src/db/models.py`
**Dipendenze:** F1-01, F0-02

## F2-02 – Metric Engine: calcolo metriche
**Agente:** BACKEND
**Descrizione:** Implementare `src/metrics/calculator.py`. Classe `MetricCalculator` con metodo `calculate(position: Position, config: RiskConfig, current_price: float) -> MetricsResult`. Calcoli:
- `risk_pct` = (entry - stop_loss) / entry × 100
- `risk_usd` = capital × risk_pct / 100
- `rr` = (tp - entry) / (entry - sl) (se SL/TP presenti)
- `delta_exposure` = size × current_price
- `effective_leverage` = delta_exposure / capital_usd
**Input:** `src/trade_engine/position.py`, `src/metrics/config.py`
**Output:** `src/metrics/calculator.py`, `src/metrics/models.py`
**Dipendenze:** F2-01, F1-06

## F2-03 – Integrazione metriche nel pipeline
**Agente:** BACKEND
**Descrizione:** Aggiornare `src/main.py` e wiring per inserire `MetricCalculator` dopo `TradeEngine` e prima di `TemplateRenderer`. Passare `MetricsResult` al renderer. Aggiornare i template `.j2` per includere sezione metriche opzionale: `{{ risk_pct }}%`, `${{ risk_usd }}`, `RR {{ rr }}`.
**Input:** `src/metrics/calculator.py`, `src/templates/renderer.py`, `src/main.py`
**Output:** aggiornamento `src/main.py`, template aggiornati
**Dipendenze:** F2-02, F1-07, F1-11

## F2-04 – Template aggiuntivi: ADD, REDUCE, SL, TP
**Agente:** BACKEND
**Descrizione:** Creare template Jinja2 per tutti i tipi evento: `add.j2`, `reduce.j2`, `sl_hit.j2`, `tp_hit.j2`. Includere metriche dove rilevante. Aggiornare `TemplateRenderer` per selezionare template corretto in base a `EventType`.
**Input:** `src/events/types.py`, `src/metrics/models.py`
**Output:** `src/templates/default/add.j2`, `reduce.j2`, `sl_hit.j2`, `tp_hit.j2`
**Dipendenze:** F2-03, F1-07

## F2-05 – Test metriche
**Agente:** TEST
**Descrizione:** Scrivere `tests/unit/test_metrics.py`: test calcoli risk_pct, risk_usd, RR, delta, leva con position e config mock. Coprire casi edge: no SL/TP, posizione short, leva massima superata.
**Input:** `src/metrics/calculator.py`
**Output:** `tests/unit/test_metrics.py`
**Dipendenze:** F2-02

---

# FASE 3 – Multi-Trader

## F3-01 – Modello Trader e isolamento DB
**Agente:** DB
**Descrizione:** Aggiungere a `src/db/models.py` tabella `Trader`: id, name, binance_api_key, binance_api_secret, telegram_review_chat_id, telegram_channel_id, is_active. Aggiungere FK `trader_id` a `Trade`, `Position`, `TelegramDraft`, `TraderConfig`. Creare migration Alembic.
**Input:** `src/db/models.py`, PRD Fase 3
**Output:** aggiornamento `src/db/models.py`, nuova migration
**Dipendenze:** F1-01, F2-01

## F3-02 – Multi-listener: un listener per trader
**Agente:** BACKEND
**Descrizione:** Refactoring `src/exchange/binance_listener.py` per supportare istanze multiple, una per trader. Creare `src/exchange/listener_manager.py`: carica traders attivi da DB, istanzia un `BinanceListener` per ciascuno, li avvia in parallelo. Ogni evento porta `trader_id`.
**Input:** `src/db/models.py`, `src/exchange/binance_listener.py`
**Output:** `src/exchange/listener_manager.py`, refactoring listener
**Dipendenze:** F3-01, F1-04

## F3-03 – Template personalizzati per trader
**Agente:** BACKEND
**Descrizione:** Aggiungere tabella `TraderTemplate` in DB: trader_id, event_type, template_text (Jinja2 string). Aggiornare `TemplateRenderer` per: 1) cercare template personalizzato del trader, 2) fallback al template default. Creare `src/templates/template_store.py` per CRUD template su DB.
**Input:** `src/db/models.py`, `src/templates/renderer.py`
**Output:** `src/templates/template_store.py`, aggiornamento renderer e DB
**Dipendenze:** F3-01, F1-07

## F3-04 – Canali Telegram separati per trader
**Agente:** TELEGRAM
**Descrizione:** Aggiornare `DraftManager` e `MessageDispatcher` per usare `trader.telegram_review_chat_id` e `trader.telegram_channel_id` invece di valori globali da config. Ogni draft è associato a un trader e inviato al canale corretto.
**Input:** `src/db/models.py`, `src/telegram/draft_manager.py`, `src/dispatcher/dispatcher.py`
**Output:** aggiornamento draft_manager e dispatcher
**Dipendenze:** F3-01, F1-08, F1-10

## F3-05 – Handler Telegram: comandi admin
**Agente:** TELEGRAM
**Descrizione:** Aggiungere handlers in `src/telegram/handlers.py` per comandi admin:
- `/add_trader` – wizard interattivo per registrare nuovo trader
- `/list_traders` – elenco traders attivi
- `/toggle_trader <id>` – abilita/disabilita trader
**Input:** `src/db/models.py`, `src/telegram/bot.py`
**Output:** aggiornamento `src/telegram/handlers.py`
**Dipendenze:** F3-01, F1-09

## F3-06 – Test multi-trader
**Agente:** TEST
**Descrizione:** Scrivere `tests/integration/test_multi_trader.py`: simula 2 trader con eventi paralleli, verifica isolamento posizioni, draft e canali. Verificare che evento trader A non contamini stato trader B.
**Input:** moduli F3
**Output:** `tests/integration/test_multi_trader.py`
**Dipendenze:** F3-02, F3-03, F3-04

---

# FASE 4 – Web UI

## F4-01 – Setup framework web
**Agente:** BACKEND
**Descrizione:** Aggiungere FastAPI + Uvicorn alle dipendenze. Creare `src/api/__init__.py`, `src/api/main.py` con app FastAPI. Definire router base `/health`, `/traders`, `/trades`. Integrare con DB session existente.
**Input:** `src/db/session.py`, `src/db/models.py`, PRD Fase 4
**Output:** `src/api/main.py`, `src/api/routers/`
**Dipendenze:** F3-01

## F4-02 – API REST: traders e trades
**Agente:** BACKEND
**Descrizione:** Implementare endpoint REST:
- `GET /traders` – lista traders
- `POST /traders` – crea trader
- `GET /traders/{id}/trades` – storico trade trader
- `GET /traders/{id}/positions` – posizioni aperte
- `GET /trades/{id}` – dettaglio singolo trade
Usare Pydantic schemas per request/response.
**Input:** `src/db/models.py`, `src/api/main.py`
**Output:** `src/api/routers/traders.py`, `src/api/routers/trades.py`, `src/api/schemas.py`
**Dipendenze:** F4-01

## F4-03 – API REST: template management
**Agente:** BACKEND
**Descrizione:** Implementare endpoint:
- `GET /traders/{id}/templates` – lista template trader
- `PUT /traders/{id}/templates/{event_type}` – aggiorna template
- `DELETE /traders/{id}/templates/{event_type}` – ripristina default
- `POST /traders/{id}/templates/preview` – preview rendering con dati mock
**Input:** `src/templates/template_store.py`
**Output:** `src/api/routers/templates.py`
**Dipendenze:** F3-03, F4-01

## F4-04 – Dashboard frontend (base)
**Agente:** BACKEND
**Descrizione:** Creare UI web minimale con HTML/JS (o Jinja2 templates serviti da FastAPI). Pagine: 1) Dashboard con lista trade recenti e PnL, 2) Gestione template con editor, 3) Storico trade con filtri. Nessun framework JS pesante – usare HTMX o vanilla JS.
**Input:** `src/api/routers/`
**Output:** `src/api/templates/` (HTML), `src/api/static/` (CSS/JS)
**Dipendenze:** F4-02, F4-03

## F4-05 – Test API
**Agente:** TEST
**Descrizione:** Scrivere `tests/unit/test_api.py` con `TestClient` di FastAPI. Testare tutti gli endpoint CRUD con DB in-memory. Coprire: creazione trader, trade, aggiornamento template, preview.
**Input:** `src/api/`
**Output:** `tests/unit/test_api.py`
**Dipendenze:** F4-02, F4-03

---

# TRASVERSALE – DevOps & Qualità

## TX-01 – CI/CD: GitHub Actions
**Agente:** DEVOPS
**Descrizione:** Creare `.github/workflows/ci.yml`: installa dipendenze, esegue `pytest tests/unit/` e `pytest tests/integration/` su ogni push/PR. Aggiungere step linting (ruff) e type check (mypy). Target: Python 3.11+.
**Input:** `pyproject.toml`, `tests/`
**Output:** `.github/workflows/ci.yml`
**Dipendenze:** F1-12

## TX-02 – Docker e docker-compose
**Agente:** DEVOPS
**Descrizione:** Creare `Dockerfile` per l'app Python. Creare `docker-compose.yml` con servizi: `app` (telegram_signals), `db` (PostgreSQL). Gestire variabili ambiente via `.env`. Volume per DB persistente.
**Input:** `src/main.py`, `src/config.py`
**Output:** `Dockerfile`, `docker-compose.yml`
**Dipendenze:** F1-11

## TX-03 – Script setup e run
**Agente:** DEVOPS
**Descrizione:** Implementare `scripts/setup.sh` (installa deps, crea `.env` da example, esegue migrations). Implementare `scripts/run_dev.sh` (avvia app in modalità development con reload). Documentare i comandi nel README.
**Input:** `pyproject.toml`, `src/db/migrations/`
**Output:** `scripts/setup.sh`, `scripts/run_dev.sh`
**Dipendenze:** F0-03

## TX-04 – Test E2E pipeline completa
**Agente:** TEST
**Descrizione:** Scrivere `tests/e2e/test_full_pipeline.py`: avvia sistema completo con exchange mock (simula WS Binance), invia sequenza eventi OPEN→ADD→CLOSE, verifica che: 1) draft Telegram creato, 2) metriche calcolate, 3) messaggio inviato dopo approvazione mock, 4) DB aggiornato correttamente.
**Input:** tutti i moduli
**Output:** `tests/e2e/test_full_pipeline.py`
**Dipendenze:** F1-13, F2-05, F3-06

---

# Riepilogo Task per Fase

| Fase | Task ID | N. Task |
|------|---------|---------|
| Fase 0 – Setup | F0-01 → F0-03 | 3 |
| Fase 1 – MVP | F1-01 → F1-13 | 13 |
| Fase 2 – Metriche | F2-01 → F2-05 | 5 |
| Fase 3 – Multi-Trader | F3-01 → F3-06 | 6 |
| Fase 4 – Web UI | F4-01 → F4-05 | 5 |
| Trasversale | TX-01 → TX-04 | 4 |
| **TOTALE** | | **36** |

---

# Grafo dipendenze critico (Fase 1)

```
F0-01 → F0-02 → F0-03
                  ↓
F0-03 → F1-01 (DB models)
F0-01 → F1-02 (Event models)
F1-02 → F1-03, F1-04
F1-04 → F1-05 (Normalizer)
F1-05 → F1-06 (Trade Engine)
F1-06 → F1-07 (Templates)
F1-07 → F1-08 (Telegram Bot)
F1-08 → F1-09 (Handlers)
F1-09 → F1-10 (Dispatcher)
F1-10 → F1-11 (main.py)
F1-11 → F1-12 → F1-13
```
