# PRD MASTER – Sistema di Signalizzazione Trading Manuale (Detailed)

## Visione
Sistema che trasforma trading manuale in eventi strutturati, stato coerente e messaggi controllati.

## Architettura
Exchange → Normalizer → Trade Engine → Metric Engine → Template → Telegram → Dispatch

## Stack
- CCXT
- SDK exchange
- aiogram
- Jinja
- SQLModel

## Principi
- separazione livelli
- multi-trader
- Telegram UI iniziale
