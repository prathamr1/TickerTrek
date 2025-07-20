"""
TickerTrek - Main Streamlit Application
main module v1.0.0
"""

import streamlit as st
import sys
import os
import pandas as pd
from streamlit_autorefresh import st_autorefresh

sys.path.append(os.path.dirname(os.path.abspath('C:\\Users\prath\Desktop\TickerTrek2')))

from config import PAGE_CONFIG, CUSTOM_CSS
from sidebar import render_sidebar
from metrics import render_key_metrics, render_real_time_price
from data_table import render_recent_data, render_statistics
from data_etl import StockDataManage
from visualization import plot_candlestick

def main():
    """Main application function"""
    st.set_page_config(**PAGE_CONFIG)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        '<h1 class="main-header">💲TickerTrek - Stock Price Analytics</h1>',
        unsafe_allow_html=True
    )
    st.markdown("**🔸Real-time stock data, Financial Metrics, Statistical Analytics and Historical trends**")

    if 'stock_symbol' not in st.session_state:
        st.session_state.stock_symbol = 'NVDA'
    if 'period' not in st.session_state:
        st.session_state.period = '1y'
    stock_symbol, period = render_sidebar()  # Render sidebar and get user inputs

    if stock_symbol:  # Update session state
        st.session_state.stock_symbol = stock_symbol
    if period:
        st.session_state.period = period

    if st.session_state.period == "live":
        st_autorefresh(interval=10_000, key="live_refresh")

    if st.session_state.stock_symbol:
        data_manager = StockDataManage()

        with st.spinner(f"Fetching data for {st.session_state.stock_symbol}..."):  # Fetch data with loading spinner
            stock_data = data_manager.get_stock_data(st.session_state.stock_symbol, period)
        st.markdown("---")
        render_real_time_price(stock_data)
        st.markdown("---")

        st.plotly_chart(plot_candlestick(st.session_state.stock_symbol,st.session_state.period))
        st.markdown("---")
        render_key_metrics(stock_data)
        st.markdown("---")

        render_statistics(stock_data)  # Statistics and analysis
        render_recent_data(stock_data)
        st.markdown("---")
        if stock_data.info:
            render_company_info(stock_data)

        else:
            st.error(f"❌ Could not fetch data for symbol: {st.session_state.stock_symbol}")
            st.info("Please check if the stock symbol is correct and try again.")

    else:
        st.info("👈 Please enter a stock symbol in the sidebar to get started!")

    # Footer
    render_footer()


def render_company_info(stock_data):
    if not stock_data.info:
        return

    st.subheader("🏢 Company Information")
    col1, col2 = st.columns(2)

    with col1:
        if 'longBusinessSummary' in stock_data.info:
            st.write("**Business Summary:**")
            summary = stock_data.info['longBusinessSummary']
            if len(summary) > 500:
                summary = summary[:500] + "..."
            st.write(summary)

    with col2:
        st.write("**Key Information:**")
        info_data = []

        info_fields = {
            'sector': 'Sector',
            'industry': 'Industry',
            'country': 'Country',
            'employees': 'Employees',
            'website': 'Website'
        }

        for key, label in info_fields.items():
            if key in stock_data.info:
                value = stock_data.info[key]
                if key == 'employees':
                    value = f"{value:,}"
                info_data.append([label, value])

        if info_data:
            info_df = pd.DataFrame(info_data, columns=['Attribute', 'Value'])
            st.dataframe(info_df, hide_index=True)


def render_footer():

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888;'>
        <p> TickerTrek™️- Built with Streamlit & Yahoo Finance API , by <a href="https://github.com/prathamr1/">Prathamesh R</a>></p>
        <p> Stock Price is subject to change with different currencies </p>
        <p> This is for educational purposes only. Not financial advice.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

if __name__ == "__main__":
    main()