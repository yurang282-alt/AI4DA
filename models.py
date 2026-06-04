from dataclasses import dataclass
from typing import Optional


@dataclass
class PriceRow:
    code: str
    name: str
    close: Optional[float] = None
    change_pct: Optional[float] = None


@dataclass
class HoldingRow:
    code: str
    name: str
    market_value: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    weight: Optional[float] = None
    quantity: Optional[float] = None
    available_quantity: Optional[float] = None
