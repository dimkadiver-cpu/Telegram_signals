# Struttura Repository – Telegram Signals

```
telegram_signals/
│
├── src/                              # Codice sorgente principale
│   ├── exchange/                     # Connessione e ascolto exchange
│   │   ├── __init__.py
│   │   ├── base_listener.py          # Interfaccia astratta listener
│   │   ├── binance_listener.py       # Listener Binance WebSocket (SDK ufficiale)
│   │   └── ccxt_client.py            # Client REST via CCXT (market data, snapshot)
│   │
│   ├── events/                       # Normalizzazione eventi grezzi
│   │   ├── __init__.py
│   │   ├── types.py                  # Enum tipi evento (OPEN, CLOSE, ADD, REDUCE, SL, TP)
│   │   ├── models.py                 # Dataclass/Pydantic modelli evento normalizzato
│   │   └── normalizer.py             # Converte evento raw → TradeEvent standard
│   │
│   ├── trade_engine/                 # Gestione stato posizione
│   │   ├── __init__.py
│   │   ├── position.py               # Modello Position (entry, size, side, pnl...)
│   │   ├── engine.py                 # Trade engine: applica eventi, aggiorna stato
│   │   └── event_handler.py          # Router eventi → azioni engine
│   │
│   ├── metrics/                      # Calcolo metriche di rischio
│   │   ├── __init__.py
│   │   ├── models.py                 # MetricsResult (risk%, riskUSD, RR, delta, leva)
│   │   ├── calculator.py             # Logica calcolo metriche
│   │   └── config.py                 # RiskConfig (capitale, rischio%)
│   │
│   ├── templates/                    # Rendering messaggi Telegram
│   │   ├── __init__.py
│   │   ├── engine.py                 # Jinja2 environment + loader
│   │   ├── renderer.py               # Rendering template con contesto posizione + metriche
│   │   └── default/                  # Template Jinja2 predefiniti
│   │       ├── open.j2
│   │       ├── close.j2
│   │       ├── add.j2
│   │       └── reduce.j2
│   │
│   ├── telegram/                     # Bot Telegram (aiogram)
│   │   ├── __init__.py
│   │   ├── bot.py                    # Setup bot, dispatcher aiogram
│   │   ├── handlers.py               # Handler: approva, modifica, cancella, nota
│   │   ├── keyboards.py              # InlineKeyboard: Approva / Modifica / Elimina
│   │   └── draft_manager.py          # Gestione bozze in attesa di review
│   │
│   ├── db/                           # Persistenza dati
│   │   ├── __init__.py
│   │   ├── models.py                 # SQLModel: Trade, Position, Template, Trader
│   │   ├── session.py                # Sessione async SQLAlchemy
│   │   └── migrations/               # Alembic migrations
│   │       └── env.py
│   │
│   ├── dispatcher/                   # Invio finale messaggi
│   │   ├── __init__.py
│   │   └── dispatcher.py             # Invia messaggio approvato al canale Telegram
│   │
│   └── main.py                       # Entry point: avvia listener + bot in asyncio
│
├── config/                           # Configurazione
│   ├── config.example.yaml           # Esempio configurazione (exchange, bot, db, risk)
│   └── templates/                    # Template personalizzati per trader
│
├── docs/                             # Documentazione e PRD
│   ├── Concept_trading_manual_events_v04.md
│   ├── PRD_MASTER_detailed.md
│   ├── PRD_trading_manual_signal_v04.md
│   ├── PRD_trading_manual_signal_v04-1.md
│   ├── PRD_Fase_1_MVP_detailed-1.md
│   ├── PRD_Fase_2_Metriche_detailed-1.md
│   ├── PRD_Fase_3_MultiTrader_detailed-1.md
│   └── PRD_Fase_4_UI_detailed-1.md
│
├── tests/                            # Test suite
│   ├── unit/
│   │   ├── test_normalizer.py
│   │   ├── test_trade_engine.py
│   │   ├── test_metrics.py
│   │   └── test_templates.py
│   ├── integration/
│   │   ├── test_exchange_to_engine.py
│   │   └── test_telegram_flow.py
│   └── e2e/
│       └── test_full_pipeline.py
│
├── scripts/
│   ├── setup.sh                      # Setup ambiente, DB, dipendenze
│   └── run_dev.sh                    # Avvio sviluppo locale
│
├── TASKS.md                          # Task list per team agenti
├── REPO_STRUCTURE.md                 # Questo file
├── pyproject.toml                    # Dipendenze e metadata progetto
├── requirements.txt                  # requirements (generato da pyproject)
├── .env.example                      # Variabili ambiente di esempio
└── .gitignore
```

## Flusso dati

```
Trader opera su exchange
        ↓
Exchange Listener (Binance WS)
        ↓
Event Normalizer → TradeEvent standard
        ↓
Trade Engine → Position state aggiornato
        ↓
Metric Engine → MetricsResult (risk, RR, leva...)
        ↓
Template Engine → Messaggio Jinja2 renderizzato
        ↓
Telegram Bot → Bozza inviata al trader
        ↓
Trader: Approva / Modifica / Cancella
        ↓
Dispatcher → Messaggio finale inviato al canale
        ↓
DB → Persistenza trade, position, messaggio
```

## Moduli e Responsabilità

| Modulo | Responsabilità | Dipendenze esterne |
|--------|---------------|-------------------|
| `exchange/` | Ricevere eventi raw dall'exchange | Binance SDK, CCXT |
| `events/` | Normalizzare eventi in formato standard | - |
| `trade_engine/` | Mantenere stato posizione | - |
| `metrics/` | Calcolare metriche di rischio | - |
| `templates/` | Renderizzare messaggi | Jinja2 |
| `telegram/` | UI review e invio | aiogram |
| `db/` | Persistenza | SQLModel, SQLAlchemy |
| `dispatcher/` | Invio finale | aiogram |
