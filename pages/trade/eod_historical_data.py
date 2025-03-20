import pandas as pd
import requests
import streamlit as st
from funcy import rtl_write
import plotly.graph_objects as go

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

def calculate_trendlines(df):
    # Simple trendline calculation (linear regression for highs and lows)
    df['Uptrend'] = df['low'].rolling(window=20).mean()  # Uptrend line
    df['Downtrend'] = df['high'].rolling(window=20).mean()  # Downtrend line
    return df

def calculate_pivot_points(df):
    # Pivot Point Calculation
    df['Pivot'] = (df['high'] + df['low'] + df['close']) / 3
    df['R1'] = 2 * df['Pivot'] - df['low']
    df['S1'] = 2 * df['Pivot'] - df['high']
    df['R2'] = df['Pivot'] + (df['high'] - df['low'])
    df['S2'] = df['Pivot'] - (df['high'] - df['low'])
    return df

def plot_stock_data(df):
    fig = go.Figure()

    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Price"
    ))

    # Add support line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['Support'],
        mode='lines',
        name='Support',
        line=dict(color='green', width=1)
    ))

    # Add resistance line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['Resistance'],
        mode='lines',
        name='Resistance',
        line=dict(color='red', width=1)
    ))

    # Add uptrend line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['Uptrend'],
        mode='lines',
        name='Uptrend',
        line=dict(color='blue', width=1, dash='dot')
    ))

    # Add downtrend line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['Downtrend'],
        mode='lines',
        name='Downtrend',
        line=dict(color='orange', width=1, dash='dot')
    ))

    # Add pivot points
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['Pivot'],
        mode='lines',
        name='Pivot',
        line=dict(color='purple', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['R1'],
        mode='lines',
        name='R1',
        line=dict(color='pink', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['S1'],
        mode='lines',
        name='S1',
        line=dict(color='cyan', width=1)
    ))

    # Update layout
    fig.update_layout(
        title="Stock Price Analysis with Price Action Lines",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark"
    )

    return fig

def main():
    rtl_write("تحلیل خطوط عمل قیمت")
    selected_name = st.selectbox("نماد سهام مورد نظر را انتخاب کنید:", list(STOCK_SYMBOLS.values()))
    selected_symbol = [key for key, value in STOCK_SYMBOLS.items() if value == selected_name][0]

    if selected_symbol:
        data = fetch_stock_data(selected_symbol)
        if data is not None and not data.empty:
            if 'high' in data.columns and 'low' in data.columns:
                data = calculate_support_resistance(data)
                data = calculate_trendlines(data)
                data = calculate_pivot_points(data)

                # Display last few rows of data
                st.dataframe(data[['date', 'high', 'low', 'Support', 'Resistance', 'Uptrend', 'Downtrend', 'Pivot', 'R1', 'S1']].tail())

                # Plot the chart
                st.write(f"Chart for {selected_name} ({selected_symbol})")
                fig = plot_stock_data(data)
                st.plotly_chart(fig)

