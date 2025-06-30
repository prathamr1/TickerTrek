import yfinance as yf
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

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
    def get_price_change(self)-> Tuple[float,float]:
        """Calculate price and % change"""
        if len(self.data) < 2:
            return 0.0,0.0
        try:
            prev_close = self.data['Close'].iloc[-2]
            price_change = self.current_price - prev_close
            price_change_p = (price_change/prev_close)*100
            return price_change,price_change_p
        except (IndexError, ZeroDivisionError):
            return 0.0,0.0

    def get_basic_stats(self)->Dict[str,float]:
        if not self.is_valid():
            return{}

        close_prices = self.data['Close']
        return {
            'mean': close_prices.mean(),
            'median': close_prices.median(),
            'std': close_prices.std(),
            'min': close_prices.min(),
            'max' : close_prices.max(),
            'current': self.current_price
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

    def get_stock_data(self,symbol:str, period: str = "1y")-> StockData:
        try:
            symbol = symbol.upper().strip()
            if not symbol:
                raise ValueError("Empty stock Symbol")

            stock = yf.Ticker(symbol)

            data = stock.history(period=period)
            if data.empty:
                raise ValueError(f"Please check with symbol/ticker name or no data founf for the ticker")

            info = self._safe_get_info(stock)
            current_price = self._get_current_price(stock,data)

            return StockData(
            symbol=symbol,
            data=data,
            info=info,
            current_price=current_price
            )

        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return StockData(symbol,pd.DataFrame(),{},0.0)
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
    def _get_current_price(self,stock,historical_data : pd.DataFrame) -> float :
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

    def refresh_real_time_data(self,symbol:str)-> Optional[float]:
        try:
            self._get_current_price.clear()
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
