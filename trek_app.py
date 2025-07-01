"""
TickerTrek - Main Streamlit Application
main module v1.0.0
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath('C:\\Users\prath\Desktop\TickerTrek2')))

from config import PAGE_CONFIG, CUSTOM_CSS
from sidebar import render_sidebar
from metrics import render_key_metrics, render_real_time_price
from data_table import render_recent_data, render_statistics
from visualization import render_main_chart, render_volume_chart, render_rsi_chart
from data_etl import StockDataManage


def main():
    """Main application function"""
    st.set_page_config(**PAGE_CONFIG)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.markdown(
        '<h1 class="main-header">📈 TickerTrek - Stock Price Tracker</h1>',
        unsafe_allow_html=True
    )
    st.markdown("**Real-time stock data, historical trends, and advanced visualizations**")

    if 'stock_symbol' not in st.session_state:
        st.session_state.stock_symbol = 'AAPL'

    stock_symbol, period, chart_options = render_sidebar()  # Render sidebar and get user inputs
    if stock_symbol:  # Update session state
        st.session_state.stock_symbol = stock_symbol

    if st.session_state.stock_symbol:
        data_manager = StockDataManage()

        with st.spinner(f"Fetching data for {st.session_state.stock_symbol}..."):  # Fetch data with loading spinner
            stock_data = data_manager.get_stock_data(st.session_state.stock_symbol, period)

        if stock_data.is_valid():
            render_real_time_price(stock_data)
            render_key_metrics(stock_data)
            render_main_chart(stock_data.data, chart_options)

            if chart_options.get('show_volume', False):
                render_volume_chart(stock_data.data,chart_options)

            if chart_options.get('show_rsi', False):
                render_rsi_chart(stock_data.data,chart_options)

            render_statistics(stock_data)  # Statistics and analysis
            render_recent_data(stock_data)
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
    """Render company information section"""
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
            import pandas as pd
            info_df = pd.DataFrame(info_data, columns=['Attribute', 'Value'])
            st.dataframe(info_df, hide_index=True)


def render_footer():
    """Render application footer"""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p> TickerTrek™️- Built with Streamlit & Yahoo Finance API , by <a href="https://github/prathamr1/">Prathamesh R</a>></p>
        <p> This is for educational purposes only. Not financial advice.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()