import plotly.graph_objects as go
from data_etl import StockDataManage
import pandas as pd

def plot_candlestick(ticker_symbol:str, period: str = '1y'):
    manager = StockDataManage()

    try:
        df = manager.get_candlestick_data(ticker_symbol,period)
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'])

        df.set_index('Date',inplace=True)

        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            increasing={'line': {'color':'green'}},
            decreasing={'line': {'color':'red'}}
        )])

        fig.update_layout(
            title=f"{ticker_symbol.upper()} CandleStick",
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False,
            template="plotly_white"
        )
        return fig

    except Exception:
        raise RuntimeError(f"Failed to render candlestick chart")