import streamlit as st
import pandas as pd
import numpy as np
def main():
    # عنوان برنامه
    st.header("Trade Plan Generator - Advanced - DeepSeek")

    # Display RTL text using HTML
    st.write("""
    <div dir="rtl" style="text-align: right; font-family: 'Arial', sans-serif;">
        این برنامه داده‌های قیمتی را از فایل CSV خوانده و تحلیل تکنیکال شامل پیوت‌پوینت، 
        میانگین متحرک، RSI، MACD، حجم معاملات و الگوهای کندلی را ارائه می‌دهد.
    </div>
    """, unsafe_allow_html=True)

    # آپلود فایل CSV
    uploaded_file = st.file_uploader("فایل CSV خود را آپلود کنید:", type=["csv"])

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file, encoding='utf-16-le', header=None, 
                            names=["Date", "Open", "High", "Low", "Close", "Volume", "Additional"])
            data["Date"] = pd.to_datetime(data["Date"])
            data.set_index("Date", inplace=True)
            st.success("داده‌ها با موفقیت بارگذاری شدند.")
            
            # تشخیص تایم‌فریم بر اساس فاصله بین داده‌ها
            time_diffs = data.index.to_series().diff().dropna()
            avg_time_diff = time_diffs.mode()[0]
            if avg_time_diff <= pd.Timedelta(minutes=1):
                timeframe = "یک دقیقه‌ای"
            elif avg_time_diff <= pd.Timedelta(minutes=5):
                timeframe = "۵ دقیقه‌ای"
            elif avg_time_diff <= pd.Timedelta(hours=1):
                timeframe = "ساعتی"
            elif avg_time_diff <= pd.Timedelta(days=1):
                timeframe = "روزانه"
            elif avg_time_diff <= pd.Timedelta(weeks=1):
                timeframe = "هفتگی"
            else:
                timeframe = "ماهانه یا بالاتر"
            
            st.write(f"⏳ تایم‌فریم داده‌های ورودی: {timeframe}")

            # نمایش جدول داده‌ها
            st.subheader("داده‌های بارگذاری شده:")
            st.dataframe(data.tail(10))

            # انتخاب تعداد ردیف‌های پردازش‌شده
            row_count = int(st.number_input("تعداد سطرهای پردازش‌شده:", min_value=10, max_value=len(data), value=50))
            data = data.tail(row_count)

            # محاسبه پیوت‌پوینت و سطوح مقاومت و حمایت
            pivot_point = (data['High'].iloc[-1] + data['Low'].iloc[-1] + data['Close'].iloc[-1]) / 3
            r1 = 2 * pivot_point - data['Low'].iloc[-1]
            s1 = 2 * pivot_point - data['High'].iloc[-1]
            r2 = pivot_point + (data['High'].iloc[-1] - data['Low'].iloc[-1])
            s2 = pivot_point - (data['High'].iloc[-1] - data['Low'].iloc[-1])

            # تعیین نقاط ورود، استاپ‌لاس و تیک‌پروفیت
            buy_entry = s1
            sell_entry = r1
            stop_loss_buy = s2
            stop_loss_sell = r2
            take_profit_buy = r1
            take_profit_sell = s1

            # نمایش نقاط ورود و خروج در جدول
            trade_plan = pd.DataFrame({
                "نوع معامله": ["خرید", "فروش"],
                "نقطه ورود": [buy_entry, sell_entry],
                "استاپ لاس": [stop_loss_buy, stop_loss_sell],
                "تیک پروفیت": [take_profit_buy, take_profit_sell]
            })

            st.subheader("طرح معاملاتی:")
            st.dataframe(trade_plan)

            # محاسبه اندیکاتورها
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['RSI_14'] = 100 - (100 / (1 + (data['Close'].diff(1).clip(lower=0).rolling(window=14).mean() /
                                            data['Close'].diff(1).clip(upper=0).abs().rolling(window=14).mean())))
            data['MACD'] = data['Close'].ewm(span=12, adjust=False).mean() - data['Close'].ewm(span=26, adjust=False).mean()
            data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

            # تعیین توضیحات پویا
            rsi_desc = "اشباع خرید" if data['RSI_14'].iloc[-1] > 70 else "اشباع فروش" if data['RSI_14'].iloc[-1] < 30 else "نرمال"
            macd_desc = "روند صعودی" if data['MACD'].iloc[-1] > 0 else "روند نزولی"
            signal_desc = "تأیید سیگنال خرید" if data['MACD'].iloc[-1] > data['Signal'].iloc[-1] else "تأیید سیگنال فروش"

            # نمایش اندیکاتورها در جدول همراه با توضیحات پویا
            indicators_table = pd.DataFrame({
                "اندیکاتور": ["میانگین متحرک 20 روزه", "RSI (14)", "MACD", "Signal Line"],
                "مقدار": [data['SMA_20'].iloc[-1], data['RSI_14'].iloc[-1], data['MACD'].iloc[-1], data['Signal'].iloc[-1]],
                "توضیح": [
                    "نشان‌دهنده روند کلی قیمت در 20 دوره گذشته است.",
                    f"RSI ({data['RSI_14'].iloc[-1]:.2f}): {rsi_desc}",
                    f"MACD ({data['MACD'].iloc[-1]:.5f}): {macd_desc}",
                    f"Signal Line ({data['Signal'].iloc[-1]:.5f}): {signal_desc}"
                ]
            })
            
            st.subheader("مقادیر اندیکاتورها:")
            st.dataframe(indicators_table)
        
        except Exception as e:
            st.error(f"خطا در پردازش داده‌ها: {e}")
    else:
        st.info("لطفاً یک فایل CSV آپلود کنید.")
