#!/usr/bin/env bash
set -e

echo "=== Telegram Signals – Setup ==="

# 1. Crea .env da .env.example se non esiste
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[OK] .env creato da .env.example – aggiorna le variabili prima di avviare."
else
    echo "[SKIP] .env già presente."
fi

# 2. Installa dipendenze
if command -v pip &> /dev/null; then
    pip install -e ".[dev]"
else
    echo "[WARN] pip non trovato. Installa manualmente: pip install -e '.[dev]'"
fi

# 3. Esegui migrations DB
echo "Creazione tabelle DB..."
python -c "
import asyncio
from src.db.session import init_db, create_tables
from src.config import Settings
s = Settings()
init_db(s.database_url)
asyncio.run(create_tables())
print('[OK] Tabelle create.')
"

echo "=== Setup completato ==="
