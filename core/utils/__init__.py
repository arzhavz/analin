import yfinance as yf

from curl_cffi import requests

session = requests.Session(impersonate="chrome")

def idr2usd(amount_idr: int) -> float:
    try:
        pair = yf.Ticker("USDIDR=X", session=session)
        data = pair.history(period="1d")
        if data.empty:
            raise ValueError("Gagal mendapatkan data nilai tukar.")

        rate = data["Close"].iloc[-1]

        usd_amount = amount_idr / rate
        return round(usd_amount, 4)

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return 0.0
    