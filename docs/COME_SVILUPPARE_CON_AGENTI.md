# Come sviluppare il progetto con agenti e team umano

Questa guida risponde alla domanda pratica: **"adesso come procedo nello sviluppo con agenti e persone?"**

## 1) Ruoli consigliati

- **Product Owner (persona):** definisce priorità e accetta output.
- **Tech Lead (persona):** valida scelte architetturali e sblocca dipendenze.
- **Agente Executor:** implementa una task alla volta seguendo prompt unificato.
- **Agente QA (opzionale):** verifica test/check e qualità PR.

## 2) Fonte unica da usare sempre

1. `docs/tasks/master.yaml` → backlog, stato, dipendenze, check.
2. `agents/UNIFIED_AGENT_PROMPT.md` → prompt operativo agente.
3. `agents/AGENT_GUIDE.md` → governance di lavoro.
4. `TASKS.md` → sola vista sintetica (lettura rapida).

## 3) Flusso operativo giornaliero (semplice)

### Step A — Pianificazione (umano)
- Scegliere massimo 1–3 task candidabili (dipendenze soddisfatte).
- Assegnare owner (`owner_role`) e priorità.

### Step B — Esecuzione (agente)
- Lanciare l'agente con prompt unificato.
- L'agente legge i documenti obbligatori.
- Esegue **una sola task** e produce output strutturato.

### Step C — Revisione (umano + QA)
- Verificare evidenza check.
- Validare che lo scope sia rispettato.
- Se OK: merge; altrimenti feedback puntuale e ripetizione ciclo.

## 4) Prompt pratico da dare all'agente

Usare direttamente il contenuto di `agents/UNIFIED_AGENT_PROMPT.md`.

Versione super-breve:

```text
Leggi docs/tasks/master.yaml, AGENT_GUIDE e PRD fase.
Seleziona una sola task con dipendenze soddisfatte.
Metti task in wip, implementa, esegui acceptance checks.
Se i check passano: done. Se falliscono: blocked/review con motivazione.
Restituisci: task scelta, file letti, modifiche, check con esito, stato finale, prossima task.
```

## 5) Regole pratiche per lavorare bene con "la gente"

- Evitare richieste vaghe: dare sempre task ID (es. `F2-03`).
- Chiedere output verificabile (comandi + esiti).
- Mantenere cicli brevi (task piccole, PR piccole).
- Blocchi/ambiguità sempre in `GAPS_RISKS.md`.
- Nessuna task `done` senza check espliciti.

## 6) Esempio concreto (oggi)

1. Product Owner seleziona `F2-03` da `master.yaml`.
2. Passa all'agente il prompt unificato + obiettivo "integrare metriche nel pipeline".
3. L'agente implementa e allega check.
4. Tech Lead valida e decide merge.
5. Aggiornare stato task e rigenerare `TASKS.md`.

## 7) Checklist di avvio rapido

- [ ] `docs/tasks/master.yaml` aggiornato
- [ ] task candidate con dipendenze OK
- [ ] prompt unificato usato
- [ ] check eseguiti e allegati
- [ ] stato task aggiornato (`wip/done/blocked`)
- [ ] `TASKS.md` rigenerato (`python scripts/render_tasks_docs.py`)

---

Se vuoi, nel prossimo step posso anche prepararti un **template operativo per ticket Jira/Linear** già allineato a questo flusso.
