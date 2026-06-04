from __future__ import annotations

import os
import tempfile
from datetime import date
from pathib import Path

import streamlit as st
from dotenv import load_dotenv

from ai_services import extract_from_screenshots, generate_report, has_api_key
from etf_config import ETF_UNIVERSE
from etf_matching import canonical_name, infer_etf_code
from excel_store import update_workbook
from feishu_store import append_daily_records, build_preview_records, env_ready as feishu_env_ready

load_dotenv()

st.set_page_config(page_title="AI4DRA ETF 助手", page_icon="📊", layout="wide")


def normalize_price_rows(rows: list[dict]) -> list[dict]:
    by_code = {}
    for item in ETF_UNIVERSE:
        by_code[item["code"]] = {
            "code": item["code"],
            "name": item["name"],
            "close": None,
            "change_pct": None,
        }
    for row in rows:
        code = infer_etf_code(row.get("name"), row.get("code"))
        if not code:
            continue
        by_code[code].update(
            {
                "code": code,
                "name": canonical_name(code, row.get("name")),
                "close": row.get("close"),
                "change_pct": row.get("change_pct"),
            }
        )
    return list(by_code.values())


def normalize_holding_rows(rows: list[dict]) -> list[dict]:
    normalized = []
    seen = set()
    for row in rows:
        code = infer_etf_code(row.get("name"), row.get("code"))
        if not code or code in seen:
            continue
        seen.add(code)
        normalized.append(
            {
                "code": code,
                "name": canonical_name(code, row.get("name")),
                "market_value": row.get("market_value"),
                "pnl": row.get("pnl"),
                "pnl_pct": row.get("pnl_pct"),
                "weight": row.get("weight"),
                "quantity": row.get("quantity"),
                "available_quantity": row.get("available_quantity"),
            }
        )
    return normalized


def save_upload(uploaded_file) -> str | None:
    if uploaded_file is None:
        return None
    suffix = Path(uploaded_file.name).suffix or ".png"
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    handle.write(uploaded_file.getbuffer())
    handle.close()
    return handle.name


def reset_editors() -> None:
    st.session_state.editor_version = st.session_state.get("editor_version", 0) + 1


st.title("AI4DA ETF 每日助手")

with st.sidebar:
    st.subheader("配置")
    storage_target = st.selectbox("写入目标", ["飞书多维表格", "Excel 备用"], index=0)
    default_excel = os.getenv("ETF_EXCEL_PATH", "/Users/bytedance/Downloads/ETF 多股跟进0601.xlsx")
    excel_path = st.text_input("Excel 跟踪表路径", default_excel, disabled=storage_target != "Excel 备用")
    report_date = st.date_input("交易日期", value=date.today())
    risk_profile = st.selectbox("风险风格", ["均衡", "保守", "进取"], index=0)
    max_holdings = st.number_input("ETF 持仓上限", min_value=1, max_value=11, value=5, step=1)
    st.caption("配置 OPENAI_API_KEY 后，可自动识别截图并生成联网分析。")
    st.success("API Key 已配置" if has_api_key() else "未检测到 API Key")
    st.success("飞书已配置" if feishu_env_ready() else "飞书未配置")

price_image = st.file_uploader("上传 ETF 自选价格截图", type=["png", "jpg", "jpeg"])
holding_image = st.file_uploader("上传持仓截图", type=["png", "jpg", "jpeg"])

if "prices" not in st.session_state:
    st.session_state.prices = normalize_price_rows([])
if "holdings" not in st.session_state:
    st.session_state.holdings = []
if "cash_balance" not in st.session_state:
    st.session_state.cash_balance = None
if "report" not in st.session_state:
    st.session_state.report = ""
if "editor_version" not in st.session_state:
    st.session_state.editor_version = 0
if "flash_message" in st.session_state:
    level, message = st.session_state.pop("flash_message")
    getattr(st, level)(message)

