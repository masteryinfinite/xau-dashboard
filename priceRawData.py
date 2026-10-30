# priceRawData.py
# 雲端簡化版：不再使用 MetaTrader5，也不再寫本地檔案

def saveInitialData(n, path, symbol, interval):
    """原本會儲存 CSV，現在改為空操作（數據即時由 API 取得）"""
    print(f"[saveInitialData] {symbol} {interval} n={n} → skipped (live API)")

def saveRealTimeData(folder_path, symbol, interval):
    """原本會更新 CSV，現在改為空操作"""
    print(f"[saveRealTimeData] {symbol} {interval} → skipped (live API)")