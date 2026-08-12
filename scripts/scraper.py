import requests
import pandas as pd
from datetime import date
import time
import os
import sys

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INST_DIR = os.path.join(BASE_DIR, "data", "institutional")
MARGIN_DIR = os.path.join(BASE_DIR, "data", "margin")
os.makedirs(INST_DIR, exist_ok=True)
os.makedirs(MARGIN_DIR, exist_ok=True)


def fetch_institutional_investors(query_date: str):
    url = "https://www.twse.com.tw/rwd/zh/fund/BFI82U"
    params = {"response": "json", "date": query_date}
    r = requests.get(url, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("stat") != "OK":
        return None
    df = pd.DataFrame(data["data"], columns=data["fields"])
    df.insert(0, "date", query_date)
    return df


def fetch_margin_trading(query_date: str):
    url = "https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN"
    params = {"response": "json", "date": query_date}
    r = requests.get(url, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("stat") != "OK":
        return None
    df = pd.DataFrame(data["tables"][0]["data"], columns=data["tables"][0]["fields"])
    df.insert(0, "date", query_date)
    return df


def main():
    today = date.today().strftime("%Y%m%d")
    had_data = False

    df_inst = fetch_institutional_investors(today)
    if df_inst is not None:
        path = os.path.join(INST_DIR, f"institutional_{today}.csv")
        df_inst.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"[OK] 三大法人資料已存 {path}")
        had_data = True
    else:
        print(f"[Skip] {today} 無三大法人資料（可能是假日）")

    time.sleep(2)

    df_margin = fetch_margin_trading(today)
    if df_margin is not None:
        path = os.path.join(MARGIN_DIR, f"margin_{today}.csv")
        df_margin.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"[OK] 融資融券資料已存 {path}")
        had_data = True
    else:
        print(f"[Skip] {today} 無融資融券資料（可能是假日）")

    # 若當天完全沒資料，回傳非 0 exit code 讓 Actions 顯示為警告方便追蹤（非必要，可拿掉）
    if not had_data:
        sys.exit(0)  # 用 0 而非非 0，避免假日被標記成「失敗」


if __name__ == "__main__":
    main()
