import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import streamlit as st
import matplotlib.pyplot as plt
from newsapi import NewsApiClient
from datetime import datetime , timedelta
from funcy import rtl_write
# 1. خواندن داده‌های قیمت طلا از فایل CSV
@st.cache_data
def load_gold_data(file_path):
    data = pd.read_csv(file_path, encoding='utf-16-le', header=None, 
                           names=["Date", "Open", "High", "Low", "Close", "Volume", "Additional", 'NewsImpact'])
    
    data['Date'] = pd.to_datetime(data['Date'])
    return data

# 2. دریافت اخبار از NewsAPI
def fetch_news(api_key, query, from_date, to_date):
    newsapi = NewsApiClient(api_key=api_key)
    news = newsapi.get_everything(
        q=query,
        from_param=from_date.strftime('%Y-%m-%d'),
        to=to_date.strftime('%Y-%m-%d'),
        language='en',
        sort_by='publishedAt'
    )
    articles = pd.DataFrame(news['articles'])
    articles['publishedAt'] = pd.to_datetime(articles['publishedAt']).dt.date
    return articles

# 3. ترکیب داده‌های قیمت طلا و اخبار
def merge_data(gold_data, news_data):
    merged_data = pd.merge_asof(
        gold_data.sort_values('Date'),
        news_data.sort_values('publishedAt'),
        left_on='Date',
        right_on='publishedAt'
    )
    return merged_data

# 4. ساخت مدل یادگیری ماشین
def train_model(data):
    # فرض کنید NewsImpact و Volume ویژگی‌های مستقل هستند و Close هدف است
    X = data[['Open', 'High', 'Low', 'Volume', 'NewsImpact']].fillna(0)
    y = data['Close']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    
    return model, mse

# 5. نمایش نتایج در Streamlit
def main():
    st.title("تحلیل تأثیر اخبار بر قیمت طلا")
    
    # بارگذاری داده‌ها
    gold_file = st.file_uploader("فایل CSV داده‌های قیمت طلا را آپلود کنید", type=["csv"])
    if not gold_file:
        st.warning("لطفاً فایل CSV داده‌های قیمت طلا را آپلود کنید.")
        return
    
    gold_data = load_gold_data(gold_file)
    
    # ورودی تاریخ برای جمع‌آوری اخبار
    st.subheader("انتخاب بازه زمانی برای جمع‌آوری اخبار")
    from_date = st.date_input("از تاریخ", value= datetime.today() - timedelta(days = 10))
    to_date = st.date_input("تا تاریخ", value=datetime.now())
    
    if from_date > to_date:
        st.error("تاریخ شروع باید قبل از تاریخ پایان باشد.")
        return
    
    # دریافت اخبار از NewsAPI
    api_key = "dbe24e0b2d9c4db0a026b32f86934e82"

    query = st.text_input(label = "write the wanted query")
    if query : 
        news_data = fetch_news(api_key, query, from_date, to_date)
        
        if news_data.empty:
            st.warning("هیچ خبری در این بازه زمانی یافت نشد.")
            return
        st.dataframe(news_data)
        # ترکیب داده‌ها
        merged_data = merge_data(gold_data, news_data)
        
        # آموزش مدل
        model, mse = train_model(merged_data)
        
        # نمایش نتایج
        st.subheader("نتایج مدل")
        st.write(f"میانگین مربعات خطا (MSE): {mse:.2f}")
        
        # نمودار قیمت طلا
        st.subheader("نمودار قیمت طلا")
        fig, ax = plt.subplots()
        ax.plot(merged_data['Date'], merged_data['Close'], label='قیمت بسته شدن')
        ax.set_title("قیمت طلا در طول زمان")
        ax.set_xlabel("تاریخ")
        ax.set_ylabel("قیمت (دلار)")
        ax.legend()
        st.pyplot(fig)
        
        # پیش‌بینی با مدل
        st.subheader("پیش‌بینی قیمت طلا")
        input_features = {
            'Open': st.number_input("قیمت باز شدن", value=900.0),
            'High': st.number_input("بالاترین قیمت", value=910.0),
            'Low': st.number_input("پایین‌ترین قیمت", value=890.0),
            'Volume': st.number_input("حجم معاملات", value=30000),
            'NewsImpact': st.number_input("تأثیر اخبار (0 یا 1)", value=0)
        }
        input_df = pd.DataFrame([input_features])
        prediction = model.predict(input_df)
        st.write(f"قیمت پیش‌بینی شده طلا: {prediction[0]:.2f} دلار")

main()    