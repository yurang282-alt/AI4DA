# Validation Rules

## Required Daily Inputs

Price screenshot/OCR should provide 11 watchlist rows:

- ETF code or matchable name
- close/latest price
- daily percentage change

Holding screenshot/OCR should provide:

- total assets
- daily P/L
- available cash
- withdrawable cash
- holding market value
- holding P/L
- account position percentage
- each held ETF's name, market value, P/L, P/L %, position %, holding quantity, available quantity

## Account Cash

- Current user preference: treat cash as `总资产 - 持仓市值`.
- Do not use `可用` or `可取` as the primary cash value unless the user changes this rule again.
- If the screenshot shows both values, record/report both when useful, but base trading cash discipline on `总资产 - 持仓市值`.

## Holding Count Rule

- The user wants to hold no more than 5 ETFs.
- If current holdings are already 5, a new ETF recommendation must be framed as replacement:
  - sell/reduce an existing holding first
  - then buy the new ETF if the buy trigger is met
- Do not suggest adding a sixth ETF as a simple new position.

## Percent Handling

- Store percentages as numeric percent values, not decimals: `-23.45`, not `-0.2345`.
- For imported Excel history, if values are decimals between -1 and 1, multiply by 100 for Feishu display consistency.

## Safety Checks Before Advice

- Highlight the largest holding and largest loss holding.
- Check whether one theme dominates the portfolio, especially 科创芯片、通信、纳指、中概.
- Check whether a proposed buy is chasing a large one-day gain.
- Prefer cash preservation after a large rebound day.
