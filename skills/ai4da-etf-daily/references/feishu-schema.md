# Feishu Base Schema

Current AI4DA Base is configured through environment variables:

- Base token: `FEISHU_BITABLE_APP_TOKEN`
- `ETF收盘价` table: `FEISHU_PRICE_TABLE_ID`
- `ETF持仓` table: `FEISHU_HOLDING_TABLE_ID`

Prefer `lark-cli` user identity for writes:

```bash
lark-cli auth status --verify
```

## ETF收盘价

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| ETF代码 | text | Primary identifier |
| 日期 | text | ISO date, e.g. `2026-06-02` |
| ETF名称 | text | Canonical name |
| 收盘价 | number | Use the close/latest value shown after close |
| 涨跌幅% | number | Numeric percent, e.g. `5.81` |

CLI batch-create shape:

```json
{
  "fields": ["ETF代码", "日期", "ETF名称", "收盘价", "涨跌幅%"],
  "rows": [["513050", "2026-06-02", "中概互联ETF", 1.183, 5.81]]
}
```

## ETF持仓

Fields:

| Field | Type | Notes |
| --- | --- | --- |
| ETF代码 | text | Use `CASH` for cash row |
| 日期 | text | ISO date |
| ETF名称 | text | Canonical name, or `现金` |
| 持有市值 | number | Holding market value |
| 持仓盈亏 | number | Total holding P/L |
| 盈亏比例% | number | Numeric percent, e.g. `-23.45` |
| 个股仓位% | number | Numeric percent, e.g. `15.2` |
| 持仓数量 | number | Total quantity |
| 可用数量 | number | Available quantity |
| 现金余额 | number | Only for the `CASH` row |

CLI batch-create shape:

```json
{
  "fields": ["ETF代码", "日期", "ETF名称", "持有市值", "持仓盈亏", "盈亏比例%", "个股仓位%", "持仓数量", "可用数量", "现金余额"],
  "rows": [
    ["588200", "2026-06-02", "科创芯片ETF", 94393, 1145.6, 1.23, 22.9, 27400, 22400, null],
    ["CASH", "2026-06-02", "现金", null, null, null, null, null, null, 78319.31]
  ]
}
```

## Write Discipline

- Preview records before writing if there is any uncertainty.
- Do not write duplicate same-date records unless the user asks for a correction or append.
- If correcting same-date data, prefer explicit update/delete behavior rather than silent duplicate insert.
- After writing, read back a few records and report counts.
