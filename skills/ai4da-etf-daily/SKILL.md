---
name: ai4da-etf-daily
description: Daily ETF tracking and decision workflow for AI4DA. Use when the user sends Guangfa Yitaojin ETF watchlist screenshots, holding screenshots, OCR text, Feishu Base records, or asks to identify ETF prices/positions, write daily ETF data into Feishu Bitable, analyze 11 watched ETFs, and produce next-trading-day executable ETF operation advice with price triggers, quantities, cash discipline, and max-5-holdings risk control.
---

# AI4DA ETF Daily

## Overview

Execute the user's daily ETF workflow: identify data from two screenshots or pasted OCR text, normalize ETF codes/names, write daily records to Feishu Base when tooling is available, then produce a concise next-day operation plan. Keep the final trade decision with the user; never claim guaranteed returns or execute trades.

## Daily Workflow

1. Determine the trading date.
   - If screenshots are after the close, use that calendar trading date.
   - If the user asks in the morning, treat advice as for the current trading day and cite exact dates.

2. Extract and normalize data.
   - Price screenshot: extract 11 ETF rows: code, name, close/latest price, daily percentage change.
   - Holding screenshot: extract total assets, daily P/L, available cash, withdrawable cash, holding market value, holding P/L, account position percentage, and each holding's name, market value, P/L, P/L %, position %, holding quantity, available quantity.
   - The holding screenshot often lacks ETF codes; infer from aliases in `references/etf-universe.md`.

3. Validate before writing.
   - Read `references/validation-rules.md`.
   - Use the user's current cash rule: cash is `总资产 - 持仓市值`, not `可用` or `可取`, unless the user changes this rule again.
   - Enforce the user's hard rule: no more than 5 ETF holdings. If already holding 5, any new ETF is a replacement, not an addition.

4. Write to Feishu when available.
   - Read `references/feishu-schema.md`.
   - Prefer `lark-cli` user identity if available and authorized.
   - If writing cannot be done, output the exact records to write and explain what permission/tool is missing.

5. Produce the operation plan.
   - Read `references/operation-template.md`.
   - Lead with the actionable conclusion, then give trigger-price tables.
   - Include sell, buy, and do-nothing conditions; quantities should be executable in round lots where practical.
   - Use current web/market information when available. If live market lookup is unavailable, state that limitation and base the plan on the provided data and history.

## Output Rules

- Use Chinese unless the user asks otherwise.
- Be concrete: codes, prices, quantities, cash limits, and trigger conditions.
- Keep recommendations conditional: "if price reaches X, sell Y" rather than vague opinions.
- Prefer "do nothing" when no trigger is hit.
- Do not recommend exceeding 5 ETF holdings.
- Do not recommend chasing a large one-day move unless a clear risk/reward reason exists.
- End with a short risk reminder: this is a decision aid, not automatic trading or return guarantee.

## References

- ETF universe and aliases: `references/etf-universe.md`
- Feishu Base schema and write records: `references/feishu-schema.md`
- Data checks and account-cash rules: `references/validation-rules.md`
- Operation advice structure: `references/operation-template.md`
