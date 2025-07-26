"""
Metrics Display Components Module
Handles the display of key financial metrics and real-time price information
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from datetime import datetime


from data_etl import StockData
from utils import format_number, format_percentage, format_currency

def render_real_time_price(stock_data: StockData):

    st.subheader(f"⚪ {stock_data.symbol}")

    # Get company name if available
    company_name = stock_data.info.get('longName', stock_data.symbol)
    if company_name != stock_data.symbol:
        st.write(f"**{company_name}**")
    now = datetime.now()
    fdate = now.strftime("%Y-%m-%d - %H:%M")
    st.write(f"🕐 Current Date & Time {fdate}")
    # Create columns for price display
    col1, col2 = st.columns([2, 2])

    with col1:
        current_price = stock_data.current_price
        if current_price:
            st.metric(
                label="Current Price",
                value=format_currency(current_price),
                delta=format_currency(current_price),
                delta_color="off",
                border=True
            )

    with col2:
        price_change_data = stock_data.get_price_change()
        price_change = price_change_data["Price Change"]
        change_percent = price_change_data["Change %"]
        st.metric(
            label="Price Change",
            value=format_currency(price_change),
            delta=format_percentage(change_percent),
            border=True
            )

def render_key_metrics(stock_data: StockData):

    st.subheader("💲Key Financial Metrics")

    # Get financial metrics
    metrics_data = stock_data.get_basic_stats()

    if not metrics_data:
        st.warning("Financial metrics data not available")
        return

    # Create metric columns
    col1, col2, col3, col4 = st.columns(4)

    metrics_layout = [
        ("Market Cap", "marketCap", col1),
        ("P/E Ratio", "trailingPE", col2),
        ("Earnings Per Share", "trailingEps", col3),
        ("Dividend Yield", "dividendYield", col4)
    ]

    for label, key, column in metrics_layout:
        with column:
            value = metrics_data.get(key)
            if value is not None:
                if key == "marketCap":
                    formatted_value = format_number(value)
                elif key == "dividendYield":
                    formatted_value = value
                elif key == "trailingEps":
                    formatted_value = format_currency(value)
                else:
                    formatted_value = format_number(value)

                st.metric(label=label, value=formatted_value)
            else:
                st.metric(label=label, value="N/A")


def render_trading_metrics(stock_data: StockData):
    """
    Render trading-related metrics

    Args:
        stock_data: StockData object containing stock information
    """
    st.subheader("📊 Trading Metrics")

    trading_data = stock_data.get_returns_analysis()

    if not trading_data:
        st.warning("Trading metrics data not available")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        volume = trading_data.get('volume')
        if volume:
            st.metric(
                label="Volume",
                value=format_number(volume)
            )

        avg_volume = trading_data.get('averageVolume')
        if avg_volume:
            st.metric(
                label="Avg Volume (10d)",
                value=format_number(avg_volume)
            )

    with col2:
        day_high = trading_data.get('dayHigh')
        day_low = trading_data.get('dayLow')
        if day_high and day_low:
            st.metric(
                label="Day High",
                value=format_currency(day_high)
            )
            st.metric(
                label="Day Low",
                value=format_currency(day_low)
            )

    with col3:
        week_52_high = trading_data.get('fiftyTwoWeekHigh')
        week_52_low = trading_data.get('fiftyTwoWeekLow')
        if week_52_high and week_52_low:
            st.metric(
                label="52W High",
                value=format_currency(week_52_high)
            )
            st.metric(
                label="52W Low",
                value=format_currency(week_52_low)
            )

def render_metrics_summary(stock_data: StockData):
    """
    Render a comprehensive metrics summary

    Args:
        stock_data: StockData object containing stock information
    """
    st.header(f"📊 {stock_data.symbol} - Financial Overview")

    # Real-time price section
    render_real_time_price(stock_data)

    st.divider()

    # Key metrics in tabs
    tab1, tab2 = st.tabs(["Key Metrics", "Trading Data"])

    with tab1:
        render_key_metrics(stock_data)

    with tab2:
        render_trading_metrics(stock_data)


def render_metrics_cards(metrics_dict: Dict[str, Any], title: str = "Metrics"):
    """
    Render metrics in card format

    Args:
        metrics_dict: Dictionary containing metric names and values
        title: Title for the metrics section
    """
    st.subheader(title)

    # Calculate number of columns based on metrics count
    num_metrics = len(metrics_dict)
    num_cols = min(4, num_metrics)

    if num_cols == 0:
        st.warning("No metrics data available")
        return

    cols = st.columns(num_cols)

    for idx, (metric_name, metric_value) in enumerate(metrics_dict.items()):
        col_idx = idx % num_cols
        with cols[col_idx]:
            if metric_value is not None:
                # Format value based on metric type
                if isinstance(metric_value, (int, float)):
                    if metric_name.lower() in ['volume', 'marketcap', 'shares']:
                        formatted_value = format_number(metric_value)
                    elif 'percent' in metric_name.lower() or 'yield' in metric_name.lower():
                        formatted_value = format_percentage(metric_value)
                    elif 'price' in metric_name.lower() or 'eps' in metric_name.lower():
                        formatted_value = format_currency(metric_value)
                    else:
                        formatted_value = format_number(metric_value)
                else:
                    formatted_value = str(metric_value)

                st.metric(label=metric_name, value=formatted_value)
            else:
                st.metric(label=metric_name, value="N/A")


def render_comparison_metrics(stock_data_list: list, metric_keys: list):
    """
    Render comparison metrics for multiple stocks

    Args:
        stock_data_list: List of StockData objects to compare
        metric_keys: List of metric keys to compare
    """
    if not stock_data_list:
        st.warning("No stock data provided for comparison")
        return

    st.subheader("📊 Stock Comparison")

    # Create comparison dataframe
    comparison_data = []

    for stock_data in stock_data_list:
        metrics = stock_data.get_key_metrics()
        row_data = {'Symbol': stock_data.symbol}

        for key in metric_keys:
            value = metrics.get(key) if metrics else None
            row_data[key] = value

        comparison_data.append(row_data)

    if comparison_data:
        df = pd.DataFrame(comparison_data)

        # Format the dataframe for display
        formatted_df = df.copy()
        for col in df.columns:
            if col != 'Symbol':
                formatted_df[col] = df[col].apply(
                    lambda x: format_number(x) if pd.notna(x) else "N/A"
                )

        st.dataframe(formatted_df, use_container_width=True)
    else:
        st.warning("No comparison data available")


# Error handling wrapper
def safe_render_metrics(render_func, *args, **kwargs):
    """
    Safely execute metric rendering functions with error handling

    Args:
        render_func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
    """
    try:
        render_func(*args, **kwargs)
    except Exception as e:
        st.error(f"Error rendering metrics: {str(e)}")
        st.write("Please check your data source and try again.")