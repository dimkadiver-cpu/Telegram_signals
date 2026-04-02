# GAPS & RISKS – Fase 4: Web UI

---

## Gap e Rischi noti

---

### [2026-04-02] [F4-01] Autenticazione API assente

**Tipo:** Rischio
**Severità:** Alta
**Descrizione:** Le API REST non hanno alcun sistema di autenticazione. Chiunque conosca l'URL può leggere trader, trade e template, o modificare configurazioni.
**Impatto:** Esposizione totale dei dati se il server è accessibile da rete pubblica.
**Proposta:** Aggiungere autenticazione HTTP Basic o JWT. Minimo: token API fisso da variabile d'ambiente controllato via middleware FastAPI.
**Stato:** Aperto — bloccante per deploy pubblico

---

### [2026-04-02] [F4-01] FastAPI e main.py: due server asincroni

**Tipo:** Rischio
**Severità:** Media
**Descrizione:** `src/main.py` avvia il bot aiogram con `asyncio.gather`. Aggiungere Uvicorn/FastAPI richiede di integrare i due event loop o avviarli come processi separati.
**Impatto:** `uvicorn.run()` blocca il thread. Non può essere aggiunto direttamente in `asyncio.gather`.
**Proposta:** Usare `uvicorn.Config` + `uvicorn.Server` con `server.serve()` che è awaitable, oppure separare API e bot in processi distinti coordinati da `docker-compose`.
**Stato:** Aperto — decisione architetturale da prendere in F4-01

---

### [2026-04-02] [F4-04] Dashboard: nessuna autenticazione frontend

**Tipo:** Rischio
**Severità:** Alta
**Descrizione:** La dashboard HTML è accessibile senza login. Mostra dati sensibili (API keys, trade history).
**Proposta:** Aggiungere HTTP Basic Auth via middleware FastAPI prima di esporre la dashboard.
**Stato:** Aperto — correlato a F4-01

---

### [2026-04-02] [F4-02] Paginazione trade: non implementata

**Tipo:** Gap
**Severità:** Bassa
**Descrizione:** `GET /traders/{id}/trades` senza paginazione restituirà tutti i trade del DB, potenzialmente migliaia di record.
**Proposta:** Aggiungere parametri `limit` e `offset` (o cursor-based) a tutti gli endpoint di lista.
**Stato:** Aperto

---

### [2026-04-02] [GENERALE] Fase 4 fuori scope MVP

**Tipo:** Decisione pendente
**Severità:** Bassa
**Descrizione:** La Web UI (Fase 4) è esplicitamente indicata nel PRD come Fase 3 della roadmap (dopo multi-trader). Non è necessaria per il funzionamento del sistema.
**Proposta:** Considerare Fase 4 come opzionale. Prioritizzare la stabilità di Fase 1-3 prima di iniziare Fase 4.
**Stato:** Accettato — fase opzionale
