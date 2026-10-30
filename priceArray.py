# priceArray.py
import requests
from typing import List

TF_MAP = {
    "M5": "5m",
    "M15": "15m",
    "M30": "30m",
    "H1": "1h",
    "H4": "4h",
    "D1": "1d",
    "W1": "1d",
}

def getPriceArray(symbol: str, timeframe: str, bars: int = 100) -> List[float]:
    """
    回傳 flattened OHLC list: [open, high, low, close, open, high, low, close, ...]
    順序 oldest → newest，配合 rangeCalculator 的 for i in range(1, len, 4)
    """
    interval = TF_MAP.get(timeframe, "30m")
    url = f"https://biquote.io/api/{symbol}/ohlc"
    params = {"interval": interval, "limit": bars}

    try:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        bars_data = data.get("bars", [])

        if not bars_data:
            print(f"[getPriceArray] No bars returned for {symbol} {timeframe}")
            return []

        # biquote 預設 newest-first，反轉成 oldest-first
        bars_data = list(reversed(bars_data))

        flat = []
        for b in bars_data:
            flat.extend([
                float(b["open"]),
                float(b["high"]),
                float(b["low"]),
                float(b["close"]),
            ])
        return flat

    except Exception as e:
        print(f"[getPriceArray] Error fetching {symbol} {timeframe}: {e}")
        return []