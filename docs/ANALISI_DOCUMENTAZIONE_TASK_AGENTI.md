# Analisi documentazione: ridondanza vs complementarità

## Obiettivo
Valutare se la documentazione attuale (PRD, task list, guide agenti e istruzioni per fase) sia ridondante o complementare, e proporre una struttura unica centrata sulle task, estendibile dagli agenti.

---

## Documenti analizzati
- `TASKS.md`
- `agents/AGENT_GUIDE.md`
- `agents/phase_*/INSTRUCTIONS.md`
- `agents/phase_*/STATUS.md`
- `REPO_STRUCTURE.md`
- PRD in `docs/` (master + per fase)

---

## Esito sintetico
La base è **prevalentemente complementare**, ma contiene una **ridondanza significativa di livello operativo** (soprattutto task, dipendenze, test e stato).

In pratica:
- **Complementare**: PRD (il “perché/cosa”) vs task operative (il “come/quando”).
- **Ridondante**: task e regole replicate in più punti (`TASKS.md`, `INSTRUCTIONS.md`, `STATUS.md`, `AGENT_GUIDE.md`).

---

## Dove è complementare (bene)

1. **PRD vs TASKS**
   - I PRD definiscono obiettivi, scope e funzionalità.
   - `TASKS.md` traduce in backlog eseguibile con dipendenze.

2. **REPO_STRUCTURE vs TASKS**
   - `REPO_STRUCTURE.md` dice *dove* vivono i moduli.
   - `TASKS.md` dice *quali attività* fare su quei moduli.

3. **AGENT_GUIDE come governance**
   - Definisce protocollo, regole test, formato status/gap, convenzioni commit.
   - È utile come “manuale operativo trasversale”.

---

## Dove è ridondante (da snellire)

1. **Duplicazione task tra `TASKS.md` e `agents/phase_*/INSTRUCTIONS.md`**
   - Stessi task ID e stessi file target ripetuti in due luoghi.
   - Alto rischio di divergenza nel tempo.

2. **Duplicazione regole test tra `AGENT_GUIDE.md` e `INSTRUCTIONS.md`**
   - Comandi di verifica ripetuti (talvolta con varianti).
   - Se si aggiorna una suite test, bisogna inseguire più file.

3. **Stato distribuito in `STATUS.md` + note in altri file**
   - La fonte dello stato non è chiaramente unica.
   - Alcuni stati “DONE” convivono con fase globale “TODO”, creando ambiguità.

4. **Dipendenze e gating fase replicate**
   - Ordine fasi presente in più documenti.
   - Logica di blocco può diventare incoerente.

---

## Valutazione finale
- **Architettura documentale attuale**: valida ma “verbosa” e soggetta a drift.
- **Problema principale**: non è la quantità di documenti, ma la duplicazione di informazioni “vive” (task, stato, test).

---

## Proposta: struttura unica “Task-first”, estendibile con agenti

### Principio
Avere una **fonte unica delle task** e usare i documenti agenti solo come **overlay operativo** (non come copia del backlog).

### Struttura proposta

1. **`docs/tasks/master.yaml` (Single Source of Truth)**
   - Contiene per ogni task:
     - `id`, `phase`, `title`, `description`
     - `inputs`, `outputs`, `dependencies`
     - `owner_role` (SETUP/BACKEND/DB/...)
     - `acceptance_checks` (comandi test/lint)
     - `status` (todo/wip/done/blocked/review)
     - `updated_at`, `updated_by`

2. **`TASKS.md` auto-generato dal master**
   - Solo vista leggibile del backlog.
   - Nessuna modifica manuale alle task.

3. **`agents/AGENT_GUIDE.md` solo regole globali**
   - Protocollo, policy commit, policy testing, escalation gap.
   - Nessun elenco task duplicato.

4. **`agents/phase_X/INSTRUCTIONS.md` come “playbook fase”**
   - Contenuti consentiti:
     - contesto fase
     - rischi tipici
     - checklist qualitativa
     - link ai task del master (ID)
   - Contenuti NON consentiti:
     - riscrivere task complete
     - riscrivere comandi test ufficiali già nel master

