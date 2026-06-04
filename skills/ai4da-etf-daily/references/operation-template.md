# Operation Advice Template

Use this structure for daily advice. Keep it executable and short enough for morning trading.

## Opening

Start with:

```text
今日主基调：<one-line strategy>
```

Then summarize:

```text
总资产：
可用现金：
持仓市值：
当前仓位：
当前持仓数量：
```

## Operation Principles

List 4-6 rules, for example:

```text
1. 不新增第6只ETF
2. 不追高昨日大涨方向
3. 第一大仓只在触发价处理
4. 新建防守仓必须来自弱仓替换
5. 可用现金至少保留 X 元
```

## Execution Table

Use a table with exact triggers:

| 顺序 | 标的 | 触发条件 | 操作 | 数量 |
| ---: | --- | ---: | --- | ---: |
| 1 | 科创芯片ETF 588200 | 3.52-3.60 | 卖出 | 3,000份 |

Only include trades that are actionable. Use `不操作` when no trigger is met.

## Scenario Handling

Add three short scenarios:

```text
如果科技线高开：...
如果科技线低开：...
如果市场平开震荡：...
```

## Replacement Logic

If the user already holds 5 ETFs, write buy advice as replacement:

```text
卖出证券ETF成功 -> 才考虑买红利低波
```

## Cash Discipline

Base cash limits on deployable cash:

```text
可用现金：
不减仓时新增买入上限：
减仓成功后新增买入上限：
最低保留可用现金：
```

## Closing

End with:

```text
最简操作版：
1. ...
2. ...
3. ...
```

Then include a concise risk reminder:

```text
以上是盘前决策辅助，不是收益承诺；最终交易由用户确认执行。
```
