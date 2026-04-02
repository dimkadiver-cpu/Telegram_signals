# STATUS – Fase 2: Metric Engine

**Stato fase:** ⏳ TODO (attende Fase 1)
**Agente:** —
**Ultimo aggiornamento:** —

---

## Avanzamento task

| Task ID | Titolo                        | Stato   | Agente | Data | Note |
|---------|-------------------------------|---------|--------|------|------|
| F2-01   | RiskConfig e TraderConfig DB  | ✅ DONE | setup  | — | Skeleton presente |
| F2-02   | Metric Calculator             | ✅ DONE | setup  | — | Skeleton presente |
| F2-03   | Integrazione nel pipeline     | ⏳ TODO | —      | — | main.py da aggiornare con MetricCalculator |
| F2-04   | Template per tutti EventType  | ✅ DONE | setup  | — | 6 template .j2 presenti |
| F2-05   | Test metriche completi        | ⏳ TODO | —      | — | Skeleton presente, da completare copertura |

---

## Risultati test

| Suite                        | Ultimo risultato | Data | Agente |
|-----------------------------|-----------------|------|--------|
| `tests/unit/test_metrics`   | ⏳ da eseguire  | —    | —      |
| `tests/e2e/`                | ⏳ da eseguire  | —    | —      |

---

## Checklist chiusura fase

- [ ] Fase 1 completata
- [ ] `pytest tests/unit/test_metrics.py -v` — 100% pass
- [ ] Pipeline smoke: render con metriche funzionante
- [ ] Tutti i 6 EventType renderizzano senza errori
- [ ] `pytest tests/e2e/ -v` — pass
- [ ] GAPS_RISKS.md aggiornato

---

## Note agente

<!-- Aggiungere note operative qui -->
