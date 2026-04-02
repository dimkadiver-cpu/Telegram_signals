# PRD Fase 2 – Metriche

## Feature
- risk %
- risk USD
- RR
- delta exposure

## Config
- capitale fisso
- rischio configurabile

## Formule applicate (MVP)
- `delta_exposure = size * current_price`
- `effective_leverage = delta_exposure / capital_usd` (se `capital_usd` disponibile)
- distanza avversa (`adverse_distance`):
  - LONG: `avg_entry - stop_loss`
  - SHORT: `stop_loss - avg_entry`
- distanza favorevole (`favorable_distance`):
  - LONG: `take_profit - avg_entry`
  - SHORT: `avg_entry - take_profit`
- `risk_pct = (adverse_distance / avg_entry) * 100` solo se `adverse_distance > 0`
- `risk_usd = (risk_pct / 100) * capital_usd`
- `rr = favorable_distance / adverse_distance` solo se entrambe positive

## Regole edge-case
- Se `stop_loss` manca, `risk_pct`, `risk_usd`, `rr` restano `None`.
- Se `stop_loss` è presente ma non avverso rispetto al lato trade, rischio non calcolato (`None`).
- Se `take_profit` manca, `rr` resta `None` ma rischio viene calcolato se SL valido.
- I template devono nascondere metriche non disponibili (no render di valori `None`).
