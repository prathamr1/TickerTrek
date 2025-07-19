"""
Utility helper function
"""
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st


def format_number(num): #returns formatted string number T,M,K,B
    if pd.isna(num) or num==0:
        return '0'
    num=float(num)

    if abs(num)>=1e12:
        return f"{num/1e12:.1f}T"
    elif abs(num)>=1e9:
        return f"{num/1e9:1f}B"
    elif abs(num)>=1e6:
        return f"{num/1e6:1f}M"
    elif abs(num)>=1e3:
        return f"{num/1e3:1f}K"
    else:
        return f"{num:.0f}"


def format_currency(amount): #Returns formated percentage string
    try:
        amount = float(amount)
        return f"{amount:,.2f}"
    except ValueError:
        return f"{amount}"


def format_percentage(val,decimals=2):
    try:
        val = float(val)
        return f"{val:.{decimals}f}%"
    except ValueError:
        print(f"Invalid value for percentage:{val}")
        return "N/A"


def calculate_percentage_change(old_value,new_value):
    if pd.isna(old_value) or pd.isna(new_value) or old_value==0:
        return 0
    return ((new_value-old_value)/old_value) *100


def get_color_for_change(change_value):
    if change_value >0:
        return "success"
    elif change_value<0:
        return "error"
    else:
        return "info"


def validate_stock_symbol(symbol):
    if not symbol:
        return False, ""

    cleaned = symbol.strip().upper()

    if len(cleaned) < 1 or len(cleaned) > 10:
        return False, cleaned

    if not all(c.isalnum() or c in '.-' for c in cleaned):
        return False, cleaned

    return True, cleaned


def calculate_ma(data,window):
    return data.rolling(window=window).mean()


def calculate_rsi(data,period=14):
    delta = data.diff()
    gain = (delta.where(delta>0,0)).rolling(window=period).mean()
    loss = (-delta.where(delta<0,0)).rolling(window=period).mean()

    rs=gain/loss
    rsi= 100-(100/(1+rs))

    return rsi

def calculate_bollinger_bands(data, window=20, stdd=2):
    middle = data.rolling(window=window).mean()
    std = data.rolling(window=window).std()

    upper = middle+(std*stdd)
    lower = middle-(std*stdd)

    return upper,middle,lower

def get_trading_session_info():
    now=datetime.now()

    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close= now.replace(hour=15, minute=30,second=0, microsecond=0)

    is_weekday=now.weekday()<5

    if is_weekday and market_open <= now <= market_close:
        status="OPEN"
        time_info = f"Market closes at{market_close.strftime('%I:%M %p')}"

    elif is_weekday and now <market_open:
        status="PRE_MARKET"
        time_info= f"Market opens at{market_open.strftime('%I:%M %p')}"

    elif is_weekday and now>market_close:
        status="AFTER_HOURS"
        next_open = (now + timedelta(days=1)).replace(hour=9,minute=15,second=0,microsecond=0)
        time_info = f"Market opens tomorrow at {next_open.strftime('%I:%M %p')}"

    else:
        status = "CLOSED"
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 1
        next_trading_day = now + timedelta(days=days_until_monday)
        next_open = next_trading_day.replace(hour=9, minute=30, second=0, microsecond=0)
        time_info = f"Market opens {next_open.strftime('%A at %I:%M %p')}"

    return {
            "status" : status,
            "time_info":time_info,
            "is_trading_hours": status=="OPEN"
    }


def create_price_alert(current_price, target_price, alert_type="both"):
    return {
        "current_price": current_price,
        "target_price": target_price,
        "alert_type": alert_type,
        "created_at": datetime.now(),
        "active": True
    }

def calculate_support_resistance(data,window=20):
    if len(data) < window:
        return {"support": None, "resistance": None}
    recent_data = data.tail(window)
    support=recent_data.min()
    resistance=recent_data.max()

    return{
        "support":support,
        "resistance":resistance,
        "range":resistance-support
    }


def format_market_cap(market_cap):
    if pd.isna(market_cap) or market_cap==0:
        return "N/A"
    return format_number(market_cap)



@st.cache_data(ttl=300)
def cached_calculations(func,*args,**kwargs):
    return func(*args,**kwargs)


def safe_divide(nume,deno,default=0):
    if deno==0 or pd.isna(deno):
        return default
    return nume/deno


def truncate_text(text,max_length=10):
    if not text or len(text) <= max_length:
        return text
    return text[:max_length-3]+ "....."