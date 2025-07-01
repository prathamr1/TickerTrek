"""
Data table components: Handles display of the tabular data
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils import format_number,calculate_percentage_change

def render_recent_data(stock_data,num_rows=10):
    if stock_data.data is None or stock_data.data.empty:
        st.error("No data available to display")
        return ""

    st.subheader("Recent Data")
    recent_data = stock_data.data.tail(num_rows).copy()
    recent_data = recent_data.sort_index(ascending=False)

    display_d = recent_data.copy()

    numeric_columns= ['Open','High','Low','Close','Adj Close']
    for col in numeric_columns:
        if col in display_d.columns:
            display_d[col] = display_d[col].apply(lambda x: f'{x:.2f}')

    if 'Volume' in display_d.columns:
        display_d['Volume'] = display_d['Volume'].apply(format_number)


    if len(recent_data) > 1:
        daily_changes =[]
        for i in range(len(recent_data)):
            if i == len(recent_data)-1:
                daily_changes.append("N/A")
            else:
                current_close = recent_data.iloc[i]['Close']
                previous_close = recent_data.iloc[i+1]['Close']
                change= calculate_percentage_change(previous_close,current_close)

                color="🟢" if change>0 else "🔴" if change<0 else "😶"
                daily_changes.append(f"{color} {change:+.2f}%")

        display_d['Daily Change'] = daily_changes

    display_d.reset_index(inplace=True)
    display_d['Data'] = display_d['Date'].dt.strftime('%Y-%m-%d')

    st.dataframe(
        display_d,
        use_container_width=True,
        hide_index=True
    )


    csv_data=recent_data.to_csv()
    st.download_button(
        label="Download Recent stock data in .csv",
        data=csv_data,
        file_name=f"{stock_data.symbol}_recent_data.csv",
        mime="text/csv"
    )


def render_statistics(stock_data):
    if stock_data.data is None or stock_data.data.empty:
        st.error("No data available for statistical analysis")
        return ""

    st.subheader("Statistical Data Analysis")
    data =stock_data.data['Close']
    stats_data= {
        'Metric': [
            'Current Price',
            'Mean Price',
            'Median Price',
            'Standard Deviation',
            'Minimum Price',
            'Maximum Price',
            '52-Week High',
            '52-Week Low',
            'Volatility (30-day)',
            'Average Volume'
        ],

        'Value':[
            f"{data.iloc[-1]:.2f}",
            f"{data.mean():.2f}",
            f"{data.median():.2f}",
            f"{data.std():.2f}",
            f"{data.min():.2f}",
            f"{data.max():.2f}",
            f"{data.tail(252).max():.2f}" if len(data) >= 252 else f"{data.max():.2f}",
            f"{data.tail(252).min():.2f}" if len(data) >= 252 else f"{data.min():.2f}",
            f"{calculate_volatility(data):.2f}",
            format_number(stock_data.data['Volume'].mean())
        ]
    }

    returns = data.pct_change().dropna()
    if len(returns) > 0 :
        stats_data['Metric'].extend(
            ['Sharpe Ratio(approx)','Max Drawdown','Positive days%'])
        stats_data['Value'].extend([
            f"{calculate_sharpe_ratio(returns):.2f}",
            f"{calculate_max_drawdown(data):.2f}%",
            f"{(returns>0).mean()*100:.1f}%"
            ])

        stats_df=pd.DataFrame(stats_data)
        col1,col2=st.columns(2)
        midpoint=len(stats_df) //2

        with col1:
            st.dataframe(
                stats_df.iloc[:midpoint],
                use_container_width=True,
                hide_index=True
            )

        with col2:
            st.dataframe(
                stats_df.iloc[midpoint:],
                use_container_width=True,
                hide_index=True
            )

def render_performance_summary(stock_data):
    st.subheader("Performance summary")
    data=stock_data.data['Close']
    current_price= data.iloc[-1]

    periods={
        '1 Week': 7,
        '1 Month': 30,
        '3 Months': 90,
        '6 Months': 180,
        '1 Year': 252
    }
    performance_data=[]
    for period_name,days in periods.items():
        if len(data) > days:
            past_price = data.iloc[-(days+1)]
            change = calculate_percentage_change(past_price,current_price)

            if change > 0:
                emoji = "🟢"
                #color = "success"
            elif change < 0:
                emoji = "🔴"
                #color = "error"
            else:
                emoji = "⚪"

            performance_data.append({
                'Period': period_name,
                'Return': f"{emoji} {change:+.2f}%",
                'Start Price': f"${past_price:.2f}",
                'Current Price': f"${current_price:.2f}"
            })

    if performance_data:
        perf_df=pd.DataFrame(performance_data)
        st.dataframe(
            perf_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Insufficient Data for performance analytics")


def calculate_volatility(prices,window=30):
    if not isinstance(prices,pd.Series):
        prices = pd.Series(prices)

    if len(prices) < window:
        window = len(prices)

    returns = prices.pct_change().dropna()

    if len(returns) < window:
        return 0

    volatility= returns.std()*np.sqrt(252)
    return volatility



def calculate_sharpe_ratio(returns,risk_free_return=0.02):
    if len(returns)==0 or returns.std()==0:
        return 0

    excess_returns= returns.mean()*252-risk_free_return
    volatility =returns.std()*np.sqrt(252)
    return excess_returns/volatility

def calculate_max_drawdown(prices):
    if len(prices) < 2:
        return 0
    peak=prices.expanding().max()
    drawdown=(prices-peak)/peak*100
    return drawdown.min()
