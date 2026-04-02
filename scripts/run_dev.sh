#!/usr/bin/env bash
set -e

echo "=== Avvio Telegram Signals in modalità dev ==="

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

python src/main.py
