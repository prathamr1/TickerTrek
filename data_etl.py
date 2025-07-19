import yfinance as yf
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any
from dataclasses import dataclass

from sidebar import render_sidebar


@dataclass()
class StockData:
    """Data to hold stock information"""

    def __init__(self, symbol: str, data: pd.DataFrame, info: Dict[str, Any], current_price: float):
        self.symbol = symbol
        self.data = data
        self.info = info
        self.current_price = current_price

    def is_valid(self) -> bool :
        return(
            self.data is not None and not self.data.empty
            and self.current_price>0
        )


    def get_price_change(self)-> Dict[str,float]:
        """Calculate price and % change"""
        if len(self.data) < 2:
            return {'Price Change':0.0,'Change %':0.0}
        try:
            prev_close = self.data['Close'].iloc[-2]
            price_change = self.current_price - prev_close
            price_change_p = (price_change/prev_close)*100
            return {'Price Change':price_change,'Change %':price_change_p}
        except (IndexError, ZeroDivisionError):
            return {'Price Change':0.0,'Change %':0.0}



    def get_basic_stats(self)->Dict[str,float]:
        if not self.is_valid():
            return{}

        #close_prices = self.data['Close']
        return {
            "marketCap": self.info.get("marketCap"),
            "trailingPE": self.info.get("trailingPE"),
            "trailingEps": self.info.get("trailingEps"),
            "dividendYield": self.info.get("dividendYield"),
        }

    def get_returns_analysis(self)->Dict[str,float]:
        if not self.is_valid() or len(self.data) < 2:
            return {}
        try:
            returns = self.data['Close'].pct_changes().dropna()

            cumulative = (1+returns).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative /running_max -1)
            max_drawdown = drawdown.min()

            sharpe_ratio = 0
            if returns.std() != 0:
                sharpe_ratio = (returns.mean() / returns.std()) * (252 ** 0.5)

            return {
                'daily_return_mean': returns.mean(),
                'daily_return_std': returns.std(),
                'sharpe_ratio': sharpe_ratio,
                'max_draw_down': max_drawdown
            }
        except Exception as e:
            st.write(f"Error while retrieving{self.data}:{str(e)}")
            return {}

class StockDataManage:

    def __init__(self):
        self.cache_ttl = 300 #5 min cache for historical data
        self.realtime_cache_ttl = 60 #1 min chace for realtime data

    @st.cache_data(ttl=300)
    def get_stock_data(_self,_symbol: str, period: str = '1y') -> StockData:
        try:
            ticker_symbol = _symbol.upper().strip()
            if not ticker_symbol:
                raise ValueError("Empty stock symbol")

            stock = yf.Ticker(ticker_symbol)
            #Live Data
            if period=="live":
                try:
                    info=stock.fast_info
                    current_price=info.get("last_price",0.0)
                except Exception as e :
                    st.error(f"Live data fetch error:  {e}")
                    return StockData(symbol=ticker_symbol, data=pd.DataFrame(),info={},current_price=0.0)
                data=pd.DataFrame([{"Live Price:":current_price,"Symbol":ticker_symbol}])
                return  StockData(symbol=ticker_symbol,data=data,info=info,current_price=current_price)

            #Historical Data
            try:
                data = stock.history(period=period)
            except (KeyError, IndexError, ValueError) as e:
                st.error(f"Error retrieving historical data: {e}")
                return StockData(symbol=ticker_symbol, data=pd.DataFrame(), info={}, current_price=0.0)

            if data.empty:
                st.warning(f"No data found for the ticker '{ticker_symbol}'")
                return StockData(symbol=ticker_symbol, data=pd.DataFrame(), info={}, current_price=0.0)

            # Safe info extraction
            try:
                info = stock.info
            except (KeyError, ValueError):
                info = {}

            # Get current price
            try:
                current_price = data["Close"].iloc[-1]
            except (KeyError, IndexError):
                current_price = 0.0

            return StockData(
                symbol=ticker_symbol,
                data=data,
                info=info,
                current_price=current_price
            )

        except ValueError as ve:
            st.error(f"Input error for symbol '{_symbol}': {ve}")
        except Exception as e:
            st.error(f"Unexpected error fetching data for '{_symbol}': {type(e).__name__} - {str(e)}")

        return StockData(symbol=_symbol, data=pd.DataFrame(), info={}, current_price=0.0)

    def get_candlestick_data(self, ticker_symbol):
        stock_data = self.get_stock_data(ticker_symbol)
        df = stock_data.data

        if 'Date' not in df.columns:
            df = df.reset_index()
        df.columns=[col.strip().capitalize() for col in df.columns]

        required_cols = ['Date', 'Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("Data is missing one or more required OHLC columns.")
        df.dropna(subset=['Open','High','Low','Close'], inplace=True)
        return df[required_cols]

    @staticmethod
    def _safe_get_info(stock) -> Dict[str, Any]:
            """Safely fetch stock info with error handling"""
            info = {}
            try:
                result = stock.info
                if isinstance(result,dict):
                    info = result
            except Exception as e:
                st.error(f"error refreshing the price for {stock}: {str(e)}")

                pass
            return info

    @st.cache_data(ttl=60)
    def get_current_price(_self,stock,historical_data : pd.DataFrame) -> float :
        try :
            real_time_data = stock.history(period='1d', interval='1m')
            if not real_time_data.empty:
                return float(real_time_data['Close'].iloc[-1])
            if not historical_data.empty:
                return float(historical_data['Close'].iloc[-1])
            return 0.0

        except (KeyError, ValueError, AttributeError):
            if not historical_data.empty:
                return float(historical_data['Close'].iloc[-1])
            return 0.

    def refresh_real_time_data(_self,symbol:str)-> Optional[float]:
        try:
            _self.get_current_price.clear()
            stock = yf.Ticker(symbol.upper())
            real_time_data = stock.history(period='1d',interval='1m')

            if not real_time_data.empty:
                return float(real_time_data['Close'].iloc[-1])

        except Exception as e:
            st.error(f"error refreshing the price for {symbol}: {str(e)}")

        return None

    @staticmethod
    def validate_symbol(symbol:str) -> bool :
        try:
            symbol = symbol.upper().strip()
            if not symbol:
                return False

            stock = yf.Ticker(symbol)
            data = stock.history(period='5d')
            return not data.empty

        except (KeyError, ValueError, AttributeError):
            return False

    @staticmethod
    def get_symbol_suggestion(self,query:str) -> list:
        common_stocks = ['AAPL','MSFT','GOOGL','TATASTEEL.NS','TATAPOWER.BS','TSLA', 'META', 'NVDA', 'NFLX']
        query_upper = query.upper()
        self.suggestions = [stock for stock in common_stocks if query_upper in stock]
        return self.suggestions[:5]
