# Sistema di Signalizzazione Trading Manuale – Concetto (v0.4)

## Idea
Sistema che trasforma il trading manuale in:
→ eventi
→ stato
→ messaggi controllati

## Interfaccia
Telegram è la UI principale:
- ricevi bozza
- modifichi
- invii

## Tecnologia
- CCXT per base exchange
- SDK ufficiale per eventi reali
- aiogram per Telegram
- Jinja per template

## Flusso
Trader → Exchange → Server → Eventi → Metriche → Template → Telegram → Invio

## Template
Ogni trader può:
- usare emoji
- cambiare layout
- mostrare metriche
- definire stile

## Metriche
- rischio %
- rischio fisso
- delta
- leva
- RR

## Multi-trader
Sistema unico, più utenti separati

## Scopo
- meno lavoro manuale
- segnali coerenti
- storico pulito
- base per automazione futura

