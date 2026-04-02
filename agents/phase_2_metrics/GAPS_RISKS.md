# GAPS & RISKS – Fase 2: Metric Engine

---

## Gap e Rischi noti

### [2026-04-02] [F2-02] Calcolo rischio direction-aware implementato

**Tipo:** Aggiornamento
**Severità:** —
**Descrizione:** Il `MetricCalculator` ora calcola rischio/reward in modo coerente con il lato posizione (`LONG`/`SHORT`), ignorando SL/TP non validi direzionalmente e gestendo l'assenza di SL/TP senza rompere il rendering.
**Impatto:** Riduzione falsi positivi nelle metriche (es. RR negativo o rischio non sensato).
**Stato:** Chiuso

---

### [2026-04-02] [F2-02] SL/TP non sempre disponibili dall'exchange

**Tipo:** Gap
**Severità:** Media
**Descrizione:** Non tutti gli exchange forniscono SL e TP nell'evento ordine. Su Binance Futures, SL e TP sono ordini separati (STOP_MARKET, TAKE_PROFIT_MARKET) e non sono collegati all'ordine di apertura.
**Impatto:** `MetricCalculator` riceve `stop_loss=None` e `take_profit=None` nella maggior parte dei casi reali. risk_pct e RR non vengono calcolati.
**Proposta:** 1) Permettere all'utente di impostare SL/TP manualmente via Telegram prima dell'approvazione del draft. 2) Monitorare ordini STOP/TP separati e associarli alla posizione.
**Stato:** Aperto — impatto alto sulla qualità del segnale

---

### [2026-04-02] [F2-02] Leva effettiva: capital_usd fisso non riflette il reale

**Tipo:** Gap
**Severità:** Bassa
**Descrizione:** `effective_leverage = delta_exposure / capital_usd` usa il capitale configurato staticamente. Non riflette il margine effettivamente usato sull'exchange.
**Proposta:** Usare CCXT per ottenere il margine disponibile in tempo reale tramite `fetch_balance()`.
**Stato:** Aperto — miglioramento futuro

---

### [2026-04-02] [F2-03] MetricCalculator usa `current_price = event.price`

**Tipo:** Gap
**Severità:** Bassa
**Descrizione:** Il prezzo corrente per calcolare `delta_exposure` è il prezzo dell'ultimo evento, non il mark price attuale.
**Impatto:** Per posizioni ADD/REDUCE, la delta exposure è leggermente sbagliata.
**Proposta:** Chiamare `CCXTClient.get_ticker(symbol)` per ottenere il mark price prima di chiamare `MetricCalculator`.
**Stato:** Aperto

---

### [2026-04-02] [F2-04] Copertura test incompleta per template sl_hit/tp_hit

**Tipo:** Gap
**Severità:** Bassa
**Descrizione:** I template `sl_hit.j2` e `tp_hit.j2` non dipendono da `MetricsResult` (la posizione è già chiusa) ma mancavano test unitari diretti sul loro rendering.
**Impatto:** Rischio regressioni non rilevate sui messaggi di chiusura, pur avendo il PnL già presente tramite `realized_pnl`.
**Proposta:** Aggiungere test unitari dedicati per `SL_HIT`/`TP_HIT` e mantenere il passaggio di `realized_pnl` nel context renderer.
**Stato:** Chiuso — copertura test aggiunta in `tests/unit/test_templates.py`

---

### [2026-04-02] [F2-04] Template ADD può mostrare leva `None`

**Tipo:** Gap
**Severità:** Bassa
**Descrizione:** In `add.j2` la leva veniva sempre renderizzata se esisteva `metrics`, anche quando `effective_leverage=None`.
**Impatto:** Output telegram ambiguo (es. `Leva: Nonex`) in configurazioni senza `capital_usd`.
**Proposta:** Renderizzare `Leva` solo con check esplicito `metrics.effective_leverage is not none`.
**Stato:** Chiuso — fix applicato in `src/templates/default/add.j2`