5. **`agents/phase_X/STATUS.md` opzionale o derivato**
   - Opzione A (consigliata): deprecato, stato letto dal master.
   - Opzione B: mantenuto come snapshot generato automaticamente.

6. **`agents/phase_X/GAPS_RISKS.md` resta manuale**
   - Documento vivo utile e non ridondante.

---

## Regole anti-ridondanza consigliate

1. **Una sola fonte per tipo dato**
   - Task/stato/test ufficiali: solo `master.yaml`.
   - Governance: solo `AGENT_GUIDE.md`.
   - Requisiti prodotto: solo PRD.

2. **Campi obbligatori task**
   - `depends_on`, `definition_of_done`, `checks`.
   - Evita ambiguità su “quando è davvero done”.

3. **Aggiornamento stato per transizione**
   - `todo -> wip -> done/review/blocked`.
   - Ogni transizione richiede timestamp e agente.

4. **Rendering automatico documenti umani**
   - Script (`scripts/render_tasks_docs.py`) genera:
     - `TASKS.md`
     - eventuali `STATUS.md` di fase

---

## Piano di migrazione pragmatico

### Step 1 (basso rischio)
- Introdurre `docs/tasks/master.yaml` con tutte le task correnti.
- Aggiungere script di rendering.
- Congelare modifiche manuali a `TASKS.md`.

### Step 2
- Snellire `phase_*/INSTRUCTIONS.md` rimuovendo task duplicate.
- Mantenere solo linee guida e riferimenti a task ID.

### Step 3
- Rendere `STATUS.md` derivato automatico o eliminarlo.
- Usare il master come unico stato ufficiale.

### Step 4
- Integrare check CI:
  - fail se `TASKS.md` non allineato a `master.yaml`
  - fail se task marked `done` senza `acceptance_checks` passate

---

## Benefici attesi
- Meno drift documentale.
- Migliore handoff tra agenti.
- Stato progetto più affidabile.
- Onboarding più rapido (meno file da sincronizzare mentalmente).

---

## Template minimo task (esempio)

```yaml
- id: F1-06
  phase: F1
  title: Trade Engine: gestione stato posizione
  owner_role: BACKEND
  description: >
    Implementare process_event con logica OPEN/ADD/REDUCE/CLOSE/SL_HIT/TP_HIT.
  inputs:
    - src/events/models.py
    - src/db/models.py
  outputs:
    - src/trade_engine/engine.py
    - src/trade_engine/position.py
  dependencies: [F1-01, F1-05]
  acceptance_checks:
    - PYTHONPATH=. pytest tests/unit/test_trade_engine.py -v --tb=short
    - PYTHONPATH=. ruff check src/trade_engine/
  definition_of_done:
    - test unitari verdi
    - stato posizione persistito correttamente
  status: todo
  updated_at: 2026-04-02
  updated_by: null
```

---



## Addendum operativo: prompt unico già pronto

Per rendere la proposta immediatamente eseguibile, è stato aggiunto anche un prompt unificato in:
- `agents/UNIFIED_AGENT_PROMPT.md`

Il file include:
- prompt completo da incollare in un agente;
- algoritmo operativo step-by-step;
- condizioni di gate per fase;
- formato output standard;
- versione breve del prompt per contesti con poco spazio token.

## Conclusione
Le informazioni oggi sono in parte complementari ma hanno ridondanza operativa non banale. La proposta migliore è una **struttura unica task-first** con backlog/stato/check centralizzati e documenti agenti ridotti a governance + playbook.

---

## Implementazione eseguita (2026-04-02)

Per applicare la proposta sono stati effettuati questi passi concreti:
- introdotto `docs/tasks/master.yaml` come fonte unica task/stato/dipendenze/check;
- trasformato `TASKS.md` in vista sintetica derivata;
- semplificato `agents/AGENT_GUIDE.md` come governance (senza backlog duplicato);
- mantenuto `agents/UNIFIED_AGENT_PROMPT.md` come istruzione operativa unica;
- rimossi i file `agents/phase_*/INSTRUCTIONS.md` per eliminare duplicazione operativa.
