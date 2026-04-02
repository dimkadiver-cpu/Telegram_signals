# GAPS & RISKS – Fase 0: Setup

> Aggiornare questo file ogni volta che si trova un problema, un'assunzione non verificata o una decisione pendente.

---

## Template entry

```
## [DATA] [TASK_ID] Titolo

**Tipo:** Gap / Rischio / Errore / Decisione pendente
**Severità:** Alta / Media / Bassa
**Descrizione:**
**Impatto:**
**Proposta:**
**Stato:** Aperto / Risolto / Accettato
```

---

## Gap e Rischi noti

---

### [2026-04-02] [F0-03] Versione Python e setuptools

**Tipo:** Rischio
**Severità:** Media
**Descrizione:** Il `build-backend` originale usava `setuptools.backends.legacy:build` che richiede setuptools >= 64 con la nuova API. Il sistema potrebbe avere una versione precedente.
**Impatto:** `pip install -e .[dev]` fallisce senza aggiornare setuptools.
**Proposta:** Usare `setuptools.build_meta` (già corretto in pyproject.toml) oppure aggiungere `pip install --upgrade setuptools` nello script di setup.
**Stato:** Risolto — build-backend corretto in pyproject.toml

---

### [2026-04-02] [F0-03] Driver DB asyncpg richiede PostgreSQL client

**Tipo:** Gap
**Severità:** Bassa (solo prod)
**Descrizione:** `asyncpg` richiede `libpq-dev` sul sistema. In dev si usa aiosqlite ma in produzione con PostgreSQL potrebbe fallire l'install.
**Impatto:** Deploy su container minimal potrebbe fallire.
**Proposta:** Aggiungere al Dockerfile: `apt-get install -y libpq-dev` prima di `pip install`.
**Stato:** Aperto

---

### [2026-04-02] [F0-01] Alembic non ancora configurato

**Tipo:** Gap
**Severità:** Media
**Descrizione:** `src/db/migrations/env.py` è uno skeleton. Le migration Alembic non sono operative. Attualmente si usa `create_all()` direttamente.
**Impatto:** In produzione non si possono fare migrazioni incrementali senza perdere dati.
**Proposta:** Configurare Alembic completo in Fase 1 o Fase 3 (quando lo schema si stabilizza).
**Stato:** Aperto — accettato per MVP, da risolvere prima di Fase 3

---

### [2026-04-02] [F0-02] .env non presente in produzione

**Tipo:** Rischio
**Severità:** Alta
**Descrizione:** Se `.env` non esiste e le variabili d'ambiente non sono impostate, `Settings()` userà valori vuoti (es. `binance_api_key=""`) che causeranno errori runtime silenti.
**Impatto:** Il bot parte senza credenziali valide.
**Proposta:** Aggiungere validazione esplicita dei campi obbligatori in `Settings` con `@validator`.
**Stato:** Aperto
