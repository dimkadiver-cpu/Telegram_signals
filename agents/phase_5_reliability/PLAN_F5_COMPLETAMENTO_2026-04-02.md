# Piano completamento Fase 5 (Reliability & Hardening)

**Data:** 2026-04-02  
**Fonte task:** `docs/tasks/master.yaml`

## 1) Stato attuale F5

Nel `master.yaml` tutte le task F5 sono ancora `todo`:

- F5-01 Distinzione OPEN vs ADD nel lifecycle posizione
- F5-02 Keepalive listenKey Binance user stream
- F5-03 Persistenza e restore stato posizioni su restart
- F5-04 Validazione esplicita token Telegram in init_bot
- F5-05 Timeout FSM edit draft e reset automatico
- F5-06 Retry/backoff su errori Telegram 429
- F5-07 Test resilienza restart stato posizioni
- F5-08 Test resilienza retry Telegram 429
- F5-09 Test longevity stream Binance con keepalive

## 2) Verifica rapida codice corrente vs task F5

### F5-01 (OPEN vs ADD)
- **Stato:** non completata.
- **Evidenza:** `EventNormalizer` mappa attualmente i fill non reduce a `OPEN`, senza discriminare add alla posizione.
- **File coinvolti:** `src/events/normalizer.py`, `src/trade_engine/engine.py`.

### F5-02 (keepalive listenKey)
- **Stato:** non completata.
- **Evidenza:** `BinanceListener` usa reconnect con backoff ma non implementa un loop di keepalive listenKey.
- **File coinvolti:** `src/exchange/binance_listener.py`.

### F5-03 (persistenza/restore posizioni)
- **Stato:** non completata.
- **Evidenza:** `TradeEngine` mantiene stato in `_positions` in memoria.
- **File coinvolti:** `src/trade_engine/engine.py`, `src/db/models.py`.

### F5-04 (validazione token Telegram)
- **Stato:** non completata.
- **Evidenza:** `init_bot` istanzia `Bot(token=token)` senza validazione esplicita né fail-fast con messaggio chiaro.
- **File coinvolti:** `src/telegram/bot.py`.

### F5-05 (timeout FSM edit draft)
- **Stato:** non completata.
- **Evidenza:** FSM di edit (`EditState`) non ha timeout o auto-reset.
- **File coinvolti:** `src/telegram/handlers.py`.

### F5-06 (retry/backoff Telegram 429)
- **Stato:** non completata.
- **Evidenza:** `MessageDispatcher.dispatch()` effettua una sola `send_message` e rilancia eccezioni.
- **File coinvolti:** `src/dispatcher/dispatcher.py`.

### F5-07/F5-08/F5-09 (test resilienza)
- **Stato:** non completate.
- **Evidenza:** non sono presenti test dedicati alle tre aree di resilienza F5.
- **File target:** `tests/integration/`, `tests/e2e/`.

## 3) Sequenza consigliata per chiudere la fase

### Step 1 – Core reliability backend
1. **F5-01**: introdurre regole deterministiche OPEN vs ADD nel normalizer (in base a stato posizione o campi payload Binance).
2. **F5-03**: persistere posizioni attive su DB e ripristino all'avvio (`main`/engine bootstrap).
3. **F5-02**: aggiungere keepalive listenKey + gestione rinnovo/scadenza robusta.

### Step 2 – Telegram hardening
4. **F5-04**: validazione token in `init_bot` (controllo formato + `getMe()` fail-fast opzionale).
5. **F5-05**: timeout FSM edit con reset automatico stato e messaggio utente.
6. **F5-06**: retry/backoff su 429 (gestire `retry_after` se disponibile).

### Step 3 – Test di resilienza (gate di chiusura)
7. **F5-07**: test restart con restore stato posizioni.
8. **F5-08**: test retry dispatcher su errore 429 simulato.
9. **F5-09**: test longevity stream Binance (mock socket + keepalive loop).

## 4) Definition of Done Fase 5

La fase 5 può essere considerata completata quando:

1. `docs/tasks/master.yaml` ha F5-01..F5-09 in `done` con evidenza check.
2. Stato runtime non perde posizioni su restart (test verde).
3. Stream Binance regge sessioni lunghe con keepalive.
4. Telegram è robusto su token errato, timeout FSM e rate limit 429.
5. Esistono test automatizzati per restart/retry/longevity.

## 5) Nota operativa

Le task F5 sono indipendenti dal gate F4 nel `master.yaml` (gate F5 = F3), quindi la fase 5 può essere completata senza attendere la UI F4.
