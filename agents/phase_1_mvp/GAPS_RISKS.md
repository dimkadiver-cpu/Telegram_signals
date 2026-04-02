# GAPS & RISKS – Fase 1: MVP Core

---

## Gap e Rischi noti

---

### [2026-04-02] [F1-05] Distinzione ADD vs OPEN non implementata

**Tipo:** Gap
**Severità:** Media
**Descrizione:** L'`EventNormalizer` mappa tutti gli ordini BUY filled su `EventType.OPEN`. Non distingue se esiste già una posizione aperta (in quel caso dovrebbe essere `ADD`).
**Impatto:** Il `TradeEngine` aprirà una nuova posizione invece di aumentare quella esistente.
**Proposta:** Prima di determinare il tipo evento, `EventNormalizer` (o `TradeEngine`) deve consultare lo stato delle posizioni aperte. Richiede accesso al DB o allo stato in memoria del `TradeEngine`.
**Stato:** Aperto — alto priorità per correttezza funzionale

---

### [2026-04-02] [F1-04] Reconnect Binance WS — listenKey expiry

**Tipo:** Rischio
**Severità:** Alta
**Descrizione:** Il User Data Stream Binance richiede il rinnovo del `listenKey` ogni 60 minuti tramite `PUT /api/v3/userDataStream`. Se non rinnovato, il WS si chiude silentemente.
**Impatto:** Il listener smette di ricevere eventi senza errori visibili.
**Proposta:** Aggiungere task asyncio che esegue `keepalive_user_data_stream()` ogni 30 minuti nel `BinanceListener`.
**Stato:** Aperto — da implementare in F1-04

---

### [2026-04-02] [F1-06] Stato posizione solo in memoria

**Tipo:** Gap
**Severità:** Alta
**Descrizione:** `TradeEngine` mantiene lo stato delle posizioni in `_positions: dict` in memoria. Al riavvio del processo, lo stato viene perso.
**Impatto:** Dopo un crash o riavvio, il sistema non sa quali posizioni sono aperte.
**Proposta:** 1) Ricaricare le posizioni aperte dal DB `Position` all'avvio. 2) Persistere ogni aggiornamento di posizione su DB in modo asincrono.
**Stato:** Aperto — critico per produzione

---

### [2026-04-02] [F1-08] Bot token hardcoded non sicuro

**Tipo:** Rischio
**Severità:** Alta
**Descrizione:** Se `.env` non è configurato, il bot viene inizializzato con token vuoto e fallisce silentemente al primo messaggio.
**Proposta:** Validare `telegram_bot_token` non vuoto in `init_bot()` con raise esplicito.
**Stato:** Aperto

---

### [2026-04-02] [F1-09] FSM edit state: nessun timeout

**Tipo:** Gap
**Severità:** Bassa
**Descrizione:** Quando il trader entra nello stato `EditState.waiting_for_text`, la FSM rimane in attesa indefinitamente. Se il trader abbandona senza inviare testo, la bozza rimane bloccata.
**Proposta:** Aggiungere timeout FSM (es. 5 minuti) dopo cui lo stato viene resettato e l'utente notificato.
**Stato:** Aperto

---

### [2026-04-02] [F1-10] Dispatcher: nessun retry su Telegram flood

**Tipo:** Rischio
**Severità:** Media
**Descrizione:** Se Telegram restituisce `TooManyRequests (429)`, il dispatcher fallisce senza retry.
**Proposta:** Implementare exponential backoff per errori 429 di Telegram nel `MessageDispatcher`.
**Stato:** Aperto

---

### [2026-04-02] [F1-11] main.py: ListenerManager non ancora integrato

**Tipo:** Gap
**Severità:** Media
**Descrizione:** `main.py` usa un singolo `BinanceListener` con credenziali da config globale. `ListenerManager` per multi-trader non è ancora integrato nel wiring.
**Impatto:** Sistema supporta un solo trader fino alla Fase 3.
**Proposta:** Accettato come limitazione MVP. Integrare `ListenerManager` in Fase 3.
**Stato:** Accettato — limitazione voluta Fase 1
