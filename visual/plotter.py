import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import yfinance as yf

from curl_cffi import requests

session = requests.Session(impersonate="chrome")

def plot_technical_chart(df, ticker):
    mc = mpf.make_marketcolors(up='g', down='r', edge='inherit', wick='inherit', volume='in')
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', y_on_right=True)  # Changed y_on_right to True

    ap = [
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
        figsize=(16, 10),
        returnfig=True,
        panel_ratios=(4, 1),  # hanya panel harga dan volume
        scale_padding={'left': 0.4, 'top': 1.1, 'right': 2.1, 'bottom': 0.6},
        xrotation=0,
        datetime_format='%d %b %Y',
        tight_layout=True,
        update_width_config=dict(candle_linewidth=0.8, candle_width=0.6),
    )

    ax = axlist[0]
    ax.fill_between(df.index, df['Senkou_span_a'], df['Senkou_span_b'],
                    where=df['Senkou_span_a'] >= df['Senkou_span_b'],
                    facecolor='lightgreen', alpha=0.3, interpolate=True)
    ax.fill_between(df.index, df['Senkou_span_a'], df['Senkou_span_b'],
                    where=df['Senkou_span_a'] < df['Senkou_span_b'],
                    facecolor='lightcoral', alpha=0.3, interpolate=True)
    
    last_close_price = df['Close'].iloc[-1]
    last_volume = df['Volume'].iloc[-1]

    ax.axhline(y=last_close_price, color='black', linestyle='--', linewidth=1)
    ax.annotate(f'{last_close_price:.2f}',
                xy=(0, last_close_price),
                xytext=(10, 0),  
                textcoords='offset points',
                va='center',
                ha='right',
                fontsize=8,
                backgroundcolor='white',
                color='black',
                bbox=dict(boxstyle="round,pad=0.2", edgecolor='gray', facecolor='white', alpha=0.8),
                arrowprops=dict(arrowstyle='-', color='black', linestyle='--'))

    ax_vol = axlist[2] 
    ax_vol.axhline(y=last_volume, color='black', linestyle='--', linewidth=1)
    ax_vol.annotate(f'{last_volume:.0f}',
                    xy=(0, last_volume),
                    xytext=(10, 0),
                    textcoords='offset points',
                    va='center',
                    ha='right',
                    fontsize=8,
                    backgroundcolor='white',
                    color='black',
                    bbox=dict(boxstyle="round,pad=0.2", edgecolor='gray', facecolor='white', alpha=0.8),
                    arrowprops=dict(arrowstyle='-', color='black', linestyle='--'))

    handles, labels = ax.get_legend_handles_labels()
    if handles:
        legend = ax.legend(
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