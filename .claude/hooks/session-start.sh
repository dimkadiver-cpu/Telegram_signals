#!/bin/bash
set -euo pipefail

# Solo in ambienti remoti (Claude Code on the web)
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

echo "[session-start] Installazione dipendenze Python..."
pip install -e ".[dev]" --quiet

echo "[session-start] Configurazione PYTHONPATH..."
echo 'export PYTHONPATH="${CLAUDE_PROJECT_DIR:-.}"' >> "$CLAUDE_ENV_FILE"

echo "[session-start] Setup completato."
