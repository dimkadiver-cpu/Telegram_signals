# STATUS – Fase 4: Web UI

**Stato fase:** ⏳ TODO (attende Fase 3)
**Agente:** —
**Ultimo aggiornamento:** —

---

## Avanzamento task

| Task ID | Titolo                        | Stato   | Agente | Data | Note |
|---------|-------------------------------|---------|--------|------|------|
| F4-01   | Setup FastAPI                 | ⏳ TODO | —      | — | Da aggiungere deps + creare src/api/ |
| F4-02   | API REST traders e trades     | ⏳ TODO | —      | — | |
| F4-03   | API REST template management  | ⏳ TODO | —      | — | Dipende da F3-03 TemplateStore |
| F4-04   | Dashboard frontend            | ⏳ TODO | —      | — | Jinja2 + HTMX |
| F4-05   | Test API                      | ⏳ TODO | —      | — | TestClient FastAPI |

---

## Risultati test

| Suite                      | Ultimo risultato | Data | Agente |
|---------------------------|-----------------|------|--------|
| `tests/unit/test_api`     | ⏳ da creare    | —    | —      |
| `tests/e2e/`              | ⏳ da eseguire  | —    | —      |

---

## Checklist chiusura fase

- [ ] Fase 3 completata
- [ ] `GET /health` → 200
- [ ] CRUD traders via API funzionante
- [ ] Template preview via API funzionante
- [ ] Dashboard HTML accessibile
- [ ] `pytest tests/unit/test_api.py -v` — 100% pass
- [ ] `pytest tests/e2e/ -v` — pass (suite completa)
- [ ] GAPS_RISKS.md aggiornato
- [ ] `ruff check src/api/` — zero errori

---

## Note agente

<!-- Aggiungere note operative qui -->
