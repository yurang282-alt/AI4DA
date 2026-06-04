from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path
from typing import Any, Optional, Union

from openai import OpenAI


EXTRACTION_SCHEMA_HINT = {
    "prices": [
        {"code": "512880", "name": "证券ETF", "close": 1.035, "change_pct": 0.19}
    ],
    "holdings": [
        {
            "code": "",
            "name": "证券ETF国泰",
            "market_value": 28462.5,
            "pnl": -8506.6,
            "pnl_pct": -23.01,
            "weight": 7.0,
            "quantity": 27500,
            "available_quantity": 17500,
        }
    ],
    "cash_balance": 78499.51,
}


def has_api_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _image_part(path: Union[str, Path]) -> dict[str, str]:
    path = Path(path)
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return {"type": "input_image", "image_url": f"data:{mime};base64,{data}"}


def extract_from_screenshots(
    price_image: Optional[Union[str, Path]], holding_image: Optional[Union[str, Path]]
) -> dict[str, Any]:
    if not has_api_key():
        return {"prices": [], "holdings": [], "cash_balance": None}

    content: list[dict[str, Any]] = [
        {
            "type": "input_text",
            "text": (
                "请从广发易淘金 APP 截图中提取 ETF 数据，只返回 JSON，不要解释。"
                "价格截图提取 name、code、close、change_pct。"
                "持仓截图提取 name、market_value、pnl、pnl_pct、weight、quantity、available_quantity、cash_balance。"
                "如果持仓截图没有 ETF 代码，code 留空。百分比使用数字，例如 -3.4。"
                f"JSON 结构参考：{json.dumps(EXTRACTION_SCHEMA_HINT, ensure_ascii=False)}"
            ),
        }
    ]
    if price_image:
        content.append(_image_part(price_image))
    if holding_image:
        content.append(_image_part(holding_image))

    response = _client().responses.create(
        model=os.getenv("OPENAI_VISION_MODEL", "gpt-4.1"),
        input=[{"role": "user", "content": content}],
    )
    return _parse_json(response.output_text)


def generate_report(
    report_date: str,
    prices: list[dict],
    holdings: list[dict],
    cash_balance: Optional[float],
    risk_profile: str = "均衡",
    max_holdings: int = 5,
) -> str:
    if not has_api_key():
        return "未配置 OPENAI_API_KEY。请先在 .env 中配置后再生成联网分析报告。"

    prompt = f"""
你是一位严谨的 ETF 交易复盘助手。请基于用户的 ETF 收盘价格、持仓、现金，以及联网检索到的宏观、行业、地缘政治和市场信息，生成明日操作建议。

约束：
- 关注标的是 11 只 ETF。
- 风格：{risk_profile}。
- 最多持有 ETF 数量：{max_holdings} 只。
- 不直接鼓励重仓赌博式交易。
- 输出应包含风险收益、持仓分析、明日操作计划、价格区间、金额/数量建议、风险提示。
- 所有建议都应说明依据和不确定性。
- 不承诺收益，不替用户执行交易。

日期：{report_date}
收盘价格：{json.dumps(prices, ensure_ascii=False)}
持仓：{json.dumps(holdings, ensure_ascii=False)}
现金余额：{cash_balance}
"""
    try:
        response = _client().responses.create(
            model=os.getenv("OPENAI_ANALYSIS_MODEL", "gpt-4.1"),
            tools=[{"type": "web_search_preview"}],
            input=prompt,
        )
    except Exception:
        response = _client().responses.create(
            model=os.getenv("OPENAI_ANALYSIS_MODEL", "gpt-4.1"),
            input=prompt + "\n如果当前环境不能联网，请仅基于已提供数据给出结构化分析，并明确说明未联网。",
        )
    return response.output_text


def _parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        data = json.loads(match.group(0)) if match else {}
    return {
        "prices": data.get("prices", []),
        "holdings": data.get("holdings", []),
        "cash_balance": data.get("cash_balance"),
    }
