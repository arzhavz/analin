import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import yfinance as yf

from curl_cffi import requests

session = requests.Session(impersonate="chrome")

def plot_technical_chart(df, ticker):
    mc = mpf.make_marketcolors(up='g', down='r', edge='inherit', wick='inherit', volume='in')
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', y_on_right=False)
    
    # Create panels for additional indicators
    ap = [
        # Price panel indicators
        mpf.make_addplot(df['MA20'], color='blue', width=1.5, panel=0, label='MA20'),
        mpf.make_addplot(df['MA50'], color='green', width=1.5, panel=0, label='MA50'),
        mpf.make_addplot(df['MA200'], color='red', width=1.5, panel=0, label='MA200'),
        mpf.make_addplot(df['VWAP'], color='cyan', width=1.5, panel=0, label='VWAP'),
        mpf.make_addplot(df['BB_upper'], color='gray', linestyle='--', width=1, alpha=0.8, panel=0, label='BB Upper'),
        mpf.make_addplot(df['BB_lower'], color='gray', linestyle='--', width=1, alpha=0.8, panel=0, label='BB Lower'),
        mpf.make_addplot(df['Tenkan_sen'], color='orange', width=1.5, panel=0, label='Tenkan Sen'),
        mpf.make_addplot(df['Kijun_sen'], color='purple', width=1.5, panel=0, label='Kijun Sen'),
        mpf.make_addplot(df['Senkou_span_a'], color='lime', linestyle=':', width=1.5, alpha=0.7, panel=0, label='Senkou A'),
        mpf.make_addplot(df['Senkou_span_b'], color='pink', linestyle=':', width=1.5, alpha=0.7, panel=0, label='Senkou B'),
        
        # MACD panel
        mpf.make_addplot(df['MACD'], color='blue', width=1, panel=1, label='MACD'),
        mpf.make_addplot(df['MACD_signal'], color='red', width=1, panel=1, label='Signal'),
        mpf.make_addplot(df['MACD_hist'], type='bar', color=np.where(df['MACD_hist'] >= 0, 'g', 'r'), alpha=0.5, panel=1, label='Histogram'),
        
        # RSI panel
        mpf.make_addplot(df['RSI'], color='purple', width=1, panel=2, label='RSI (14)'),
        mpf.make_addplot(df['RSI_MA'], color='orange', width=1, panel=2, label='RSI MA (9)'),
        
        # Stochastic panel
        mpf.make_addplot(df['Stoch_%K'], color='blue', width=1, panel=3, label='%K'),
        mpf.make_addplot(df['Stoch_%D'], color='red', width=1, panel=3, label='%D'),
        
        # OBV panel
        mpf.make_addplot(df['OBV'], color='blue', width=1, panel=4, label='OBV'),
        mpf.make_addplot(df['OBV_MA'], color='red', width=1, panel=4, label='OBV MA (20)'),
    ]

    fig, axlist = mpf.plot(
        df,
        type='candle',
        style=s,
        addplot=ap,
        volume=True,
        title=f"\n{yf.Ticker(ticker, session=session).info['longName']} – Technical Analysis",
        ylabel="Price",
        ylabel_lower="Volume",
        figsize=(16, 12),
        returnfig=True,
        panel_ratios=(4, 1, 1, 1, 1),
        scale_padding={'left': 0.5, 'top': 1.1, 'right': 1.3, 'bottom': 0.6},
        xrotation=0,
        datetime_format='%d %b %Y',
        tight_layout=True,
        update_width_config=dict(candle_linewidth=0.8, candle_width=0.6),
    )

    # Add horizontal lines for Fibonacci levels
    fib_levels = {
        '0%': df['Close'].max(),
        '23.6%': df['Close'].max() - (df['Close'].max() - df['Close'].min()) * 0.236,
        '38.2%': df['Close'].max() - (df['Close'].max() - df['Close'].min()) * 0.382,
        '50%': df['Close'].max() - (df['Close'].max() - df['Close'].min()) * 0.5,
        '61.8%': df['Close'].max() - (df['Close'].max() - df['Close'].min()) * 0.618,
        '100%': df['Close'].min()
    }
    
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
    for i, (level, price) in enumerate(fib_levels.items()):
        axlist[0].axhline(y=price, color=colors[i], linestyle='--', alpha=0.5, linewidth=0.7)
        axlist[0].text(df.index[-1], price, f' {level} ({price:.2f})', 
                      verticalalignment='center', color=colors[i], fontsize=8)

    # Price panel customization
    axlist[0].set_ylabel('Price', fontsize=10)
    axlist[0].grid(True, linestyle=':', alpha=0.5)
    
    # MACD panel customization
    axlist[1].set_ylabel('MACD', fontsize=8)
    axlist[1].grid(True, linestyle=':', alpha=0.3)
    
    # RSI panel customization
    axlist[2].set_ylabel('RSI', fontsize=8)
    axlist[2].axhline(y=70, color='red', linestyle='--', alpha=0.5, linewidth=0.7)
    axlist[2].axhline(y=30, color='green', linestyle='--', alpha=0.5, linewidth=0.7)
    axlist[2].grid(True, linestyle=':', alpha=0.3)
    
    # Stochastic panel customization
    axlist[3].set_ylabel('Stoch', fontsize=8)
    axlist[3].axhline(y=80, color='red', linestyle='--', alpha=0.5, linewidth=0.7)
    axlist[3].axhline(y=20, color='green', linestyle='--', alpha=0.5, linewidth=0.7)
    axlist[3].grid(True, linestyle=':', alpha=0.3)
    
    # OBV panel customization
    axlist[4].set_ylabel('OBV', fontsize=8)
    axlist[4].grid(True, linestyle=':', alpha=0.3)
    
    # Volume panel customization
    axlist[5].set_ylabel('Volume', fontsize=8)
    
    # Add Ichimoku cloud
    axlist[0].fill_between(df.index, df['Senkou_span_a'], df['Senkou_span_b'], 
                          where=df['Senkou_span_a'] >= df['Senkou_span_b'],
                          facecolor='lightgreen', alpha=0.3, interpolate=True)
    axlist[0].fill_between(df.index, df['Senkou_span_a'], df['Senkou_span_b'], 
                          where=df['Senkou_span_a'] < df['Senkou_span_b'],
                          facecolor='lightcoral', alpha=0.3, interpolate=True)
    
    # Add legends
    handles, labels = axlist[0].get_legend_handles_labels()
    if handles:
        legend = axlist[0].legend(
            handles=handles,
            loc='upper left',
            bbox_to_anchor=(0.02, 0.98),
            frameon=True,
            framealpha=0.9,
            facecolor='white',
            edgecolor='gray',
            fontsize=8,
            ncol=3
        )
        for text in legend.get_texts():
            text.set_color('black')
    
    plt.show()