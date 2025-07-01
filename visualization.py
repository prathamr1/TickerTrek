"""
Simple chart creation functions for TickerTrek.
Provides essential chart types for stock data visualization.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from typing import Dict
import warnings

warnings.filterwarnings('ignore')

# Set clean style
plt.style.use('default')


def render_main_chart(data: pd.DataFrame, ticker) -> plt.Figure:
    """Create simple price line chart."""
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(data.index, data['Close'], color='#1f77b4', linewidth=2)
    ax.set_title(f'{ticker} - Stock Price', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price ($)')
    ax.grid(True, alpha=0.3)

    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def render_volume_chart(data: pd.DataFrame, ticker) -> plt.Figure:
    """Create simple volume bar chart."""
    fig, ax = plt.subplots(figsize=(12, 4))

    ax.bar(data.index, data['Volume'], color='#ff7f0e', alpha=0.7)
    ax.set_title(f'{ticker} - Trading Volume', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Volume')
    ax.grid(True, alpha=0.3)

    # Format volume numbers
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x / 1e6:.1f}M'))

    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def create_price_with_moving_averages(data: pd.DataFrame, ticker: str,
                                      ma_short: int = 20, ma_long: int = 50) -> plt.Figure:
    """Create price chart with moving averages."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Price line
    ax.plot(data.index, data['Close'], color='#1f77b4', linewidth=2, label='Close Price')

    # Moving averages
    if len(data) >= ma_short:
        ma_short_data = data['Close'].rolling(window=ma_short).mean()
        ax.plot(data.index, ma_short_data, color='#ff7f0e', linewidth=1,
                label=f'MA {ma_short}')

    if len(data) >= ma_long:
        ma_long_data = data['Close'].rolling(window=ma_long).mean()
        ax.plot(data.index, ma_long_data, color='#2ca02c', linewidth=1,
                label=f'MA {ma_long}')

    ax.set_title(f'{ticker} - Price with Moving Averages', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price ($)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def render_returns_chart(data: pd.DataFrame, ticker: str) -> plt.Figure:
    """Create daily returns chart."""
    returns = data['Close'].pct_change().dropna()

    fig, ax = plt.subplots(figsize=(12, 6))

    # Color positive and negative returns differently
    colors = ['green' if x > 0 else 'red' for x in returns]
    ax.bar(returns.index, returns, color=colors, alpha=0.7)

    ax.set_title(f'{ticker} - Daily Returns', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Daily Return (%)')
    ax.grid(True, alpha=0.3)

    # Format y-axis as percentage
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x * 100:.1f}%'))

    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def render_comparison_chart(data_dict: Dict[str, pd.DataFrame],
                            title: str = "Stock Comparison") -> plt.Figure:
    """Create simple comparison chart for multiple stocks."""
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    for i, (ticker, data) in enumerate(data_dict.items()):
        # Normalize to percentage change from first value
        normalized = (data['Close'] / data['Close'].iloc[0] - 1) * 100
        color = colors[i % len(colors)]
        ax.plot(data.index, normalized, color=color, linewidth=2, label=ticker)

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Percentage Change (%)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def render_candlestick_chart(data: pd.DataFrame, ticker: str) -> plt.Figure:
    """Create simple candlestick chart."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Simple candlestick representation using lines
    for i, (date, row) in enumerate(data.iterrows()):
        # High-Low line
        ax.plot([date, date], [row['Low'], row['High']],
                color='black', linewidth=1)

        # Body color based on close vs open
        color = 'green' if row['Close'] >= row['Open'] else 'red'

        # Body (Open to Close)
        ax.plot([date, date], [row['Open'], row['Close']],
                color=color, linewidth=4, alpha=0.8)

    ax.set_title(f'{ticker} - Candlestick Chart', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price ($)')
    ax.grid(True, alpha=0.3)

    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def render_rsi_chart(data: pd.DataFrame, ticker, period: int = 14) -> plt.Figure:
    """Create RSI chart."""
    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    fig, ax = plt.subplots(figsize=(12, 4))

    ax.plot(data.index, rsi, color='#1f77b4', linewidth=2)
    ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
    ax.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
    ax.fill_between(data.index, 30, 70, alpha=0.1, color='gray')

    ax.set_title(f'{ticker} - RSI ({period} period)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('RSI')
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def render_histogram(data: pd.Series, title: str = "Histogram",
                     bins: int = 30, color: str = '#1f77b4') -> plt.Figure:
    """Create simple histogram."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(data.dropna(), bins=bins, color=color, alpha=0.7, edgecolor='black')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def render_scatter_plot(x_data: pd.Series, y_data: pd.Series,
                        title: str = "Scatter Plot",
                        x_label: str = "X", y_label: str = "Y") -> plt.Figure:
    """Create simple scatter plot."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(x_data, y_data, alpha=0.6, color='#1f77b4')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig