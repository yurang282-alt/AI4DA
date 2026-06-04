from difflib import SequenceMatcher

from etf_config import ETF_UNIVERSE


def normalize_name(value: object) -> str:
    text = "" if value is None else str(value)
    for token in (" ", "\t", "\n", "...", "…", "国泰", "嘉实", "招商", "南方", "易方达", "华泰柏瑞"):
        text = text.replace(token, "")
    return text.upper()


def infer_etf_code(raw_name: object, raw_code: object = None) -> str:
    code = "" if raw_code is None else str(raw_code).strip()
    if code and code.isdigit():
        return code

    query = normalize_name(raw_name)
    if not query:
        return ""

    best_code = ""
    best_score = 0.0
    for item in ETF_UNIVERSE:
        candidates = [item["name"], item["code"], *item.get("aliases", [])]
        for candidate in candidates:
            target = normalize_name(candidate)
            if not target:
                continue
            if query in target or target in query:
                score = 1.0
            else:
                score = SequenceMatcher(None, query, target).ratio()
            if score > best_score:
                best_code = item["code"]
                best_score = score

    return best_code if best_score >= 0.58 else ""


def canonical_name(code: str, fallback: object = "") -> str:
    for item in ETF_UNIVERSE:
        if item["code"] == str(code):
            return item["name"]
    return "" if fallback is None else str(fallback)

