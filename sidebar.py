import streamlit as st
from typing import Tuple,Dict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('C:\Users\prath\Desktop\TickerTrek2'))))

from config.settings import POPULAR_STOCKS, PERIOS_OPTIONS

def render_sidebar()-> Tuple[str,str,Dict]:
    #returns Tuple [stock_symbol, period, chart_options]
    st.sidebar.header("Stock Selection")
    stock_symbol = render_stock_input()

    selected_quick_stock = render_quick_select_buttons()

    if selected_quick_stock:
        stock_symbol=selected_quick_stock
    period = render_period_selection()

    chart_options = render_chart_options()
    technical_options=render_technical_indicators()
    chart_options.update(technical_options)
    render_additional_tools()

    return stock_symbol,period,chart_options

def render_stock_input()->str:
    col1,col2=st.sidebar.columns([3,1])

    with col1:
        stock_symbol = st.text_input(
            "Enter Stock Symbol:",
            value=st.session_state.get('stock_symbol','NVDA'),
            placeholder="e.g. : AAPL, GOOGL, TSLA, MSFT",
            help="Enter a valid stock ticker symbol"
        )
    with col2:
        if st.button("Refresh","Clear Cache and refresh the data"):
            st.cache_data.clear()
            st.success("Cache Cleared")
        return stock_symbol.upper().strip() if stock_symbol else ""


def render_quick_select_buttons()->str:
    st.sidebar.write("**Quicl Select Popular Stocks**")

    cols = st.sidebar.columns(2)
    for i, (name,symbol) in enumerate(POPULAR_STOCKS.items()):
        col=cols[i%2]
        button_text= f"{symbol}\n{name}"
        if col.button(
            button_text,
            key=f"quick_{symbol}",
            help=f"Select {name} ({symbol})",
            use_container_width=True
        ):
            st.session_state.stock_symbol=symbol
            st.rerun()
    return ""

def render_period_selections()->str:
    st.sidebar.header("Time Period")
    selected_period = st.sidebar.selectbox(
        "Select Time Period:",
        list(PERIOD_OPTIONS.keys()),
        index=5,
        help="CHoose the Time range for historical data"
    )

    period_info= {
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


def render_chart_options()->Dict:
    st.sidebar.header("Chart Options")
    chart_type= st.sidebar.selectbox(
        'Chart Type:',
        ["CandleStick","LineChart","Area Chart"],
        help="Choose how to display stock price data"
    )

    show_volume=st.sidebar.checkbox(
        "Show Volume Chart",
        value=True,
        help="Display trading volume below price chart"
    )
