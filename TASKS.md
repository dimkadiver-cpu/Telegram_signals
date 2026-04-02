# TASKS – Sistema Telegram Signals (vista sintetica)

> Questo file è una **vista leggibile**. La fonte autoritativa di task/stato/check è `docs/tasks/master.yaml`.

## Regole
- Modificare task, stati e dipendenze **solo** in `docs/tasks/master.yaml`.
- Usare `agents/UNIFIED_AGENT_PROMPT.md` come istruzione operativa unica per gli agenti.

## Fasi

### F0 – Setup & Fondamenta
- F0-01 Inizializza struttura progetto — `done`
- F0-02 Config e Settings — `done`
- F0-03 DB async e migrazioni — `todo`

### F1 – MVP Core
- F1-01 Modelli DB — `done`
- F1-02 Modelli evento normalizzato — `done`
- F1-03 Client REST CCXT — `done`
- F1-04 Listener Binance WS — `done`
- F1-05 Event Normalizer — `done`
- F1-06 Trade Engine — `done`
- F1-07 Template Engine — `done`
- F1-08 Bot Telegram setup e draft — `done`
- F1-09 Handler Telegram — `done`
- F1-10 Dispatcher — `done`
- F1-11 Entry point main.py — `done`
- F1-12 Test unitari fase 1 — `wip`
- F1-13 Test integrazione fase 1 — `todo`

### F2 – Metric Engine
- F2-01 RiskConfig e TraderConfig — `done`
- F2-02 Metric Calculator — `done`
- F2-03 Integrazione metriche nel pipeline — `todo`
- F2-04 Template add/reduce/sl/tp — `done`
- F2-05 Test metriche — `todo`

### F3 – Multi-Trader
- F3-01 Modello Trader e FK — `done`
- F3-02 ListenerManager multi-trader — `done`
- F3-03 Template personalizzati trader — `todo`
- F3-04 Canali Telegram separati — `todo`
- F3-05 Comandi admin Telegram — `todo`
- F3-06 Test multi-trader — `todo`

### F4 – Web UI
- F4-01 Setup FastAPI — `todo`
- F4-02 API REST traders/trades — `todo`
- F4-03 API REST templates — `todo`
- F4-04 Dashboard frontend — `todo`
- F4-05 Test API — `todo`
