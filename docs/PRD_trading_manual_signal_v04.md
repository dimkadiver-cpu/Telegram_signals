# PRD – Sistema di Signalizzazione Trading Manuale (v0.4)

## 1. Obiettivo
Sistema che intercetta operazioni manuali e le trasforma in:
- eventi strutturati
- stato posizione
- bozze Telegram
- messaggi finali

## 2. Architettura Tecnologica (STACK)

### Scelte confermate MVP

| Modulo | Libreria | Ruolo |
|-------|--------|------|
| Exchange REST | CCXT | multi-exchange, market data |
| Exchange Events | SDK ufficiale (es. Binance) | ordini, fill, eventi account |
| Telegram | aiogram | review, approvazione, invio |
| Template | Jinja | rendering messaggi |
| DB | SQLModel / SQLAlchemy | persistenza |
| Async | asyncio | orchestrazione |

## 3. Architettura Logica

Exchange Listener  
→ Event Normalizer  
→ Trade Engine  
→ Metric Engine  
→ Template Engine  
→ Telegram Review  
→ Dispatcher  

## 4. Telegram Workflow
- bozza inviata automaticamente
- trader può:
  - modificare
  - approvare
  - cancellare
  - aggiungere note

## 5. Template System
- personalizzabile per trader
- supporto placeholder canonici
- supporto metriche

## 6. Metric Engine
Calcola:
- rischio %
- rischio USD
- RR
- delta exposure
- leva effettiva

## 7. Multi-Trader
- isolamento completo per:
  - eventi
  - template
  - metriche
  - canali Telegram

## 8. Decisioni Chiave
- Telegram come UI iniziale
- Template configurabili
- Metriche integrate
- CCXT + SDK ufficiale insieme

## 9. Roadmap
Fase 1:
- 1 exchange (Binance)
- Telegram review
- template base

Fase 2:
- metriche avanzate
- multi-trader completo

Fase 3:
- UI web
- AI support

