# ETF Universe

The watched universe currently has 11 ETFs.

| Code | Canonical name | Common screenshot aliases |
| --- | --- | --- |
| 162411 | 华宝油气LOF | 华宝油气, 华宝油气LOF, 油气LOF |
| 512890 | 红利低波ETF | 红利低波, 红利低波ETF, 红利低波ETF华泰柏瑞, 华泰柏瑞红利低波 |
| 513100 | 纳指ETF | 纳指ETF, 纳指ETF国泰, 纳指 |
| 510150 | 消费ETF | 消费ETF, 消费ETF招商, 消费 |
| 513050 | 中概互联ETF | 中概互联, 中概互联网, 中概互联网ETF, 中概互联网E..., 中概互联网ETF易方达 |
| 512880 | 证券ETF | 证券ETF, 证券ETF国泰, 证券 |
| 588200 | 科创芯片ETF | 科创芯片, 科创芯片ETF, 科创芯片ET..., 科创芯片ETF嘉实 |
| 515880 | 通信ETF | 通信ETF, 通信ETF国泰, 通信 |
| 516160 | 新能源ETF | 新能源ETF, 新能源ETF南方, 新能源 |
| 518800 | 黄金ETF | 黄金ETF, 黄金ETF国泰, 黄金 |
| 159919 | 沪深300ETF | 沪深300, 沪深300ETF, 沪深300ETF嘉实 |

Historical holdings may include ETFs outside the current universe, such as `512010 医药ETF`. Preserve historical records when importing archives, but do not include non-universe ETFs in daily watchlist analysis unless they are currently held.

## Matching Rules

- Prefer exact code when visible.
- If code is absent, normalize the name by removing spaces, ellipses, and manager suffixes such as 国泰、嘉实、招商、南方、易方达、华泰柏瑞.
- Map truncated holding names using aliases, for example `中概互联网E...` -> `513050`, `科创芯片ET...` -> `588200`.
- If a holding cannot be matched confidently, stop before writing and ask for confirmation.
