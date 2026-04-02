# GAPS & RISKS – Fase 3: Multi-Trader

---

## Gap e Rischi noti

---

### [2026-04-02] [F3-01] Migrazione schema DB con dati esistenti

**Tipo:** Rischio
**Severità:** Alta
**Descrizione:** L'aggiunta di `trader_id` come FK obbligatoria su `Trade`, `Position`, `TelegramDraft` rompe il DB esistente se ci sono righe senza `trader_id`.
**Impatto:** Il DB di sviluppo va ricreato da zero. In produzione i dati storici vengono persi.
**Proposta:** 1) In sviluppo: cancellare e ricreare il DB. 2) Prima di andare in produzione: scrivere migration Alembic con valore default temporaneo per `trader_id`. 3) Configurare Alembic correttamente in questa fase.
**Stato:** Aperto — alta priorità

---

### [2026-04-02] [F3-02] Credenziali API per trader in DB non cifrate

**Tipo:** Rischio
**Severità:** Alta
**Descrizione:** `Trader.binance_api_key` e `Trader.binance_api_secret` sono salvati in chiaro nel DB SQLite/PostgreSQL.
**Impatto:** Chiunque abbia accesso al DB può leggere le credenziali exchange di tutti i trader.
**Proposta:** Cifrare le credenziali con `cryptography.fernet` prima di salvarle. Usare una chiave di cifratura da variabile d'ambiente.
**Stato:** Aperto — bloccante per sicurezza in produzione

---

### [2026-04-02] [F3-02] ListenerManager non gestisce aggiunta dinamica trader

**Tipo:** Gap
**Severità:** Media
**Descrizione:** `ListenerManager.start_all()` carica i trader all'avvio e non aggiorna la lista se un trader viene aggiunto/rimosso mentre il sistema è in esecuzione.
**Impatto:** Per aggiungere un nuovo trader bisogna riavviare il processo.
**Proposta:** Aggiungere metodi `add_trader(trader)` e `remove_trader(trader_id)` al `ListenerManager` e chiamarli dal handler `/add_trader`.
**Stato:** Aperto

---

### [2026-04-02] [F3-05] Wizard /add_trader: API key non validata

**Tipo:** Rischio
**Severità:** Media
**Descrizione:** Il wizard raccoglie le credenziali Binance ma non le verifica prima di salvarle nel DB. Un errore di battitura causerebbe un listener che non funziona.
**Proposta:** Dopo la raccolta, eseguire `CCXTClient.get_open_positions()` come test di connessione. Se fallisce, non salvare e notificare l'errore.
**Stato:** Aperto

---

### [2026-04-02] [F3-03] TemplateStore: nessun caching

**Tipo:** Gap
**Severità:** Bassa
**Descrizione:** `TemplateStore` eseguirà una query DB per ogni evento processato per cercare il template personalizzato del trader.
**Impatto:** Possibile collo di bottiglia con molti trader e alto volume di eventi.
**Proposta:** Aggiungere cache in memoria con invalidazione quando il template viene aggiornato.
**Stato:** Aperto — ottimizzazione futura
