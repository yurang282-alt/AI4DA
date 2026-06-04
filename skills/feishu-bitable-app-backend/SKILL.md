---
name: feishu-bitable-app-backend
description: Use Feishu/Lark Bitable as the online data backend for a lightweight app. Use when the user wants to replace Excel with Feishu Base, create or operate Bitable tables, design schemas, write records through lark-cli, MCP, or API, import spreadsheet history, preview records, avoid duplicates, and keep Feishu credentials safe.
---

# Feishu Bitable App Backend

## Purpose

Use Feishu Bitable as a practical early-stage backend for personal or team workflow apps. Treat it as a database with a human-editable UI, not as a casual spreadsheet dump.

## Design Rules

- Design the schema before writing code.
- Use one table per stable record type, not one giant mixed table.
- Keep field names user-readable and stable.
- Store ids/tokens in environment variables or approved secret storage.
- Never commit `.env`, app secrets, Base tokens, table ids, or user auth tokens.
- Write preview records before mutating the table when there is uncertainty.

## Workflow

1. Identify record types.
   - Examples: daily price, holding snapshot, task, contact, log entry, analysis result.
   - Decide each table's primary key and duplicate rule.

2. Create or inspect tables.
   - Confirm Base token and table ids.
   - Confirm fields, types, and required columns.
   - Rename blank/default tables before using them in production.

3. Choose the write path.
   - Prefer `lark-cli` user identity when the user has already authorized it and wants local workflow automation.
   - Use MCP/app connector when available and authorized.
   - Use API app credentials only when a server/app needs unattended writes.

4. Configure safely.
   - Put values such as `FEISHU_BITABLE_APP_TOKEN`, table ids, and write mode in `.env`.
   - Keep `.env.example` with placeholders only.
   - Add `.env` to `.gitignore`.

5. Build records.
   - Convert app field names to Feishu field names explicitly.
   - Normalize numbers, dates, and percentages before writing.
   - Include a special row or separate table for summary/cash/account-level records when needed.

6. Preview and write.
   - Show the exact fields and rows to be written.
   - Batch writes where the tool supports it.
   - Report the number of rows written per table.

7. Verify.
   - Read back sample records when possible.
   - Confirm counts and dates.
   - If a same-date correction is needed, prefer explicit update/delete logic over silent duplicate append.

## CLI Pattern

Use `lark-cli auth status --verify` to check user auth when the CLI path is selected.

For batch writes, build a payload like:

```json
{
  "fields": ["日期", "名称", "数值"],
  "rows": [["2026-06-04", "示例", 123.45]]
}
```

Then write through the user's authorized CLI or connector. If the tool is unavailable, output the exact rows and the missing setup step.

## Failure Handling

- Permission error: explain whether it is Base access, table access, app scope, or user auth.
- Field mismatch: show missing or unexpected field names.
- Duplicate risk: stop before appending unless the user explicitly wants duplicate history rows.
- Token leakage risk: stop, remove secrets from tracked files, and scan before publishing.

