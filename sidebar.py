import streamlit as st
from typing import Tuple, Dict
import sys
import os

from scipy.constants import minute

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('C:\Users\prath\Desktop\TickerTrek2'))))

from config.settings import POPULAR_STOCKS, PERIOS_OPTIONS


def render_sidebar() -> Tuple[str, str, Dict]:
    # returns Tuple [stock_symbol, period, chart_options]
    st.sidebar.header("Stock Selection")
    stock_symbol = render_stock_input()

    selected_quick_stock = render_quick_select_buttons()

    if selected_quick_stock:
        stock_symbol = selected_quick_stock
    period = render_period_selection()

    chart_options = render_chart_options()
    technical_options = render_technical_indicators()
    chart_options.update(technical_options)
    render_additional_tools()

    return stock_symbol, period, chart_options


def render_stock_input() -> str:
    col1, col2 = st.sidebar.columns([3, 1])

    with col1:
        stock_symbol = st.text_input(
            "Enter Stock Symbol:",
            value=st.session_state.get('stock_symbol', 'NVDA'),
            placeholder="e.g. : AAPL, GOOGL, TSLA, MSFT",
            help="Enter a valid stock ticker symbol"
        )
    with col2:
        if st.button("Refresh", "Clear Cache and refresh the data"):
            st.cache_data.clear()
            st.success("Cache Cleared")
        return stock_symbol.upper().strip() if stock_symbol else ""


def render_quick_select_buttons() -> str:
    st.sidebar.write("**Quicl Select Popular Stocks**")

    cols = st.sidebar.columns(2)
    for i, (name, symbol) in enumerate(POPULAR_STOCKS.items()):
        col = cols[i % 2]
        button_text = f"{symbol}\n{name}"
        if col.button(
                button_text,
                key=f"quick_{symbol}",
                help=f"Select {name} ({symbol})",
                use_container_width=True
        ):
            st.session_state.stock_symbol = symbol
            st.rerun()
    return ""


def render_period_selections() -> str:
    st.sidebar.header("Time Period")
    selected_period = st.sidebar.selectbox(
        "Select Time Period:",
        list(PERIOD_OPTIONS.keys()),
        index=5,
        help="CHoose the Time range for historical data"
    )

    period_info = {
        "1 Day": "Intraday data with 1-minute intervals",
        "5 Days": "Recent week's trading data",
        "1 Month": "Last month's daily data",
        "3 Months": "Quarterly performance data",
        "6 Months": "Half-year trend analysis",
        "1 Year": "Annual performance overview",
        "2 Years": "Two-year trend analysis",
        "5 Years": "Long-term performance data"
    }
    if selected_period in period_info:
        st.sidebar.caption(period_info[selected_period])
    return PERIOD_OPTIONS[selected_period]


def render_chart_options() -> Dict:
    st.sidebar.header("Chart Options")
    chart_type = st.sidebar.selectbox(
        'Chart Type:',
        ["CandleStick", "LineChart", "Area Chart"],
        help="Choose how to display stock price data"
    )

    show_volume = st.sidebar.checkbox(
        "Show Volume Chart",
        value=True,
        help="Display trading volume below price chart"
    )
    show_ma = st.sidebar.checkbox(
        "Show Moving Averages",
        value=True,
        help="Add 20 and 50 day moving averages"
    )
    colour_scheme = st.sidebar.selectbox(
        "Color Scheme:",
        ["Default", "Dark", "ColourFul"],
        help="Choose chart colour theme"
    )

    return {
        'chart_type': chart_type,
        'show_volume': show_ma,
        'show_ma': show_ma,
        'colour scheme': colour_scheme
    }


def render_technical_indicators() -> Dict:
    st.sidebar.header("Technical Indicators")
    show_rsi = st.sidebar.checkbox(
        "Show Relative Strength Index (RSI)",
        help="Momentum oscillator (0-100)"
    )
    show_bollinger = st.sidebar.checkbox(
        "Show Bollinger Bands",
        help="Volatility bands around moving averages"
    )
    show_macd = st.sidebar.checkbox(
        "Show MACD",
        help="Moving Average Convergence and Divergence"
    )

    # with st.sidebar.expander("Advanced Indicators")
    # Advanced Indicators: Stochastic,williams,cci yet to be integrated

    return {
        'show_rsi': show_rsi,
        'show_bollinger': show_bollinger,
        'show_macd': show_macd
    }


def render_additional_tools():
    st.sidebar.header("Additional tools")

    with st.sidebar.expander("Export Options"):
        st.write("**Available Formats:**")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("CSV", use_container_width=True):
                st.session_state.export_format = 'csv'

        with col2:
            if st.button("Excel", use_container_width=True):
                st.session_state.export_format = 'excel'

    with st.sidebar.expander("Price Alert"):
        alert_enabled = st.checkbox("Enable Price Alerts")
        if alert_enabled:
            alert_type = st.selectbox(
                "Alert Type:",
                ["Price Above", "Price Below", "% change"]
            )

            alert_value = st.number_input(
                "Alert Value:",
                min_value=0.0,
                help="Set limit for alert"
            )
            if st.button("Set Alert"):
                st.success(f"Alert Set:{alert_type}{alert_value}")

    with st.sidebar.expander("App settings"):
        auto_refresh = st.checkbox(
            "Auto-refresh the data",
            help="Automatically refresh data every 2 minutes"
        )
        if auto_refresh:
            refresh_interval = st.slider(
                "Refresh interval(minutes):",
                min_value=1,
                max_value=60,
                value=2
            )
            st.session_state.refresh_interval = refresh_interval

        theme = st.selectbox(
            "App Theme:",
            ["light", "Dark", "Auto"]
        )
        st.session_state.theme = theme

    with st.sidebar.expander("About"):
        st.write("""
        **TickerTrek™️ is a comprehensive stock analysis tool built with:
        - **Real-time data** from Yahoo Finance
        - **Technical indicators** for analysis
        - **Interactive charts** with Plotly
        - **Statistical analysis** tools

        **GitHub:** [TickerTrek](https://github/prathamr1/TickerTrek2)
        **Connect with me:**[LinkedIn](https://www.linkedin.com/in/prathamesh-renuse/)
        **Data Source:** [Yahoo Finance API](https://finance.yahoo.com/)

        **For Educational Purposes only, Use with caution and
         cross check before taking any financial decision**
        """)

    if st.button("Help & Support"):
        st.info("""
                **How to use :-**
                1. Enter a stock symbol(ticker name) or use quick select
                2. Choose time period and chart options
                3. Enable technical indicators as per your interests
                4. Analyze the data and charts

                **Tricks and Tips:-**
                    -To select a stock from different markets use : "TICKERNAME.STOCK_EXCHANGE_SYMBOL"
                         e.g. : Selecting TATAMOTORS from NSE(India) , enter **TATAMOTORS.NS**

                    -Use UPPERCASE symbols (such as AAPL,NVDA,etx.)
                    -Try different time periods for various insights
                    -Enable multiple indicators for enhanced analytics
                """)

# def render_market_summary():
#    st.sidebar.header("Market Summary")
# incomplete function , yet to be developed
