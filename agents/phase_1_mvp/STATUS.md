# STATUS – Fase 1: MVP Core

**Stato fase:** ✅ DONE
**Agente:** MVP (BACKEND/DB/TELEGRAM/TEST)
**Ultimo aggiornamento:** 2026-04-02

---

## Avanzamento task

| Task ID | Titolo                          | Stato   | Agente | Data | Note |
|---------|---------------------------------|---------|--------|------|------|
| F1-01   | Modelli DB Trade/Position       | ✅ DONE | setup  | — | Modelli presenti in src/db/models.py |
| F1-02   | Modelli evento normalizzato     | ✅ DONE | setup  | — | TradeEvent, EventType presenti |
| F1-03   | Client REST CCXT                | ✅ DONE | setup  | — | CCXTClient skeleton presente |
| F1-04   | Binance Listener WS             | ✅ DONE | setup  | — | BinanceListener skeleton presente |
| F1-05   | Event Normalizer                | ✅ DONE | setup  | — | EventNormalizer presente |
| F1-06   | Trade Engine                    | ✅ DONE | setup  | — | TradeEngine presente |
| F1-07   | Template Engine base            | ✅ DONE | setup  | — | TemplateRenderer + 6 template .j2 |
| F1-08   | Telegram Bot setup e draft      | ✅ DONE | setup  | — | DraftManager presente |
| F1-09   | Handler approva/modifica/elimina| ✅ DONE | setup  | — | handlers.py con FSM presente |
| F1-10   | Dispatcher invio finale         | ✅ DONE | setup  | — | MessageDispatcher presente |
| F1-11   | Entry point main.py             | ✅ DONE | setup  | — | main.py con wiring presente |
| F1-12   | Test unitari                    | ✅ DONE | MVP    | 2026-04-02 | Unit test F1 verdi (normalizer/engine/template) |
| F1-13   | Test integrazione               | ✅ DONE | MVP    | 2026-04-02 | Integration + E2E pipeline verdi |

---

## Risultati test

| Suite                          | Ultimo risultato | Data | Agente |
|-------------------------------|-----------------|------|--------|
| `tests/unit/test_normalizer`  | ✅ pass         | 2026-04-02 | MVP      |
| `tests/unit/test_trade_engine`| ✅ pass         | 2026-04-02 | MVP      |
| `tests/unit/test_metrics`     | ➖ non scope F1 | 2026-04-02 | MVP      |
| `tests/unit/test_templates`   | ✅ pass         | 2026-04-02 | MVP      |
| `tests/integration/`          | ✅ pass (subset F1) | 2026-04-02 | MVP |
| `tests/e2e/`                  | ✅ pass         | 2026-04-02 | MVP      |

---

## Checklist chiusura fase

- [x] Tutti i task marcati ✅ DONE
- [x] `pytest` subset F1 (`tests/unit/test_normalizer.py tests/unit/test_trade_engine.py tests/unit/test_templates.py tests/integration/test_exchange_to_engine.py tests/integration/test_telegram_flow.py`) — pass
- [x] `pytest tests/e2e/test_full_pipeline.py -v` — pass
- [x] `ruff check` sui file toccati F1 — pass
- [x] GAPS_RISKS.md aggiornato

---

## Distinzione esplicita: completamento fase vs debito tecnico

### Fase completata (delivery)

- Scope MVP F1 consegnato e task `F1-01..F1-13` marcati `done` su `docs/tasks/master.yaml`.
- Regressione F1 (unit/integration/e2e) con esito positivo all'ultimo ciclo validato.

### Debito tecnico residuo (non bloccante per chiusura F1)

- F1-04: keepalive `listenKey` Binance non esplicitato nel listener.
- F1-05: distinzione semantica `OPEN` vs `ADD` non ancora implementata.
- F1-06: stato posizioni solo in memoria (assenza restore/persistenza robusta).
- F1-08: validazione esplicita token bot in bootstrap da irrobustire.
- F1-09: FSM edit senza timeout.
- F1-10: dispatcher senza retry specifico per rate limit `429`.

Nota: i punti sopra sono tracciati operativamente in `GAPS_RISKS.md` e backlog dedicato in `docs/tasks/master.yaml` (fase Reliability).

---

## Note agente

- Corretto mapping `OPEN/CLOSE` nel normalizer Binance usando flag `R` (`reduceOnly`).
- Stabilizzati test F1 con esecuzione coroutine via `asyncio.run(...)` per compatibilità ambienti senza plugin `pytest-asyncio`.
