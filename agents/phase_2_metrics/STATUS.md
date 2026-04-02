# STATUS – Fase 2: Metric Engine

**Stato fase:** ✅ DONE
**Agente:** BACKEND/TEST
**Ultimo aggiornamento:** 2026-04-02

---

## Avanzamento task

| Task ID | Titolo                        | Stato   | Agente | Data | Note |
|---------|-------------------------------|---------|--------|------|------|
| F2-01   | RiskConfig e TraderConfig DB  | ✅ DONE | setup  | — | Skeleton presente |
| F2-02   | Metric Calculator             | ✅ DONE | setup  | — | Skeleton presente |
| F2-03   | Integrazione nel pipeline     | ✅ DONE | backend/test | 2026-04-02 | `main.py` integra `MetricCalculator` nel flusso render draft |
| F2-04   | Template per tutti EventType  | ✅ DONE | setup  | — | 6 template .j2 presenti |
| F2-05   | Test metriche completi        | ✅ DONE | backend/test | 2026-04-02 | Coperti casi long/short, assenza SL/TP e compatibilità template |

---

## Risultati test

| Suite                        | Ultimo risultato | Data | Agente |
|-----------------------------|-----------------|------|--------|
| `tests/unit/test_metrics`   | ✅ pass (`5 passed`)  | 2026-04-02 | backend/test |
| `tests/unit/test_templates` | ✅ pass (`7 passed`)  | 2026-04-02 | backend/test |
| `tests/e2e/test_full_pipeline.py` | ✅ pass (`1 passed`)  | 2026-04-02 | backend/test |

---

## Checklist chiusura fase

- [x] Fase 1 completata
- [x] `pytest tests/unit/test_metrics.py -v` — pass
- [x] Pipeline smoke: render con metriche funzionante
- [x] Tutti i 6 EventType renderizzano senza errori
- [x] `pytest tests/e2e/test_full_pipeline.py -v` — pass
- [x] GAPS_RISKS.md aggiornato

---

## Note agente

- Metriche rischio rese side-aware (`LONG`/`SHORT`) e robustite per assenza di SL/TP.
- Template `open.j2` aggiornato per non renderizzare valori `None`.

---

## Debito tecnico residuo F2

- SL/TP spesso non disponibili dal solo evento exchange: servono integrazione ordini condizionati o input manuale utente.
- `effective_leverage` resta basata su `capital_usd` statico, non sul margine realtime exchange.
- `delta_exposure` usa `event.price` e non mark price live: precisione migliorabile.
