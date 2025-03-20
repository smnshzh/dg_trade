import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.metrics import mean_squared_error

# عنوان برنامه
st.title("پیش‌بینی قیمت‌ها در ساعات بعدی با LSTM")

# آپلود فایل داده‌ها
uploaded_file = st.file_uploader("فایل CSV خود را آپلود کنید", type=["csv"])

if uploaded_file is not None:
    # خواندن داده‌ها
    data = pd.read_csv(uploaded_file, header=None)
    data.columns = ['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Other']

    # نمایش داده‌ها
    st.write("نمایش داده‌های آپلود شده:")
    st.write(data.head())

    # تبدیل ستون DateTime به فرمت تاریخ و ساعت
    data['DateTime'] = pd.to_datetime(data['DateTime'])

    # جدا کردن ویژگی‌ها و برچسب‌ها
    X = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    y = data['Close'].shift(-1)  # پیش‌بینی قیمت بسته شدن در ساعت بعدی

    # حذف سطرهای با مقادیر NaN
    X = X[:-1]
    y = y[:-1]

    # نرمال‌سازی داده‌ها
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # تقسیم داده‌ها به آموزش و آزمون
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, shuffle=False)

    # تغییر شکل داده‌ها برای LSTM
    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    # ساخت مدل LSTM
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(X_train.shape[1], 1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    # آموزش مدل
    if st.button("آموزش مدل"):
        with st.spinner("در حال آموزش مدل..."):
            model.fit(X_train, y_train, epochs=200, batch_size=32, verbose=1)
            st.success("مدل آموزش داده شد!")

        # پیش‌بینی روی داده‌های آزمون
        y_pred = model.predict(X_test)

        # محاسبه خطای میانگین مربعات (MSE)
        mse = mean_squared_error(y_test, y_pred)
        st.write(f"خطای میانگین مربعات (MSE): {mse}")

        # نمایش نتایج پیش‌بینی
        results = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred.flatten()})
        st.write("نتایج پیش‌بینی:")
        st.write(results)

        # نمایش نمودار پیش‌بینی
        st.line_chart(results)

    # پیش‌بینی قیمت‌های آینده
    if st.button("پیش‌بینی قیمت‌های آینده"):
        future_data = X_scaled[-1].reshape(1, X_scaled.shape[1], 1)  # استفاده از آخرین داده برای پیش‌بینی
        future_prediction = model.predict(future_data)
        st.write(f"پیش‌بینی قیمت در ساعت بعدی: {future_prediction[0][0]}")
else:
    st.write("لطفاً یک فایل CSV آپلود کنید.")