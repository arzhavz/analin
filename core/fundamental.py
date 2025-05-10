import yfinance as yf

from curl_cffi import requests

session = requests.Session(impersonate="chrome")

def format_number(value):
    if value is None:
        return "N/A"
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"{value/1_000_000_000_000:.2f}T"
    elif abs_value >= 1_000_000_000:
        return f"{value/1_000_000_000:.2f}B"
    elif abs_value >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    else:
        return str(value)
    
def get_fundamental_data(ticker):
    stock = yf.Ticker(ticker, session=session)
    info = stock.info
    financials = stock.financials
    balance_sheet = stock.balance_sheet

    return {
        "Company": info.get("longName", "N/A"),
        "Symbol": info.get("symbol", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Recommendation": info.get("averageAnalystRating", "N/A"),
        "Market Cap": format_number(info.get("marketCap")),
        "Current Price": format_number(info.get("currentPrice")),
        "Book Value per Share (BVPS)": f"{round(info.get('bookValue', 0), 2)}" if info.get("bookValue") else "N/A",
        "Price to Book Value (PBV)": f"{round(info.get('priceToBook', 0), 2)}%" if info.get("priceToBook") else "N/A",
        "Trailing P/E": round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A",
        "Forward P/E": round(info.get("forwardPE", 0), 2) if info.get("forwardPE") else "N/A",
        "EPS (TTM)": round(info.get("trailingEps", 0), 2) if info.get("trailingEps") else "N/A",
        "Dividend Yield": f"{round(info.get('dividendYield', 0), 2)}%" if info.get("dividendYield") else "N/A",
        "Dividend per Share": format_number(info.get("dividendRate")),
        "Payout Ratio": f"{round(info.get('payoutRatio', 0) * 100, 2)}%" if info.get("payoutRatio") else "N/A",
        "ROE": f"{round(info.get('returnOnEquity', 0) * 100, 2)}%" if info.get("returnOnEquity") else "N/A",
        "ROA": f"{round(info.get('returnOnAssets', 0) * 100, 2)}%" if info.get("returnOnAssets") else "N/A",
        "Debt to Equity": round(info.get("debtToEquity", 0) / 100, 2) if info.get("debtToEquity") else "N/A",
        "Current Ratio": round(info.get("currentRatio", 0), 2) if info.get("currentRatio") else "N/A",
        "Quick Ratio": round(info.get("quickRatio", 0), 2) if info.get("quickRatio") else "N/A",
        "Gross Margin": f"{round(info.get('grossMargins', 0) * 100, 2)}%" if info.get("grossMargins") else "N/A",
        "Operating Margin": f"{round(info.get('operatingMargins', 0) * 100, 2)}%" if info.get("operatingMargins") else "N/A",
        "Profit Margin": f"{round(info.get('profitMargins', 0) * 100, 2)}%" if info.get("profitMargins") else "N/A",
        "Revenue (TTM)": format_number(info.get("totalRevenue")),
        "Net Income (TTM)": format_number(info.get("netIncomeToCommon")),
        "Free Cash Flow": format_number(info.get("freeCashflow")),
        "Beta": round(info.get("beta", 0), 2) if info.get("beta") else "N/A",
        "52 Week High": format_number(info.get("fiftyTwoWeekHigh")),
        "52 Week Low": format_number(info.get("fiftyTwoWeekLow")),
        "Trailing Annual Net Income": format_number(financials.loc["Net Income"].sum()) if "Net Income" in financials.index else "N/A",
        "Operating Cash Flow": format_number(info.get("operatingCashflow")),
        "Shares Outstanding": format_number(info.get("sharesOutstanding")),
        "Total Assets": format_number(balance_sheet.loc["Total Assets"].iloc[0]) if "Total Assets" in balance_sheet.index else "N/A",
    }