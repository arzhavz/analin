import yfinance as yf

from curl_cffi import requests

from ta.trend import SMAIndicator, MACD, IchimokuIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice, OnBalanceVolumeIndicator

class StockAnalyzer:
    def __init__(self, ticker, period='ytd'):
        self.ticker = ticker
        self.period = period
        self.df = None
        self.result = {}
        self._initialize_data()
    
    def _initialize_data(self):
        """Mengambil data saham dari Yahoo Finance"""
        session = requests.Session(impersonate="chrome")
        stock = yf.Ticker(self.ticker, session=session)
        self.df = stock.history(period=self.period)
        
        if self.df.empty:
            raise ValueError("Unable to retrieve stock data")
    
    def analyze_all(self):
        """Menjalankan semua analisis"""
        self.calculate_moving_averages()
        self.calculate_momentum_indicators()
        self.calculate_volatility_indicators()
        self.calculate_volume_indicators()
        self.calculate_ichimoku_cloud()
        self.calculate_fibonacci_levels()
        self.analyze_trend()
        self.analyze_ma_status()
        self.analyze_macd()
        self.analyze_rsi()
        self.analyze_stochastic()
        self.analyze_volume()
        self.analyze_vwap()
        self.calculate_support_resistance()
        self.calculate_risk_reward()
        self.summarize_indicators()
        
        return self.result, self.df
    
    def calculate_moving_averages(self):
        """Menghitung moving averages"""
        self.df['MA20'] = SMAIndicator(self.df['Close'], window=20).sma_indicator()
        self.df['MA50'] = SMAIndicator(self.df['Close'], window=50).sma_indicator()
        self.df['MA200'] = self.df['Close'].rolling(window=200, min_periods=1).mean()
    
    def calculate_momentum_indicators(self):
        """Menghitung indikator momentum"""
        # RSI
        self.df['RSI'] = RSIIndicator(self.df['Close'], window=14).rsi()
        self.df['RSI_MA'] = SMAIndicator(self.df['RSI'], window=9).sma_indicator()
        
        # MACD
        macd = MACD(self.df['Close'], window_slow=26, window_fast=12, window_sign=9)
        self.df['MACD'] = macd.macd()
        self.df['MACD_signal'] = macd.macd_signal()
        self.df['MACD_hist'] = macd.macd_diff()
        
        # Stochastic
        stoch = StochasticOscillator(
            high=self.df['High'], 
            low=self.df['Low'], 
            close=self.df['Close'], 
            window=14, 
            smooth_window=3
        )
        self.df['Stoch_%K'] = stoch.stoch()
        self.df['Stoch_%D'] = stoch.stoch_signal()
    
    def calculate_volatility_indicators(self):
        """Menghitung indikator volatilitas"""
        # Bollinger Bands
        bb = BollingerBands(close=self.df['Close'], window=20, window_dev=2)
        self.df['BB_upper'] = bb.bollinger_hband()
        self.df['BB_middle'] = bb.bollinger_mavg()
        self.df['BB_lower'] = bb.bollinger_lband()
        
        # ATR
        atr = AverageTrueRange(
            high=self.df['High'], 
            low=self.df['Low'], 
            close=self.df['Close'], 
            window=14
        )
        self.df['ATR'] = atr.average_true_range()
    
    def calculate_volume_indicators(self):
        """Menghitung indikator volume"""
        # VWAP
        self.df['VWAP'] = VolumeWeightedAveragePrice(
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            volume=self.df['Volume'],
            window=20
        ).volume_weighted_average_price()
        
        # OBV
        obv = OnBalanceVolumeIndicator(close=self.df['Close'], volume=self.df['Volume'])
        self.df['OBV'] = obv.on_balance_volume()
        self.df['OBV_MA'] = SMAIndicator(self.df['OBV'], window=20).sma_indicator()
    
    def calculate_ichimoku_cloud(self):
        """Menghitung indikator Ichimoku Cloud"""
        ichimoku = IchimokuIndicator(
            high=self.df['High'], 
            low=self.df['Low'], 
            window1=9, 
            window2=26, 
            window3=52
        )
        self.df['Tenkan_sen'] = ichimoku.ichimoku_conversion_line()
        self.df['Kijun_sen'] = ichimoku.ichimoku_base_line()
        self.df['Senkou_span_a'] = ichimoku.ichimoku_a()
        self.df['Senkou_span_b'] = ichimoku.ichimoku_b()
    
    def calculate_fibonacci_levels(self):
        """Menghitung level Fibonacci retracement"""
        recent_low = self.df['Close'].rolling(50).min().iloc[-1]
        recent_high = self.df['Close'].rolling(50).max().iloc[-1]
        
        self.result['Fibonacci Levels'] = {
            '0%': recent_high,
            '23.6%': recent_high - (recent_high - recent_low) * 0.236,
            '38.2%': recent_high - (recent_high - recent_low) * 0.382,
            '50%': recent_high - (recent_high - recent_low) * 0.5,
            '61.8%': recent_high - (recent_high - recent_low) * 0.618,
            '100%': recent_low
        }
    
    def analyze_trend(self):
        """Menganalisis tren saham"""
        last = self.df.iloc[-1]
        last_close = last['Close']
        last_ma20 = last['MA20']
        last_ma50 = last['MA50']
        last_ma200 = last['MA200']
        
        price_above_ma200 = last_close > last_ma200
        ma20_above_ma50 = last_ma20 > last_ma50
        ma50_above_ma200 = last_ma50 > last_ma200
        
        trend = "Strong Uptrend" if (price_above_ma200 and ma20_above_ma50 and ma50_above_ma200) else \
                "Uptrend" if (price_above_ma200 and ma50_above_ma200) else \
                "Downtrend" if (last_close < last_ma50 and last_ma50 < last_ma200) else \
                "Strong Downtrend" if (last_close < last_ma200 and last_ma20 < last_ma50 and last_ma50 < last_ma200) else \
                "Sideways/Rebound"
        
        self.result['Trend'] = trend
        self.result['Current Price'] = last_close
    
    def analyze_ma_status(self):
        """Menganalisis status moving average"""
        last = self.df.iloc[-1]
        last_close = last['Close']
        last_ma20 = last['MA20']
        last_ma50 = last['MA50']
        last_ma200 = last['MA200']
        
        ma_status = "Bullish (Price > MA20 > MA50 > MA200)" if last_close > last_ma20 > last_ma50 > last_ma200 else \
                    "Bearish (Price < MA20 < MA50 < MA200)" if last_close < last_ma20 < last_ma50 < last_ma200 else \
                    "Bullish Crossover (Price > MA20 > MA50)" if last_close > last_ma20 > last_ma50 else \
                    "Bearish Crossover (Price < MA20 < MA50)" if last_close < last_ma20 < last_ma50 else \
                    "Mixed Signals (Watch for confirmation)"
        
        self.result['MA Status'] = ma_status
    
    def analyze_macd(self):
        """Menganalisis sinyal MACD"""
        last = self.df.iloc[-1]
        last_macd = last['MACD']
        last_macd_signal = last['MACD_signal']
        
        macd_signal = "Bullish (MACD > Signal)" if last_macd > last_macd_signal else \
                      "Bearish (MACD < Signal)" if last_macd < last_macd_signal else \
                      "Neutral (MACD = Signal)"
        
        self.result['MACD Signal'] = macd_signal
    
    def analyze_rsi(self):
        """Menganalisis sinyal RSI"""
        last = self.df.iloc[-1]
        last_rsi = last['RSI']
        last_rsi_ma = last['RSI_MA']
        
        rsi_signal = "Overbought (RSI > 70)" if last_rsi > 70 else \
                     "Oversold (RSI < 30)" if last_rsi < 30 else \
                     "Bullish (RSI > MA)" if last_rsi > last_rsi_ma else \
                     "Bearish (RSI < MA)" if last_rsi < last_rsi_ma else \
                     "Neutral"
        
        self.result['RSI (14)'] = round(last_rsi, 2)
        self.result['RSI Signal'] = rsi_signal
    
    def analyze_stochastic(self):
        """Menganalisis sinyal Stochastic"""
        last = self.df.iloc[-1]
        last_stoch_k = last['Stoch_%K']
        last_stoch_d = last['Stoch_%D']
        
        stoch_signal = "Overbought (%K > 80)" if last_stoch_k > 80 else \
                       "Oversold (%K < 20)" if last_stoch_k < 20 else \
                       "Bullish Cross (%K > %D)" if last_stoch_k > last_stoch_d else \
                       "Bearish Cross (%K < %D)" if last_stoch_k < last_stoch_d else \
                       "Neutral"
        
        self.result['Stochastic Signal'] = stoch_signal
    
    def analyze_volume(self):
        """Menganalisis sinyal volume"""
        last = self.df.iloc[-1]
        last_obv = last['OBV']
        last_obv_ma = last['OBV_MA']
        
        volume_signal = "Bullish (OBV > MA)" if last_obv > last_obv_ma else \
                        "Bearish (OBV < MA)" if last_obv < last_obv_ma else \
                        "Neutral Volume"
        
        self.result['Volume Signal'] = volume_signal
    
    def analyze_vwap(self):
        """Menganalisis sinyal VWAP"""
        last = self.df.iloc[-1]
        last_close = last['Close']
        last_vwap = last['VWAP']
        
        vwap_signal = "Bullish (Price > VWAP)" if last_close > last_vwap else \
                      "Bearish (Price < VWAP)" if last_close < last_vwap else \
                      "Neutral (Price ≈ VWAP)"
        
        self.result['VWAP Signal'] = vwap_signal
    
    def calculate_support_resistance(self):
        """Menghitung level support dan resistance"""
        support = self.df['Close'].rolling(20).min().iloc[-1]
        resistance = self.df['Close'].rolling(20).max().iloc[-1]
        
        self.result['Support Level'] = round(support, 2)
        self.result['Resistance Level'] = round(resistance, 2)
    
    def calculate_risk_reward(self):
        """Menghitung rasio risiko/reward dengan pendekatan lebih komprehensif"""
        last = self.df.iloc[-1]
        last_close = last['Close']
        last_atr = last['ATR']
    
        recent_low = self.df['Low'].rolling(20).min().iloc[-1]
        recent_high = self.df['High'].rolling(20).max().iloc[-1]
    
        consolidation_threshold = 0.015 * last_close  
        consolidated_areas = []
        for i in range(len(self.df)-5, len(self.df)-20, -1):
            window = self.df.iloc[i:i+5]
            range_pct = (window['High'].max() - window['Low'].min()) / last_close
            if range_pct < consolidation_threshold:
                avg_price = window['Close'].mean()
                consolidated_areas.append(avg_price)
    
        all_levels = [
            self.result['Fibonacci Levels']['23.6%'],
            self.result['Fibonacci Levels']['38.2%'],
            self.result['Fibonacci Levels']['50%'],
            self.result['Fibonacci Levels']['61.8%'],
            recent_low,
            recent_high,
            *consolidated_areas
        ]
    
        support_levels = sorted([lvl for lvl in all_levels if lvl < last_close], reverse=True)
        resistance_levels = sorted([lvl for lvl in all_levels if lvl > last_close])
    
        atr_multiplier = 1.5 if (last_atr/last_close) < 0.02 else 2.0  
    
        recent_lows = self.df['Low'].rolling(5).min().iloc[-5:].tolist()
        recent_highs = self.df['High'].rolling(5).max().iloc[-5:].tolist()
    
        entry_low = min(recent_lows) - (0.5 * last_atr)
        entry_high = max(min(recent_lows) + (0.5 * last_atr), last_close - (0.3 * last_atr))
    
        if resistance_levels:
            target1 = resistance_levels[0]  
            if len(resistance_levels) > 1:
                target2 = resistance_levels[1]  
            else:
                target2 = target1 + (2 * last_atr)  
        else:
            target1 = last_close + (atr_multiplier * last_atr)
            target2 = last_close + (2 * atr_multiplier * last_atr)
    
        if support_levels:
            stop_loss = min(support_levels[0] - (0.5 * last_atr), last_close - (atr_multiplier * last_atr))
        else:
            stop_loss = last_close - (atr_multiplier * last_atr)
    
        potential_upside_pct = round(((target1 - last_close) / last_close) * 100, 2)
        potential_downside_pct = round(((last_close - stop_loss) / last_close) * 100, 2)
    
        self.result['Potential Upside'] = f"{potential_upside_pct}% to {round(target1, 2)}"
        self.result['Potential Downside'] = f"-{potential_downside_pct}% to {round(stop_loss, 2)}"
        self.result['Entry Zone'] = f"{round(entry_low, 2)} - {round(entry_high, 2)}"
        self.result['Target 1'] = round(target1, 2)
        self.result['Target 2'] = round(target2, 2)
        self.result['Stop Loss'] = f"< {round(stop_loss, 2)}"
        self.result['Key Support Levels'] = [round(lvl, 2) for lvl in support_levels[:3]]
        self.result['Key Resistance Levels'] = [round(lvl, 2) for lvl in resistance_levels[:3]]
    
    def analyze_ichimoku(self):
        """Menganalisis sinyal Ichimoku"""
        last = self.df.iloc[-1]
        last_close = last['Close']
        
        ichimoku_signal = "Strong Bullish (Price above cloud, Tenkan > Kijun)" if (last_close > last['Senkou_span_a']) and (last_close > last['Senkou_span_b']) and (last['Tenkan_sen'] > last['Kijun_sen']) else \
                          "Bullish (Price above cloud)" if (last_close > last['Senkou_span_a']) and (last_close > last['Senkou_span_b']) else \
                          "Strong Bearish (Price below cloud, Tenkan < Kijun)" if (last_close < last['Senkou_span_a']) and (last_close < last['Senkou_span_b']) and (last['Tenkan_sen'] < last['Kijun_sen']) else \
                          "Bearish (Price below cloud)" if (last_close < last['Senkou_span_a']) and (last_close < last['Senkou_span_b']) else \
                          "Neutral (Price in cloud)"
        
        self.result['Ichimoku Signal'] = ichimoku_signal
    
    def summarize_indicators(self):
        """Membuat ringkasan indikator"""
        trend_confirmed = (
            (self.result['Trend'].startswith("Uptrend") and 
             self.result['MACD Signal'].startswith("Bullish") and 
             self.result['RSI Signal'].startswith("Bullish")) or 
            (self.result['Trend'].startswith("Downtrend") and 
             self.result['MACD Signal'].startswith("Bearish") and 
             self.result['RSI Signal'].startswith("Bearish"))
        )
        
        last_atr = self.df.iloc[-1]['ATR']
        last_close = self.df.iloc[-1]['Close']
        
        self.result['Indicators Summary'] = {
            'Trend Confirmation': "Confirmed" if trend_confirmed else "Unconfirmed",
            'Volume Confirmation': self.result['Volume Signal'],
            'Volatility': "High" if last_atr > (0.02 * last_close) else "Medium" if last_atr > (0.01 * last_close) else "Low"
        }
        self.result['Ticker'] = self.ticker