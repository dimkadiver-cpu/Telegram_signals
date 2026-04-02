# GAPS & RISKS – Fase 2: Metric Engine

---

## Gap e Rischi noti

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

### [2026-04-02] [F2-04] Template sl_hit e tp_hit non testati con metriche

**Tipo:** Gap
**Severità:** Bassa
**Descrizione:** I template `sl_hit.j2` e `tp_hit.j2` non ricevono `MetricsResult` nel render perché la posizione è già chiusa quando vengono renderizzati.
**Impatto:** I template di chiusura non mostrano PnL finale corretto.
**Proposta:** Passare `realized_pnl` esplicitamente nel contesto del template di chiusura.
**Stato:** Aperto
