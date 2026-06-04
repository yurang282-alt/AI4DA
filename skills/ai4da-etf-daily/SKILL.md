---
name: ai4da-etf-daily
description: Daily ETF tracking, Feishu recording, and next-trading-day decision workflow for AI4DA. Use when the user sends Guangfa Yitaojin ETF watchlist screenshots, holding screenshots, OCR text, Feishu Base records, ETF price/holding data, or asks to import daily ETF data, analyze the 11 watched ETFs, enforce max-5-holdings discipline, and produce executable ETF operation advice with trigger prices, quantities, cash limits, and risk notes.
---

# AI4DA ETF Daily

## Purpose

Execute the user's daily ETF workflow: extract data, normalize ETF identities, validate account rules, write daily records to Feishu when available, then produce a concise next-trading-day operation plan. Keep the final trade decision with the user; never claim guaranteed returns or execute trades.

## Hard Rules

- Watched universe: 11 ETFs listed in `references/etf-universe.md`.
- Holding limit: no more than 5 ETF holdings. New buys must be replacements when already at the limit.
- Current cash rule: cash is `总资产 - 持仓市值`, not `可用` or `可取`, unless the user changes this rule.
- Holding screenshots often lack ETF codes. Infer codes from aliases, but stop before writing if the match is uncertain.
- Advice must be conditional and executable: code, price trigger, action, quantity, and reason.
- This is decision support only. Do not execute trades.

## Daily Workflow

1. Determine the trading date.
   - If screenshots are after the close, use that calendar trading date.
   - If the user asks in the morning, treat advice as for the current trading day and cite exact dates.

2. Extract and normalize data.
   - Price screenshot: extract 11 ETF rows: code, name, close/latest price, daily percentage change.
   - Holding screenshot: extract total assets, daily P/L, available cash, withdrawable cash, holding market value, holding P/L, account position percentage, and each holding's name, market value, P/L, P/L %, position %, holding quantity, available quantity.
   - The holding screenshot often lacks ETF codes; infer from aliases in `references/etf-universe.md`.
   - For the generic extraction pattern, follow `screenshot-to-table-ingestion` if available.

3. Validate before writing.
   - Read `references/validation-rules.md`.
   - Check expected ETF count, current holding count, account totals, cash rule, and duplicate same-date write risk.
   - Show or describe suspicious values before writing.

4. Write to Feishu when available.
   - Read `references/feishu-schema.md`.
   - Prefer `lark-cli` user identity if available and authorized.
   - If writing cannot be done, output the exact records to write and explain what permission/tool is missing.
   - For the generic Feishu pattern, follow `feishu-bitable-app-backend` if available.

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

## Final Daily Response Shape

```text
今日数据状态：
已写入：
组合核心判断：
明日操作优先级：
触发价表：
不操作条件：
风险提醒：
```

## References

- ETF universe and aliases: `references/etf-universe.md`
- Feishu Base schema and write records: `references/feishu-schema.md`
- Data checks and account-cash rules: `references/validation-rules.md`
- Operation advice structure: `references/operation-template.md`
