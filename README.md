# AI4DA

本地 ETF 每日跟踪助手。第一版目标是把你每天的截图整理、飞书多维表格更新、联网分析建议自动化，最终交易动作仍由你自己确认执行。

## 当前流程

1. 下午 3 点后上传广发易淘金两张截图：ETF 自选价格、普通账户持仓。
2. 系统识别截图内容，并展示为可编辑表格。
3. 你检查并修正识别结果。
4. 系统把数据写入飞书多维表格：
   - `ETF收盘价`：追加当天 11 只 ETF 收盘价
   - `ETF持仓`：追加当天持仓和现金
5. 系统基于 ETF 数据和联网信息生成第二天操作建议。

## 关注 ETF

当前按 11 只处理：

| 代码 | 名称 |
| --- | --- |
| 162411 | 华宝油气LOF |
| 512890 | 红利低波ETF |
| 513100 | 纳指ETF |
| 510150 | 消费ETF |
| 513050 | 中概互联ETF |
| 512880 | 证券ETF |
| 588200 | 科创芯片ETF |
| 515880 | 通信ETF |
| 516160 | 新能源ETF |
| 518800 | 黄金ETF |
| 159919 | 沪深300ETF |

## 本地运行

```bash
cd ~/AI4DA
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

如需截图自动识别和联网分析，请在项目根目录创建 `.env`：

```bash
OPENAI_API_KEY=你的_API_Key
ETF_EXCEL_PATH=/Users/bytedance/Downloads/ETF 多股跟进0601.xlsx

FEISHU_APP_ID=飞书自建应用_App_ID
FEISHU_APP_SECRET=飞书自建应用_App_Secret
FEISHU_WRITE_MODE=cli
FEISHU_BITABLE_APP_TOKEN=多维表格_app_token
FEISHU_PRICE_TABLE_ID=ETF收盘价表_table_id
FEISHU_HOLDING_TABLE_ID=ETF持仓表_table_id
```

当前推荐使用 `FEISHU_WRITE_MODE=cli`：通过已授权的 `lark-cli` 写入飞书，不需要在项目 `.env` 里保存 `App Secret`。

没有配置 `OPENAI_API_KEY` 时，也可以手动录入/校对表格，再写入飞书。没有配置飞书时，可以先用“预览飞书记录”检查匹配结果。

## 飞书多维表格

建议新建一个多维表格，里面建两个数据表。

`ETF收盘价` 字段：

| 字段名 | 建议类型 |
| --- | --- |
| 日期 | 文本 |
| ETF代码 | 文本 |
| ETF名称 | 文本 |
| 收盘价 | 数字 |
| 涨跌幅% | 数字 |

`ETF持仓` 字段：

| 字段名 | 建议类型 |
| --- | --- |
| 日期 | 文本 |
| ETF代码 | 文本 |
| ETF名称 | 文本 |
| 持有市值 | 数字 |
| 持仓盈亏 | 数字 |
| 盈亏比例% | 数字 |
| 个股仓位% | 数字 |
| 持仓数量 | 数字 |
| 可用数量 | 数字 |
| 现金余额 | 数字 |

现金会作为一条特殊记录写入 `ETF持仓`，其中 `ETF代码` 为 `CASH`，`ETF名称` 为 `现金`。

飞书接入需要一个飞书开放平台自建应用，并给它开通多维表格记录写入权限。如果已经安装并授权 `lark-cli`，本项目会优先使用 CLI 的用户身份写入记录。

## 持仓截图没有 ETF 代码怎么办

第一版会用名称别名自动匹配代码，例如：

- `中概互联网E...` -> `513050`
- `科创芯片ET...` -> `588200`
- `证券ETF国泰` -> `512880`

如果后续发现某个名称识别不稳，可以继续在 `etf_config.py` 里补别名。
