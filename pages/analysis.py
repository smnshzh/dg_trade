import pandas as pd
import requests
import streamlit as st

# لیست نمادهای رایج و نام فارسی آن‌ها
STOCK_SYMBOLS = {
    "AAPL": "اپل",
    "MSFT": "مایکروسافت",
    "GOOGL": "گوگل",
    "AMZN": "آمازون",
    "TSLA": "تسلا",
    "META": "مِتا (فیسبوک سابق)",
    "NFLX": "نتفلیکس",
    "NVDA": "انویدیا",
    "INTC": "اینتل",
    "BABA": "علی‌بابا",
    "XAU": "طلا",
    "SI=F": "نقره",
    "CL=F": "نفت",
    "CC=F": "کاکائو"
}

def fetch_stock_data(symbol):
    api_url = f"https://eodhistoricaldata.com/api/eod/{symbol}"
    api_key = "67daec1dcd3b40.62287744"  # Replace with your API key
    params = {
        "api_token": api_key,
        "fmt": "json"
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def calculate_support_resistance(df, window=5):
    df['Support'] = df['low'].rolling(window=window).min()
    df['Resistance'] = df['high'].rolling(window=window).max()
    return df

st.title("محاسبه نقاط حمایت و مقاومت")
selected_name = st.selectbox("نماد سهام مورد نظر را انتخاب کنید:", list(STOCK_SYMBOLS.values()))
selected_symbol = [key for key, value in STOCK_SYMBOLS.items() if value == selected_name][0]

if selected_symbol:
    data = fetch_stock_data(selected_symbol)
    if data is not None and not data.empty:
        if 'high' in data.columns and 'low' in data.columns:
            data = calculate_support_resistance(data)
            st.dataframe(data[['date', 'high', 'low', 'Support', 'Resistance']].tail())