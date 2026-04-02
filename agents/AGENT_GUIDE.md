# AGENT GUIDE – Regole Generali per Tutti gli Agenti

> Questo file è il contratto operativo per ogni agente che lavora sul progetto.
> Deve essere letto **prima** di iniziare qualsiasi task.

---

## 1. Struttura directory agenti

```
agents/
  AGENT_GUIDE.md              ← questo file (leggi prima di tutto)
  phase_0_setup/
    INSTRUCTIONS.md           ← cosa fare
    STATUS.md                 ← tracciamento avanzamento
    GAPS_RISKS.md             ← gap, rischi, errori trovati
  phase_1_mvp/
    INSTRUCTIONS.md
    STATUS.md
    GAPS_RISKS.md
  phase_2_metrics/
    INSTRUCTIONS.md
    STATUS.md
    GAPS_RISKS.md
  phase_3_multitrader/
    INSTRUCTIONS.md
    STATUS.md
    GAPS_RISKS.md
  phase_4_ui/
    INSTRUCTIONS.md
    STATUS.md
    GAPS_RISKS.md
```

---

## 2. Protocollo obbligatorio prima di iniziare

1. Leggi `TASKS.md` nella root per il quadro completo
2. Leggi `REPO_STRUCTURE.md` per capire dove si trova ogni modulo
3. Leggi `agents/<tua_fase>/INSTRUCTIONS.md` per i dettagli della fase
4. Controlla `agents/<tua_fase>/STATUS.md` — non rifare lavoro già fatto
5. Controlla `agents/<tua_fase>/GAPS_RISKS.md` — leggi i rischi segnalati

---

## 3. Ciclo di lavoro per ogni task

```
1. Segna task come IN PROGRESS in STATUS.md
2. Implementa il codice
3. Esegui i test previsti (vedi sezione Test)
4. Se i test passano → segna DONE in STATUS.md
5. Se trovi gap/rischi → aggiorna GAPS_RISKS.md
6. Commit con messaggio strutturato (vedi sezione Commit)
7. Passa alla task successiva
```

**NON passare alla task successiva se i test della task corrente falliscono.**

---

## 4. Test obbligatori per fase

| Fase | Comando test da eseguire prima di chiudere |
|------|--------------------------------------------|
| Fase 0 | `python -c "from src.config import Settings; Settings()"` |
| Fase 1 | `PYTHONPATH=. pytest tests/unit/ tests/integration/ -v` |
| Fase 2 | `PYTHONPATH=. pytest tests/unit/test_metrics.py -v` |
| Fase 3 | `PYTHONPATH=. pytest tests/integration/test_multi_trader.py -v` |
| Fase 4 | `PYTHONPATH=. pytest tests/unit/test_api.py -v` |
| Sempre | `PYTHONPATH=. pytest tests/e2e/ -v` (solo a fine fase) |

### Linter (sempre, prima del commit)
```bash
PYTHONPATH=. ruff check src/ tests/
```

---

## 5. Formato STATUS.md

Ogni agente aggiorna `STATUS.md` della propria fase usando questa tabella:

```markdown
| Task ID | Titolo                  | Stato      | Agente      | Data       | Note |
|---------|-------------------------|------------|-------------|------------|------|
| F1-01   | Modelli DB Trade/Pos    | ✅ DONE    | agent-db-1  | 2026-04-02 |      |
| F1-02   | Modelli evento          | 🔄 WIP     | agent-be-1  | 2026-04-02 |      |
| F1-03   | Client REST CCXT        | ⏳ TODO    |             |            |      |
```

**Valori Stato:**
- `⏳ TODO` — non iniziata
- `🔄 WIP` — in corso
- `✅ DONE` — completata e testata
- `❌ BLOCKED` — bloccata (motivo in Note)
- `⚠️ REVIEW` — completata ma richiede revisione

---

## 6. Formato GAPS_RISKS.md

Ogni gap, rischio o errore trovato va documentato immediatamente:

```markdown
## [DATA] [TASK_ID] Titolo del problema

**Tipo:** Gap / Rischio / Errore / Decisione pendente
**Severità:** Alta / Media / Bassa
**Descrizione:** ...
**Impatto:** quali task o moduli sono affetti
**Proposta:** soluzione o workaround suggerito
**Stato:** Aperto / Risolto / Accettato
```

---

## 7. Convenzioni di commit

```
<tipo>(<fase>): <descrizione breve>

<dettaglio opzionale>
```

Tipi: `feat`, `fix`, `test`, `refactor`, `chore`
Esempi:
- `feat(f1): implementa TradeEngine con OPEN/ADD/CLOSE`
- `test(f1): aggiunti test unitari trade engine`
- `fix(f2): calcolo RR per posizione short`

---

## 8. Dipendenze tra fasi — non violare l'ordine

```
Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4
```

Una fase può iniziare **solo se la fase precedente ha STATUS = DONE** per tutti i task bloccanti.
Task bloccanti per fase: vedi `INSTRUCTIONS.md` di ogni fase.

---

## 9. Checklist pre-merge

Prima di considerare una fase completa:

- [ ] Tutti i task della fase sono `✅ DONE` in STATUS.md
- [ ] `ruff check src/ tests/` — zero errori
- [ ] Suite test specifica della fase: 100% pass
- [ ] `tests/e2e/test_full_pipeline.py` — pass
- [ ] `GAPS_RISKS.md` aggiornato (anche se vuoto)
- [ ] Commit pushato sul branch corretto

---

## 10. Contesto tecnico rapido

| Componente | Libreria | Versione min |
|------------|----------|-------------|
| Python | — | 3.11 |
| Exchange WS | python-binance | 1.0.19 |
| Exchange REST | ccxt | 4.2 |
| Telegram Bot | aiogram | 3.4 |
| Template | jinja2 | 3.1 |
| ORM | sqlmodel + sqlalchemy | 0.0.16 / 2.0 |
| Config | pydantic-settings | 2.2 |
| Test | pytest + pytest-asyncio | 8.0 / 0.23 |
| Linter | ruff | 0.4 |
