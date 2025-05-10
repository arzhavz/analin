import yfinance as yf

from curl_cffi import requests

from ta.trend import SMAIndicator, MACD, IchimokuIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice


def analyze_stock(ticker, period='ytd'):
    session = requests.Session(impersonate="chrome")
    stock = yf.Ticker(ticker, session=session)
    df = stock.history(period=period)

    if df.empty:
        return {"error": "Unable to retrieve stock data"}, df

    # Basic Moving Averages
    df['MA20'] = SMAIndicator(df['Close'], window=20).sma_indicator()
    df['MA50'] = SMAIndicator(df['Close'], window=50).sma_indicator()
    df['MA200'] = df['Close'].rolling(window=200, min_periods=1).mean()
    
    # Momentum Indicators
    df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
    df['RSI_MA'] = SMAIndicator(df['RSI'], window=9).sma_indicator()
    
    # MACD with signal line
    macd = MACD(df['Close'], window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_hist'] = macd.macd_diff()
    
    # Stochastic Oscillator
    stoch = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'], window=14, smooth_window=3)
    df['Stoch_%K'] = stoch.stoch()
    df['Stoch_%D'] = stoch.stoch_signal()
    
    # Volatility Indicators
    bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_middle'] = bb.bollinger_mavg()
    df['BB_lower'] = bb.bollinger_lband()
    
    atr = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14)
    df['ATR'] = atr.average_true_range()
    
    # Volume Indicators
    df['VWAP'] = VolumeWeightedAveragePrice(
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        volume=df['Volume'],
        window=20
    ).volume_weighted_average_price()
    
    obv = OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume'])
    df['OBV'] = obv.on_balance_volume()
    df['OBV_MA'] = SMAIndicator(df['OBV'], window=20).sma_indicator()
    
    # Ichimoku Cloud
    ichimoku = IchimokuIndicator(high=df['High'], low=df['Low'], window1=9, window2=26, window3=52)
    df['Tenkan_sen'] = ichimoku.ichimoku_conversion_line()
    df['Kijun_sen'] = ichimoku.ichimoku_base_line()
    df['Senkou_span_a'] = ichimoku.ichimoku_a()
    df['Senkou_span_b'] = ichimoku.ichimoku_b()
    
    # Calculate Fibonacci levels
    recent_low = df['Close'].rolling(50).min().iloc[-1]
    recent_high = df['Close'].rolling(50).max().iloc[-1]
    fib_levels = {
        '0%': recent_high,
        '23.6%': recent_high - (recent_high - recent_low) * 0.236,
        '38.2%': recent_high - (recent_high - recent_low) * 0.382,
        '50%': recent_high - (recent_high - recent_low) * 0.5,
        '61.8%': recent_high - (recent_high - recent_low) * 0.618,
        '100%': recent_low
    }
    
    last = df.iloc[-1]
    last_close = last['Close']
    last_ma20 = last['MA20']
    last_ma50 = last['MA50']
    last_ma200 = last['MA200']
    last_rsi = last['RSI']
    last_rsi_ma = last['RSI_MA']
    last_vwap = last['VWAP']
    last_atr = last['ATR']
    last_macd = last['MACD']
    last_macd_signal = last['MACD_signal']
    last_stoch_k = last['Stoch_%K']
    last_stoch_d = last['Stoch_%D']
    last_obv = last['OBV']
    last_obv_ma = last['OBV_MA']

    # Support/Resistance based on recent price action and Fibonacci
    support = df['Close'].rolling(20).min().iloc[-1]
    resistance = df['Close'].rolling(20).max().iloc[-1]
    
    # Trend Analysis
    price_above_ma200 = last_close > last_ma200
    ma20_above_ma50 = last_ma20 > last_ma50
    ma50_above_ma200 = last_ma50 > last_ma200
    
    trend = "Strong Uptrend" if (price_above_ma200 and ma20_above_ma50 and ma50_above_ma200) else \
            "Uptrend" if (price_above_ma200 and ma50_above_ma200) else \
            "Downtrend" if (last_close < last_ma50 and last_ma50 < last_ma200) else \
            "Strong Downtrend" if (last_close < last_ma200 and last_ma20 < last_ma50 and last_ma50 < last_ma200) else \
            "Sideways/Rebound"
    
    # MA Status
    ma_status = "Bullish (Price > MA20 > MA50 > MA200)" if last_close > last_ma20 > last_ma50 > last_ma200 else \
                "Bearish (Price < MA20 < MA50 < MA200)" if last_close < last_ma20 < last_ma50 < last_ma200 else \
                "Bullish Crossover (Price > MA20 > MA50)" if last_close > last_ma20 > last_ma50 else \
                "Bearish Crossover (Price < MA20 < MA50)" if last_close < last_ma20 < last_ma50 else \
                "Mixed Signals (Watch for confirmation)"
    
    # MACD Analysis
    macd_signal = "Bullish (MACD > Signal)" if last_macd > last_macd_signal else \
                  "Bearish (MACD < Signal)" if last_macd < last_macd_signal else \
                  "Neutral (MACD = Signal)"
    
    # RSI Analysis with MA
    rsi_signal = "Overbought (RSI > 70)" if last_rsi > 70 else \
                 "Oversold (RSI < 30)" if last_rsi < 30 else \
                 "Bullish (RSI > MA)" if last_rsi > last_rsi_ma else \
                 "Bearish (RSI < MA)" if last_rsi < last_rsi_ma else \
                 "Neutral"
    
    # Stochastic Analysis
    stoch_signal = "Overbought (%K > 80)" if last_stoch_k > 80 else \
                   "Oversold (%K < 20)" if last_stoch_k < 20 else \
                   "Bullish Cross (%K > %D)" if last_stoch_k > last_stoch_d else \
                   "Bearish Cross (%K < %D)" if last_stoch_k < last_stoch_d else \
                   "Neutral"
    
    # Volume Analysis
    volume_signal = "Bullish (OBV > MA)" if last_obv > last_obv_ma else \
                    "Bearish (OBV < MA)" if last_obv < last_obv_ma else \
                    "Neutral Volume"
    
    # VWAP Analysis
    vwap_signal = "Bullish (Price > VWAP)" if last_close > last_vwap else \
                  "Bearish (Price < VWAP)" if last_close < last_vwap else \
                  "Neutral (Price ≈ VWAP)"
    
    # Calculate risk/reward based on ATR
    fib_targets = [fib_levels['23.6%'], fib_levels['38.2%'], fib_levels['50%'], fib_levels['61.8%']]
    fib_targets_sorted = sorted(fib_targets)

    # Look for resistance/fib levels above the current price
    next_resistance_candidates = [level for level in fib_targets_sorted if level > last_close]
    next_support_candidates = [level for level in fib_targets_sorted[::-1] if level < last_close]

    next_resistance = next_resistance_candidates[0] if next_resistance_candidates else resistance
    next_support = next_support_candidates[0] if next_support_candidates else support

    # Create a small ATR based buffer
    atr_buffer = 0.5 * last_atr

    # Upside and Downside
    potential_upside = round(min(next_resistance, resistance) + atr_buffer, 2)
    potential_downside = round(max(next_support, support) - atr_buffer, 2)

    # Percentage
    potential_upside_pct = round(((potential_upside - last_close) / last_close) * 100, 2)
    potential_downside_pct = round(((last_close - potential_downside) / last_close) * 100, 2)
    
    # Entry/Exit points
    entry_low = round(last_close - (last_atr), 2)
    entry_high = round(last_close - (0.5 * last_atr), 2)
    target1 = round(last_close + (1.5 * last_atr), 2)
    target2 = round(last_close + (3 * last_atr), 2)
    stop_loss = round(last_close - (1.5 * last_atr), 2)
    
    ichimoku_signal = "Strong Bullish (Price above cloud, Tenkan > Kijun)" if (last_close > last['Senkou_span_a']) and (last_close > last['Senkou_span_b']) and (last['Tenkan_sen'] > last['Kijun_sen']) else \
                      "Bullish (Price above cloud)" if (last_close > last['Senkou_span_a']) and (last_close > last['Senkou_span_b']) else \
                      "Strong Bearish (Price below cloud, Tenkan < Kijun)" if (last_close < last['Senkou_span_a']) and (last_close < last['Senkou_span_b']) and (last['Tenkan_sen'] < last['Kijun_sen']) else \
                      "Bearish (Price below cloud)" if (last_close < last['Senkou_span_a']) and (last_close < last['Senkou_span_b']) else \
                      "Neutral (Price in cloud)"
    
    result = {
        "Ticker": ticker,
        "Current Price": last_close,
        "Trend": trend,
        "MA Status": ma_status,
        "Ichimoku Signal": ichimoku_signal,
        "RSI (14)": round(last_rsi, 2),
        "RSI Signal": rsi_signal,
        "MACD Signal": macd_signal,
        "Stochastic Signal": stoch_signal,
        "Volume Signal": volume_signal,
        "VWAP Signal": vwap_signal,
        "Volatility (ATR)": round(last_atr, 2),
        "Support Level": round(support, 2),
        "Resistance Level": round(resistance, 2),
        "Fibonacci Levels": fib_levels,
        "Potential Upside": f"{potential_upside_pct}% to {potential_upside}",
        "Potential Downside": f"-{potential_downside_pct}% to {potential_downside}",
        "Risk/Reward Ratio": f"1:{round((potential_upside - last_close)/(last_close - stop_loss), 2)}",
        "Entry Zone": f"{entry_low} - {entry_high}",
        "Target 1": target1,
        "Target 2": target2,
        "Stop Loss": f"< {stop_loss}",
        "Indicators Summary": {
            "Trend Confirmation": "Confirmed" if (trend.startswith("Uptrend") and macd_signal.startswith("Bullish") and rsi_signal.startswith("Bullish")) or 
                                 (trend.startswith("Downtrend") and macd_signal.startswith("Bearish") and rsi_signal.startswith("Bearish")) else "Unconfirmed",
            "Volume Confirmation": volume_signal,
            "Volatility": "High" if last_atr > (0.02 * last_close) else "Medium" if last_atr > (0.01 * last_close) else "Low"
        }
    }

    return result, df