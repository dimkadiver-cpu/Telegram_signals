# Fase 2 – Metric Engine
**Agente assegnato:** BACKEND + TEST
**Prerequisiti:** Fase 1 completata (STATUS = ✅ DONE)
**Sblocca:** Fase 3

---

## Obiettivo
Aggiungere calcolo metriche di rischio (risk%, riskUSD, RR, delta, leva) integrate nel pipeline e nei template.

---

## Task da eseguire

### F2-01 – RiskConfig e TraderConfig DB
**File:** `src/metrics/config.py`, aggiornamento `src/db/models.py`
**Agente:** BACKEND

Verificare che `RiskConfig` sia importabile e che `TraderConfig` esista nella tabella DB:
```bash
PYTHONPATH=. python -c "
from src.metrics.config import RiskConfig
r = RiskConfig(capital_usd=10000, risk_pct=1.0)
print('RiskConfig OK:', r)
"
```

Verificare tabella DB:
```bash
PYTHONPATH=. python -c "
import asyncio
from src.db.session import init_db, create_tables
from src.config import Settings
init_db(Settings().database_url)
asyncio.run(create_tables())
from src.db.models import TraderConfig
print('TraderConfig table OK')
"
```

---

### F2-02 – Metric Calculator
**File:** `src/metrics/calculator.py`, `src/metrics/models.py`
**Agente:** BACKEND

```bash
PYTHONPATH=. pytest tests/unit/test_metrics.py -v
```
**Casi da coprire obbligatoriamente:**
- LONG con SL+TP → risk%, riskUSD, RR, delta, leva
- SHORT con SL+TP → verifica segno corretto
- Senza SL → risk_pct e risk_usd = None, delta e leva calcolati
- Leva massima superata → segnare in GAPS_RISKS.md se non gestita

---

### F2-03 – Integrazione nel pipeline
**File:** `src/main.py`, `src/templates/renderer.py`
**Agente:** BACKEND

Aggiornare `main.py` per inserire `MetricCalculator` tra `TradeEngine` e `TemplateRenderer`.
Passare `MetricsResult` al renderer.

Verifica smoke:
```bash
PYTHONPATH=. python -c "
from src.metrics.calculator import MetricCalculator
from src.metrics.config import RiskConfig
from src.trade_engine.position import Position
from src.events.types import Side
from src.templates.renderer import TemplateRenderer
from src.events.types import EventType

pos = Position('t1','BTCUSDT', Side.LONG, 0.1, 40000.0, stop_loss=38000, take_profit=46000)
config = RiskConfig(capital_usd=10000)
metrics = MetricCalculator().calculate(pos, config, 40000)
text = TemplateRenderer().render(EventType.OPEN, pos, metrics)
print(text)
"
```

---

### F2-04 – Template per tutti gli EventType
**File:** `src/templates/default/add.j2`, `reduce.j2`, `sl_hit.j2`, `tp_hit.j2`
**Agente:** BACKEND

Verificare che tutti i template siano presenti e renderizzino senza errori:
```bash
PYTHONPATH=. python -c "
from src.templates.renderer import TemplateRenderer
from src.trade_engine.position import Position
from src.events.types import EventType, Side

pos = Position('t1','ETHUSDT', Side.SHORT, 1.0, 2000.0)
pos.realized_pnl = -100.0
r = TemplateRenderer()
for et in [EventType.OPEN, EventType.CLOSE, EventType.ADD, EventType.REDUCE, EventType.SL_HIT, EventType.TP_HIT]:
    txt = r.render(et, pos)
    assert 'ETHUSDT' in txt, f'Template {et} non contiene symbol'
    print(f'{et}: OK')
"
```

---

### F2-05 – Test metriche completi
**File:** `tests/unit/test_metrics.py`
**Agente:** TEST

```bash
PYTHONPATH=. pytest tests/unit/test_metrics.py -v --tb=short
```

---

## Test di chiusura fase

```bash
# Tutti i test unitari (inclusi metriche)
PYTHONPATH=. pytest tests/unit/ -v

# E2E con metriche
PYTHONPATH=. pytest tests/e2e/test_full_pipeline.py -v

# Linter
PYTHONPATH=. ruff check src/metrics/ src/templates/
```

---

## Dipendenze bloccanti per Fase 3
- F3-01 richiede: F1-01 (DB models aggiornati)
- F3-03 richiede: F2-04 (template personalizzabili)
