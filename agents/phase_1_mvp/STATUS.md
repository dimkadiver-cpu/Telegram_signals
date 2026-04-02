# STATUS – Fase 1: MVP Core

**Stato fase:** ⏳ TODO
**Agente:** —
**Ultimo aggiornamento:** —

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
| F1-12   | Test unitari                    | 🔄 WIP  | —      | — | Skeleton presenti, da validare tutti |
| F1-13   | Test integrazione               | ⏳ TODO | —      | — | Da completare dopo F1-12 |

---

## Risultati test

| Suite                          | Ultimo risultato | Data | Agente |
|-------------------------------|-----------------|------|--------|
| `tests/unit/test_normalizer`  | ⏳ da eseguire  | —    | —      |
| `tests/unit/test_trade_engine`| ⏳ da eseguire  | —    | —      |
| `tests/unit/test_metrics`     | ⏳ da eseguire  | —    | —      |
| `tests/unit/test_templates`   | ⏳ da eseguire  | —    | —      |
| `tests/integration/`          | ⏳ da eseguire  | —    | —      |
| `tests/e2e/`                  | ⏳ da eseguire  | —    | —      |

---

## Checklist chiusura fase

- [ ] Tutti i task marcati ✅ DONE
- [ ] `pytest tests/unit/ tests/integration/ -v` — 100% pass
- [ ] `pytest tests/e2e/test_full_pipeline.py -v` — pass
- [ ] `ruff check src/ tests/` — zero errori
- [ ] GAPS_RISKS.md aggiornato

---

## Note agente

<!-- Aggiungere note operative qui -->
