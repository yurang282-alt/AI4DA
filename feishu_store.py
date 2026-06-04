from __future__ import annotations

import os
import json
import subprocess
from datetime import date
from typing import Any, Optional

import requests

from etf_matching import canonical_name, infer_etf_code


FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"


class FeishuConfigError(RuntimeError):
    pass


def env_ready() -> bool:
    if os.getenv("FEISHU_WRITE_MODE", "").strip().lower() == "cli":
        return bool(
            os.getenv("FEISHU_BITABLE_APP_TOKEN")
            and os.getenv("FEISHU_PRICE_TABLE_ID")
            and os.getenv("FEISHU_HOLDING_TABLE_ID")
        )

    required = [
        "FEISHU_APP_ID",
        "FEISHU_APP_SECRET",
        "FEISHU_BITABLE_APP_TOKEN",
        "FEISHU_PRICE_TABLE_ID",
        "FEISHU_HOLDING_TABLE_ID",
    ]
    return all(os.getenv(name) for name in required)


def append_daily_records(
    day: date,
    prices: list[dict],
    holdings: list[dict],
    cash_balance: Optional[float],
) -> dict[str, int]:
    if os.getenv("FEISHU_WRITE_MODE", "").strip().lower() == "cli":
        return _append_daily_records_with_cli(day, prices, holdings, cash_balance)

    config = _read_config()
    token = _tenant_access_token(config["app_id"], config["app_secret"])
    price_records = [_price_record(day, row) for row in prices]
    price_records = [record for record in price_records if record]
    holding_records = [_holding_record(day, row) for row in holdings]
    holding_records = [record for record in holding_records if record]
    if cash_balance is not None:
        holding_records.append(_cash_record(day, cash_balance))

    if price_records:
        _batch_create_records(token, config["app_token"], config["price_table_id"], price_records)
    if holding_records:
        _batch_create_records(token, config["app_token"], config["holding_table_id"], holding_records)

    return {"prices": len(price_records), "holdings": len(holding_records)}


def _append_daily_records_with_cli(
    day: date,
    prices: list[dict],
    holdings: list[dict],
    cash_balance: Optional[float],
) -> dict[str, int]:
    app_token = os.getenv("FEISHU_BITABLE_APP_TOKEN", "").strip()
    price_table_id = os.getenv("FEISHU_PRICE_TABLE_ID", "").strip()
    holding_table_id = os.getenv("FEISHU_HOLDING_TABLE_ID", "").strip()
    if not app_token or not price_table_id or not holding_table_id:
        raise FeishuConfigError("CLI 写入需要 FEISHU_BITABLE_APP_TOKEN、FEISHU_PRICE_TABLE_ID、FEISHU_HOLDING_TABLE_ID")

    preview = build_preview_records(day, prices, holdings, cash_balance)
    if preview["prices"]:
        _cli_batch_create(
            app_token,
            price_table_id,
            ["ETF代码", "日期", "ETF名称", "收盘价", "涨跌幅%"],
            preview["prices"],
        )
    if preview["holdings"]:
        _cli_batch_create(
            app_token,
            holding_table_id,
            [
                "ETF代码",
                "日期",
                "ETF名称",
                "持有市值",
                "持仓盈亏",
                "盈亏比例%",
                "个股仓位%",
                "持仓数量",
                "可用数量",
                "现金余额",
            ],
            preview["holdings"],
        )
    return {"prices": len(preview["prices"]), "holdings": len(preview["holdings"])}


def build_preview_records(
    day: date,
    prices: list[dict],
    holdings: list[dict],
    cash_balance: Optional[float],
) -> dict[str, list[dict]]:
    price_records = [_price_record(day, row) for row in prices]
    holding_records = [_holding_record(day, row) for row in holdings]
    if cash_balance is not None:
        holding_records.append(_cash_record(day, cash_balance))
    return {
        "prices": [record for record in price_records if record],
        "holdings": [record for record in holding_records if record],
    }


def _cli_batch_create(app_token: str, table_id: str, fields: list[str], records: list[dict]) -> None:
    payload = {
        "fields": fields,
        "rows": [[record.get(field) for field in fields] for record in records],
    }
    command = [
        "lark-cli",
        "base",
        "+record-batch-create",
        "--base-token",
        app_token,
        "--table-id",
        table_id,
        "--json",
        json.dumps(payload, ensure_ascii=False),
        "--as",
        "user",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    data = json.loads(result.stdout)
    if not data.get("ok"):
        raise RuntimeError(result.stdout)


def _read_config() -> dict[str, str]:
    config = {
        "app_id": os.getenv("FEISHU_APP_ID", "").strip(),
        "app_secret": os.getenv("FEISHU_APP_SECRET", "").strip(),
        "app_token": os.getenv("FEISHU_BITABLE_APP_TOKEN", "").strip(),
        "price_table_id": os.getenv("FEISHU_PRICE_TABLE_ID", "").strip(),
        "holding_table_id": os.getenv("FEISHU_HOLDING_TABLE_ID", "").strip(),
    }
    missing = [name for name, value in config.items() if not value]
    if missing:
        raise FeishuConfigError(f"缺少飞书配置：{', '.join(missing)}")
    return config


def _tenant_access_token(app_id: str, app_secret: str) -> str:
    response = requests.post(
        f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 0:
        raise RuntimeError(f"飞书授权失败：{data}")
    return data["tenant_access_token"]


def _batch_create_records(
    token: str,
    app_token: str,
    table_id: str,
    records: list[dict[str, Any]],
) -> None:
    response = requests.post(
        f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"records": [{"fields": record} for record in records]},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 0:
        raise RuntimeError(f"写入飞书失败：{data}")


def _price_record(day: date, row: dict) -> dict[str, Any]:
    code = infer_etf_code(row.get("name"), row.get("code"))
    close = _to_float(row.get("close"))
    if not code or close is None:
        return {}
    return {
        "日期": day.isoformat(),
        "ETF代码": code,
        "ETF名称": canonical_name(code, row.get("name")),
        "收盘价": close,
        "涨跌幅%": _to_float(row.get("change_pct")),
    }


def _holding_record(day: date, row: dict) -> dict[str, Any]:
    code = infer_etf_code(row.get("name"), row.get("code"))
    if not code:
        return {}
    return {
        "日期": day.isoformat(),
        "ETF代码": code,
        "ETF名称": canonical_name(code, row.get("name")),
        "持有市值": _to_float(row.get("market_value")),
        "持仓盈亏": _to_float(row.get("pnl")),
        "盈亏比例%": _to_float(row.get("pnl_pct")),
        "个股仓位%": _to_float(row.get("weight")),
        "持仓数量": _to_float(row.get("quantity")),
        "可用数量": _to_float(row.get("available_quantity")),
        "现金余额": None,
    }


def _cash_record(day: date, cash_balance: float) -> dict[str, Any]:
    return {
        "日期": day.isoformat(),
        "ETF代码": "CASH",
        "ETF名称": "现金",
        "持有市值": None,
        "持仓盈亏": None,
        "盈亏比例%": None,
        "个股仓位%": None,
        "持仓数量": None,
        "可用数量": None,
        "现金余额": _to_float(cash_balance),
    }


def _to_float(value):
    if value in (None, "", "-"):
        return None
    if isinstance(value, str):
        value = value.replace(",", "").replace("%", "").strip()
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
