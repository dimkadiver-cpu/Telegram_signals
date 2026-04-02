# AGENT GUIDE – Regole Generali per Tutti gli Agenti

> Documento di governance. Non contiene backlog operativo: la fonte task/stato/check è `docs/tasks/master.yaml`.

---

## 1. Fonti documentali (ordine obbligatorio)

1. `docs/tasks/master.yaml` (task, dipendenze, stato, acceptance checks)
2. `docs/PRD_MASTER_detailed.md` + PRD di fase (`docs/PRD_Fase_*`)
3. `REPO_STRUCTURE.md` (mappa moduli)
4. `agents/UNIFIED_AGENT_PROMPT.md` (prompt operativo unico)
5. `agents/phase_<fase>/STATUS.md` e `GAPS_RISKS.md` (contesto locale)

---

## 2. Workflow operativo standard

1. Seleziona una sola task candidabile (dipendenze soddisfatte).
2. Aggiorna stato task in `master.yaml` (`todo -> wip`).
3. Implementa la modifica minima necessaria.
4. Esegui acceptance checks della task.
5. Se i check passano: imposta `done`.
6. Se emergono blocchi: imposta `blocked` e documenta in `GAPS_RISKS.md`.

**Non marcare `done` senza evidenza dei check.**

---

## 3. Convenzioni stato

Valori ammessi in `master.yaml`:
- `todo`
- `wip`
- `done`
- `blocked`
- `review`

---

## 4. Commit convention

Formato:

```text
<tipo>(<scope>): <descrizione breve>
```

Tipi: `feat`, `fix`, `test`, `refactor`, `chore`, `docs`.

Esempi:
- `feat(f1): implementa TradeEngine OPEN/ADD/CLOSE`
- `test(f2): completa copertura metric calculator`
- `docs(agents): aggiorna prompt unificato`

---

## 5. Qualità minima

Prima del commit, eseguire i check previsti dalla task in `master.yaml`.

Check globali consigliati:
```bash
PYTHONPATH=. ruff check src/ tests/
```

---

## 6. Escalation

Aprire/aggiornare `GAPS_RISKS.md` quando:
- manca una dipendenza tecnica;
- c'è ambiguità nei requisiti;
- i check non sono ripristinabili nel contesto corrente.

Template minimo:

```markdown
## [DATA] [TASK_ID] Titolo
**Tipo:** Gap / Rischio / Errore / Decisione
**Severità:** Alta / Media / Bassa
**Descrizione:** ...
**Impatto:** ...
**Proposta:** ...
**Stato:** Aperto / Risolto / Accettato
```
