from __future__ import annotations

import os
import tempfile
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from ai_services import extract_from_screenshots, generate_report, has_api_key
from etf_config import ETF_UNIVERSE
from etf_matching import canonical_name, infer_etf_code
from excel_store import update_workbook
from feishu_store import append_daily_records, build_preview_records, env_ready as feishu_env_ready

load_dotenv()

st.set_page_config(page_title="AI4DA ETF \u52a9\u624b", page_icon="\U0001f4ca", layout="wide")


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


st.title("AI4DA ETF \u6bcf\u65e5\u52a9\u624b")

with st.sidebar:
    st.subheader("\u914d\u7f6e")
    storage_target = st.selectbox("\u5199\u5165\u76ee\u6807", ["\u98de\u4e66\u591a\u7ef4\u8868\u683c", "Excel \u5907\u7528"], index=0)
    default_excel = os.getenv("ETF_EXCEL_PATH", "/Users/bytedance/Downloads/ETF \u591a\u80a1\u8ddf\u8fdb0601.xlsx")
    excel_path = st.text_input("Excel \u8ddf\u8e2a\u8868\u8def\u5f84", default_excel, disabled=storage_target != "Excel \u5907\u7528")
    report_date = st.date_input("\u4ea4\u6613\u65e5\u671f", value=date.today())
    risk_profile = st.selectbox("\u98ce\u9669\u98ce\u683c", ["\u5747\u8861", "\u4fdd\u5b88", "\u8fdb\u53d6"], index=0)
    max_holdings = st.number_input("ETF \u6301\u4ed3\u4e0a\u9650", min_value=1, max_value=11, value=5, step=1)
    st.caption("\u914d\u7f6e OPENAI_API_KEY \u540e\uff0c\u53ef\u81ea\u52a8\u8bc6\u522b\u622a\u56fe\u5e76\u751f\u6210\u8054\u7f51\u5206\u6790\u3002")
    st.success("API Key \u5df2\u914d\u7f6e" if has_api_key() else "\u672a\u68c0\u6d4b\u5230 API Key")
    st.success("\u98de\u4e66\u5df2\u914d\u7f6e" if feishu_env_ready() else "\u98de\u4e66\u672a\u914d\u7f6e")

price_image = st.file_uploader("\u4e0a\u4f20 ETF \u81ea\u9009\u4ef7\u683c\u622a\u56fe", type=["png", "jpg", "jpeg"])
holding_image = st.file_uploader("\u4e0a\u4f20\u6301\u4ed3\u622a\u56fe", type=["png", "jpg", "jpeg"])

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
    if st.button("\u8bc6\u522b\u622a\u56fe", type="primary", use_container_width=True):
        if not has_api_key():
            st.warning("\u5f53\u524d\u6ca1\u6709\u914d\u7f6e OPENAI_API_KEY\uff0c\u65e0\u6cd5\u81ea\u52a8\u8bc6\u522b\u622a\u56fe\u3002\u53ef\u4ee5\u5148\u5728\u4e0b\u65b9\u8868\u683c\u91cc\u624b\u52a8\u5f55\u5165/\u7c98\u8d34\u6570\u636e\u3002")
            st.stop()
        if price_image is None and holding_image is None:
            st.warning("\u8bf7\u5148\u4e0a\u4f20 ETF \u81ea\u9009\u4ef7\u683c\u622a\u56fe\u6216\u6301\u4ed3\u622a\u56fe\u3002")
            st.stop()

        price_path = save_upload(price_image)
        holding_path = save_upload(holding_image)
        with st.spinner("\u6b63\u5728\u8bc6\u522b\u622a\u56fe..."):
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
                "\u622a\u56fe\u8bc6\u522b\u6ca1\u6709\u63d0\u53d6\u5230\u6709\u6548\u6570\u636e\u3002\u8bf7\u68c0\u67e5\u622a\u56fe\u662f\u5426\u6e05\u6670\uff0c\u6216\u5148\u624b\u52a8\u5f55\u5165/\u7c98\u8d34\u6570\u636e\u3002",
            )
        else:
            st.session_state.flash_message = (
                "success",
                f"\u8bc6\u522b\u5b8c\u6210\uff1a\u6536\u76d8\u4ef7 {price_count} \u6761\uff0c\u6301\u4ed3 {holding_count} \u6761\u3002\u8bf7\u68c0\u67e5\u5e76\u4fee\u6b63\u4e0b\u65b9\u8868\u683c\u3002",
            )
        st.rerun()

with right:
    if st.button("\u91cd\u7f6e\u4e3a\u7a7a\u8868", use_container_width=True):
        st.session_state.prices = normalize_price_rows([])
        st.session_state.holdings = []
        st.session_state.cash_balance = None
        st.session_state.report = ""
        reset_editors()
        st.rerun()