left, right = st.columns([1, 1])
with left:
    if st.button("识别截图", type="primary", use_container_width=True):
        if not has_api_key():
            st.warning("当前没有配置 OPENAI_API_KEY，无法自动识别截图。可以先在下方表格里手动录入/粘贴数据。")
            st.stop()
        if price_image is None and holding_image is None:
            st.warning("请先上传 ETF 自选价格截图或持仓截图。")
            st.stop()

        price_path = save_upload(price_image)
        holding_path = save_upload(holding_image)
        with st.spinner("正在识别截图..."):
            extracted = extract_from_screenshots(price_path, holding_path)
        st.session_state.prices = normalize_price_rows(extracted.get("prices", []))
        st.session_state.holdings = normalize_holding_rows(extracted.get("holdings", []))
        st.session_state.cash_balance = extracted.get("cash_balance")
        reset_editors()
        price_count = sum(1 for row in st.session_state.prices if row.get("close") is not None)
        holding_count = len(st.session_state.holdings)
        if price_count == 0 and holding_count == 0 and st.session_state.cash_balance is None:
            st.session_state.flash_message = (
                "warning",
                "截图识别没有提取到有效数据。请检查截图是否清晰，或先手动录入/粘贴数据。",
            )
        else:
            st.session_state.flash_message = (
                "success",
                f"识别完成：收盘价 {price_count} 条，持仓 {holding_count} 条。请检查并修正下方表格。",
            )
        st.rerun()

with right:
    if st.button("重置为空表", use_container_width=True):
        st.session_state.prices = normalize_price_rows([])
        st.session_state.holdings = []
        st.session_state.cash_balance = None
        st.session_state.report = ""
        reset_editors()
        st.rerun()

st.subheader("收盘价确认")
price_rows = st.data_editor(
    st.session_state.prices,
    num_rows="fixed",
    use_container_width=True,
    column_config={
        "code": "代码",
        "name": "名称",
        "close": st.column_config.NumberColumn("收盘价", format="%.3f"),
        "change_pct": st.column_config.NumberColumn("涨跌�i%", format="%.2f"),
    },
    key=f"price_editor_{st.session_state.editor_version}",
)

st.subheader("持仓确认")
holding_rows = st.data_editor(
    st.session_state.holdings,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "code": "代码",
        "name": "名称",
        "market_value": st.column_config.NumberColumn("持有市值", format="%.2f"),
        "pnl": st.column_config.NumberColumn("持仓盈亏", format="%.2f"),
        "pnl_pct": st.column_config.NumberColumn("盈亏比例%", format="%.2f"),
        "weight": st.column_config.NumberColumn("个股仓位%", format="%.2f"),
        "quantity": st.column_config.NumberColumn("持仓数量", format="%.0f"),
        "available_quantity": st.column_config.NumberColumn("可用数量", format="%.0f"),
    },
    key=f"holding_editor_{st.session_state.editor_version}",
)
cash_balance = st.number_input(
    "现金余额",
    value=float(st.session_state.cash_balance or 0),
    min_value=0.0,
    step=1000.0,
    format="%.2f",
)

st.subheader("写�i")
write_cols = st.columns(3)
with write_cols[0]:
    if st.button("预览飞书记录", use_container_width=True):
        preview = build_preview_records(report_date, price_rows, holding_rows, cash_balance)
        st.session_state.feishu_preview = preview
        st.success(f"已生成预览：收盘价 {len(preview['prices'])} 条，持仓/现金 {len(preview['holdings'])} 条。")

with write_cols[1]:
    if st.button("写入飞书", type="primary", use_container_width=True):
        try:
            result = append_daily_records(report_date, price_rows, holding_rows, cash_balance)
            st.success(f"写入完成：收盘价 {result['prices']} 条，持仓/现金 {result['holdings']} 条。")
        except Exception as exc:
            st.error(f"写入飞书失败：{exc}")

with write_cols[2]:
    if st.button("写�i Excel 备用", use_container_width=True):
        source = Path(excel_path).expanduser()
        output = Path("outputs") / f"ETF多股跟进_{report_date.strftime('%Y%m%d')}.xlsx"
        try:
            saved = update_workbook(source, output, report_date, price_rows, holding_rows, cash_balance)
            st.success(f"已生成更新后的 Excel：{saved.resolve()}")
        except Exception as exc:
            st.error(f"写入失败：{exc}")

if "feishu_preview" in st.session_state:
    with st.expander("飞书写入预览", expanded=False):
        st.write("收盘价表")
        st.dataframe(st.session_state.feishu_preview["prices"], use_container_width=True)
        st.write("持仓表")
        st.dataframe(st.session_state.feishu_preview["holdings"], use_container_width=True)

if st.button("生成联网分析报告", use_container_width=True):
    with st.spinner("正在生成分析报告..."):
        st.session_state.report = generate_report(
            report_date.isoformat(),
            price_rows,
            holding_rows,
            cash_balance,
            risk_profile=risk_profile,
            max_holdings=int(max_holdings),
        )

if st.session_state.report:
    st.subheader("明日操作建议")
    st.markdown(st.session_state.report)
