# Telegram Signals

Sistema automatizzato di segnalizzazione trading manuale via Telegram. Monitora in tempo reale le operazioni di uno o più trader su exchange crypto (Binance/Bybit) e pubblica segnali formattati su canali Telegram, con un passaggio obbligatorio di **review e approvazione** da parte del trader prima dell'invio pubblico.

---

## Indice

- [Funzionamento](#funzionamento)
- [Flusso di lavoro](#flusso-di-lavoro)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Configurazione](#configurazione)
- [Avvio](#avvio)
- [Gestione dei trader](#gestione-dei-trader)
- [Comandi Telegram](#comandi-telegram)
- [Template messaggi](#template-messaggi)
- [Database](#database)
- [Sviluppo e test](#sviluppo-e-test)

---

## Funzionamento

```
Exchange (WebSocket)
        │
        ▼
  Event Normalizer     ← classifica l'evento (OPEN, CLOSE, SL_HIT, ecc.)
        │
        ▼
  Trade Engine         ← aggiorna lo stato della posizione in memoria
        │
        ▼
  Metrics Calculator   ← calcola risk%, risk$, RR, leva
        │
        ▼
  Template Renderer    ← renderizza il messaggio con Jinja2
        │
        ▼
  Draft Manager        ← invia bozza al trader su Telegram (inline keyboard)
        │
   [Approva] [Modifica] [Cancella]
        │
        ▼
  Dispatcher           ← invia il messaggio finale al canale pubblico
```

Ogni trader ha un **listener WebSocket dedicato e isolato**. Al riavvio del sistema le posizioni aperte vengono ripristinate dal database.

---

## Flusso di lavoro

1. Il trader apre/modifica una posizione sull'exchange.
2. Il listener WebSocket riceve l'evento e lo normalizza.
3. Il Trade Engine aggiorna lo stato della posizione (entry medio, size, PnL).
4. Il Metrics Calculator calcola le metriche di rischio.
5. Il Template Renderer compone il messaggio.
6. La **bozza** viene inviata al trader nella sua chat privata di review.
7. Il trader sceglie:
   - **Approva** → il messaggio viene pubblicato nel canale
   - **Modifica** → viene aperta una sessione FSM per riscrivere il testo (timeout 5 min)
   - **Cancella** → la bozza viene scartata
8. Il Dispatcher invia il messaggio finale al canale Telegram con retry automatico.

---

## Requisiti

- Python >= 3.11
- Un bot Telegram (token ottenibile da [@BotFather](https://t.me/BotFather))
- API key Binance Futures o Bybit (con permessi di lettura)
- SQLite (sviluppo) o PostgreSQL (produzione)

---

## Installazione

```bash
git clone https://github.com/dimkadiver-cpu/telegram_signals.git
cd telegram_signals

python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# oppure: .venv\Scripts\activate  # Windows

pip install -e .
# Includere dipendenze di sviluppo:
# pip install -e ".[dev]"
```

---

## Configurazione

### 1. File `.env`

Copia il file di esempio e compilalo:

```bash
cp .env.example .env
```

| Variabile | Descrizione | Default |
|-----------|-------------|---------|
| `BINANCE_API_KEY` | API key Binance Futures | `""` |
| `BINANCE_API_SECRET` | API secret Binance Futures | `""` |
| `BINANCE_TESTNET` | Usa il testnet Binance | `false` |
| `BYBIT_API_KEY` | API key Bybit (opzionale) | `""` |
| `BYBIT_API_SECRET` | API secret Bybit | `""` |
| `BYBIT_TESTNET` | Usa il testnet Bybit | `false` |
| `TELEGRAM_BOT_TOKEN` | Token del bot Telegram | `""` |
| `TELEGRAM_REVIEW_CHAT_ID` | ID della chat privata dove arrivano le bozze | `""` |
| `TELEGRAM_CHANNEL_ID` | ID del canale pubblico di output | `""` |
| `DATABASE_URL` | URL connessione database | `sqlite+aiosqlite:///./telegram_signals.db` |
| `RISK_CAPITAL_USD` | Capitale totale in USD per il calcolo del rischio | `10000.0` |
| `RISK_PCT` | Percentuale di capitale rischiata per trade | `1.0` |
| `BREAKEVEN_TOLERANCE_PCT` | Tolleranza % per classificare uno SL come breakeven | `0.5` |

Esempio `.env`:

```env
BINANCE_API_KEY=la_tua_api_key
BINANCE_API_SECRET=il_tuo_api_secret
BINANCE_TESTNET=false

TELEGRAM_BOT_TOKEN=123456789:AABBcc...
TELEGRAM_REVIEW_CHAT_ID=-100123456789
TELEGRAM_CHANNEL_ID=@mio_canale_segnali

DATABASE_URL=sqlite+aiosqlite:///./telegram_signals.db

RISK_CAPITAL_USD=10000.0
RISK_PCT=1.0
BREAKEVEN_TOLERANCE_PCT=0.5
```

> **Produzione**: usa PostgreSQL come database URL:
> ```
> DATABASE_URL=postgresql+asyncpg://user:password@localhost/telegram_signals
> ```

### 2. Come ottenere gli ID Telegram

- **Bot token**: crea un bot con [@BotFather](https://t.me/BotFather) e copia il token.
- **Review chat ID**: aggiungi il bot alla tua chat privata o gruppo, poi usa `@userinfobot` o le API Telegram per ottenere l'ID.
- **Channel ID**: aggiungi il bot al canale come amministratore. L'ID del canale inizia solitamente con `-100`.

### 3. Configurazione per-trader (nel DB)

Ogni trader può avere parametri di rischio personalizzati, gestibili tramite il database (`TraderConfig`):

| Campo | Descrizione | Default |
|-------|-------------|---------|
| `capital_usd` | Capitale del trader | `10000.0` |
| `risk_pct` | % rischio per trade | `1.0` |
| `max_leverage` | Leva massima | `10.0` |

---

## Avvio

```bash
# Assicurarsi di essere nell'ambiente virtuale
source .venv/bin/activate

python -m src.main
```

Al primo avvio il sistema:
1. Inizializza il database e crea le tabelle.
2. Avvia il bot Telegram in polling.
3. Carica i trader attivi dal DB e avvia un listener WebSocket per ognuno.
4. Ripristina le posizioni aperte in memoria.

Per fermare il sistema usa `Ctrl+C` (SIGINT) o invia SIGTERM: lo shutdown è graceful.

---

## Gestione dei trader

I trader vengono registrati nel database e ogni trader attivo (`is_active=True`) ottiene un listener WebSocket dedicato sull'exchange configurato.

### Modello dati Trader

| Campo | Descrizione |
|-------|-------------|
| `id` | ID univoco (auto) |
| `name` | Nome del trader |
| `binance_api_key` | API key Binance del trader |
| `binance_api_secret` | API secret Binance del trader |
| `telegram_review_chat_id` | Chat dove il trader riceve le bozze |
| `telegram_channel_id` | Canale pubblico di output del trader |
| `is_active` | Abilita/disabilita il monitoraggio |
| `exchange` | `"binance"` oppure `"bybit"` |

---

## Comandi Telegram

I comandi si inviano al bot dalla chat di review.

| Comando | Descrizione |
|---------|-------------|
| `/add_trader` | Avvia la procedura guidata per aggiungere un nuovo trader (FSM multi-step: nome → API key → API secret → review chat ID → channel ID). Il listener WebSocket viene avviato automaticamente al termine. |
| `/list_traders` | Elenca tutti i trader registrati con ID, nome, chat di review, canale e stato (active/inactive). |

### Inline keyboard sulle bozze

Quando arriva una bozza in review vengono mostrati tre pulsanti:

| Pulsante | Azione |
|----------|--------|
| Approva | Pubblica il messaggio nel canale |
| Modifica | Apre sessione di editing (timeout 5 min) |
| Cancella | Scarta la bozza |

---

## Template messaggi

I messaggi sono generati con **Jinja2**. I template di default si trovano in `src/templates/default/`.

| File template | Evento |
|---------------|--------|
| `open.j2` | Apertura posizione |
| `close.j2` | Chiusura posizione / Liquidazione |
| `add.j2` | DCA — aggiunta size |
| `reduce.j2` | Chiusura parziale |
| `sl_hit.j2` | Stop loss colpito |
| `tp_hit.j2` | Take profit colpito |
| `sl_to_breakeven.j2` | SL spostato a breakeven |
| `sl_to_profit.j2` | SL spostato in profitto |
| `tp_modified.j2` | Take profit modificato |
| `tp_added.j2` | Nuovo livello TP aggiunto |
| `order_cancelled.j2` | Ordine cancellato |

### Variabili disponibili nei template

```jinja2
{{ symbol }}          {# es. BTCUSDT #}
{{ side }}            {# LONG o SHORT #}
{{ size }}            {# quantità #}
{{ entry_price }}     {# prezzo di ingresso medio #}
{{ stop_loss }}       {# prezzo SL (None se assente) #}
{{ take_profit }}     {# primo TP (None se assente) #}
{{ take_profits }}    {# lista di tutti i TP #}
{{ realized_pnl }}    {# PnL realizzato (su CLOSE) #}
{{ metrics.risk_pct }}         {# rischio % sul capitale #}
{{ metrics.risk_usd }}         {# rischio in USD #}
{{ metrics.rr }}               {# rapporto rischio/rendimento #}
{{ metrics.effective_leverage }}{# leva effettiva #}
```

### Template personalizzati per trader

È possibile salvare nel DB (`TraderTemplate`) template Jinja2 custom per singolo trader e per ogni tipo di evento. Il sistema li carica automaticamente al momento del render.

Esempio template custom per `OPEN`:

```
📈 *{{ side }} {{ symbol }}*
Ingresso: {{ entry_price }} | SL: {{ stop_loss }}
Rischio: {{ metrics.risk_pct }}% — RR: {{ metrics.rr }}
```

---

## Database

### Schema

Il database contiene 6 tabelle principali:

- **`trader`** — anagrafica trader
- **`trade`** — storico singole operazioni
- **`position`** — posizioni aperte/chiuse con stato corrente
- **`telegramdraft`** — bozze messaggi con stato (PENDING / APPROVED / REJECTED / SENT)
- **`traderconfig`** — configurazione rischio per-trader
- **`tradertemplate`** — template Jinja2 custom per-trader

### SQLite (sviluppo)

Il file `telegram_signals.db` viene creato automaticamente nella directory di lavoro al primo avvio.

### PostgreSQL (produzione)

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/telegram_signals
```

Le migrazioni sono gestite con **Alembic** (configurazione in `src/db/migrations/`).

---

## Sviluppo e test

```bash
# Installare dipendenze dev
pip install -e ".[dev]"

# Eseguire i test
pytest

# Linter
ruff check src/

# Type check
mypy src/
```

### Struttura del progetto

```
src/
├── main.py                # Entry point, wiring della pipeline
├── config.py              # Variabili d'ambiente (Pydantic Settings)
├── exchange/
│   ├── binance_listener.py    # Listener WebSocket Binance
│   ├── bybit_listener.py      # Listener WebSocket Bybit
│   └── listener_manager.py    # Gestione multi-trader
├── events/
│   ├── normalizer.py          # Raw event → TradeEvent standard
│   ├── models.py              # Modello TradeEvent
│   └── types.py               # Enum EventType
├── trade_engine/
│   ├── engine.py              # State machine posizioni
│   └── position.py            # Modello Position in memoria
├── metrics/
│   ├── calculator.py          # Calcolo rischio/RR/leva
│   ├── models.py              # MetricsResult
│   └── config.py              # RiskConfig
├── templates/
│   ├── default/               # Template Jinja2 di default
│   ├── renderer.py            # Selezione e rendering template
│   ├── engine.py              # Wrapper Jinja2
│   └── store.py               # Caricamento template custom dal DB
├── telegram/
│   ├── bot.py                 # Inizializzazione aiogram Bot + Dispatcher
│   ├── handlers.py            # Callback e command handlers
│   ├── draft_manager.py       # Invio bozze con inline keyboard
│   └── keyboards.py           # Definizione inline keyboards
├── dispatcher/
│   └── dispatcher.py          # Invio finale al canale con retry
└── db/
    ├── models.py              # Modelli SQLModel
    ├── session.py             # Inizializzazione DB e sessioni
    └── position_repository.py # Persistenza posizioni
config/
└── config.example.yaml        # Riferimento configurazione YAML
```

---

## Dipendenze principali

| Libreria | Uso |
|----------|-----|
| `aiogram >= 3.4` | Bot Telegram async |
| `ccxt >= 4.2` | Connessione exchange |
| `python-binance >= 1.0.19` | Binance WebSocket user data stream |
| `jinja2 >= 3.1` | Rendering template messaggi |
| `sqlmodel >= 0.0.16` | ORM async (SQLAlchemy + Pydantic) |
| `aiosqlite >= 0.19` | Driver SQLite asincrono |
| `asyncpg >= 0.29` | Driver PostgreSQL asincrono |
| `alembic >= 1.13` | Migrazioni database |
| `pydantic-settings >= 2.2` | Gestione variabili d'ambiente |