st.subheader("\u6536\u76d8\u4ef7\u786e\u8ba4")
price_rows = st.data_editor(
    st.session_state.prices,
    num_rows="fixed",
    use_container_width=True,
    column_config={
        "code": "\u4ee3\u7801",
        "name": "\u540d\u79f0",
        "close": st.column_config.NumberColumn("\u6536\u76d8\u4ef7", format="%.3f"),
        "change_pct": st.column_config.NumberColumn("\u6da8\u8dcc\u5e45%", format="%.2f"),
    },
    key=f"price_editor_{st.session_state.editor_version}",
)

st.subheader("\u6301\u4ed3\u786e\u8ba4")
holding_rows = st.data_editor(
    st.session_state.holdings,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "code": "\u4ee3\u7801",
        "name": "\u540d\u79f0",
        "market_value": st.column_config.NumberColumn("\u6301\u6709\u5e02\u503c", format="%.2f"),
        "pnl": st.column_config.NumberColumn("\u6301\u4ed3\u76c8\u4e8f", format="%.2f"),
        "pnl_pct": st.column_config.NumberColumn("\u76c8\u4e8f\u6bd4\u4f8b%", format="%.2f"),
        "weight": st.column_config.NumberColumn("\u4e2a\u80a1\u4ed3\u4f4d%", format="%.2f"),
        "quantity": st.column_config.NumberColumn("\u6301\u4ed3\u6570\u91cf", format="%.0f"),
        "available_quantity": st.column_config.NumberColumn("\u53ef\u7528\u6570\u91cf", format="%.0f"),
    },
    key=f"holding_editor_{st.session_state.editor_version}",
)
cash_balance = st.number_input(
    "\u73b0\u91d1\u4f59\u989d",
    value=float(st.session_state.cash_balance or 0),
    min_value=0.0,
    step=1000.0,
    format="%.2f",
)

st.subheader("\u5199\u5165")
write_cols = st.columns(3)
with write_cols[0]:
    if st.button("\u9884\u89c8\u98de\u4e66\u8bb0\u5f55", use_container_width=True):
        preview = build_preview_records(report_date, price_rows, holding_rows, cash_balance)
        st.session_state.feishu_preview = preview
        st.success(f"\u5df2\u751f\u6210\u9884\u89c8\uff1a\u6536\u76d8\u4ef7 {len(preview['prices'])} \u6761\uff0c\u6301\u4ed3/\u73b0\u91d1 {len(preview['holdings'])} \u6761\u3002")

with write_cols[1]:
    if st.button("\u5199\u5165\u98de\u4e66", type="primary", use_container_width=True):
        try:
            result = append_daily_records(report_date, price_rows, holding_rows, cash_balance)
            st.success(f"\u5199\u5165\u5b8c\u6210\uff1a\u6536\u76d8\u4ef7 {result['prices']} \u6761\uff0c\u6301\u4ed3/\u73b0\u91d1 {result['holdings']} \u6761\u3002")
        except Exception as exc:
            st.error(f"\u5199\u5165\u98de\u4e66\u5931\u8d25\uff1a{exc}")

with write_cols[2]:
    if st.button("\u5199\u5165 Excel \u5907\u7528", use_container_width=True):
        source = Path(excel_path).expanduser()
        output = Path("outputs") / f"ETF\u591a\u80a1\u8ddf\u8fdb_{report_date.strftime('%Y%m%d')}.xlsx"
        try:
            saved = update_workbook(source, output, report_date, price_rows, holding_rows, cash_balance)
            st.success(f"\u5df2\u751f\u6210\u66f4\u65b0\u540e\u7684 Excel\uff1a{saved.resolve()}")
        except Exception as exc:
            st.error(f"\u5199\u5165\u5931\u8d25\uff1a{exc}")

if "feishu_preview" in st.session_state:
    with st.expander("\u98de\u4e66\u5199\u5165\u9884\u89c8", expanded=False):
        st.write("\u6536\u76d8\u4ef7\u8868")
        st.dataframe(st.session_state.feishu_preview["prices"], use_container_width=True)
        st.write("\u6301\u4ed3\u8868")
        st.dataframe(st.session_state.feishu_preview["holdings"], use_container_width=True)

if st.button("\u751f\u6210\u8054\u7f51\u5206\u6790\u62a5\u544a", use_container_width=True):
    with st.spinner("\u6b63\u5728\u751f\u6210\u5206\u6790\u62a5\u544a..."):
        st.session_state.report = generate_report(
            report_date.isoformat(),
            price_rows,
            holding_rows,
            cash_balance,
            risk_profile=risk_profile,
            max_holdings=int(max_holdings),
        )

if st.session_state.report:
    st.subheader("\u660e\u65e5\u64cd\u4f5c\u5efa\u8bae")
    st.markdown(st.session_state.report)
