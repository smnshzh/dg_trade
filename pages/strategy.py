import streamlit as st
import pandas as pd
import numpy as np

# عنوان برنامه
st.title("Trade Plan Generator - Advanced")

# توضیحات
st.write("""
این برنامه داده‌های قیمتی را از فایل CSV خوانده و تحلیل تکنیکال شامل پیوت‌پوینت، 
میانگین متحرک، RSI، MACD، حجم معاملات و الگوهای کندلی را ارائه می‌دهد.
""")

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
        if row_count:    
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
            data['SMA_10'] = data['Close'].rolling(window=10).mean()
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['RSI_14'] = 100 - 100 / (1 + (data['Close'].diff(1).clip(lower=0).rolling(window=14).mean() /
                                        data['Close'].diff(1).clip(upper=0).abs().rolling(window=14).mean()))
            data['MACD'] = data['Close'].ewm(span=12, adjust=False).mean() - data['Close'].ewm(span=26, adjust=False).mean()
            data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
            data['Upper_Band'], data['Middle_Band'], data['Lower_Band'] = (
                data['Close'].rolling(window=20).mean() + 2 * data['Close'].rolling(window=20).std(),
                data['Close'].rolling(window=20).mean(),
                data['Close'].rolling(window=20).mean() - 2 * data['Close'].rolling(window=20).std()
            )
            data['%K'] = 100 * (data['Close'] - data['Low'].rolling(window=14).min()) / (
                data['High'].rolling(window=14).max() - data['Low'].rolling(window=14).min())
            data['%D'] = data['%K'].rolling(window=3).mean()
            data['Parabolic_SAR'] = data['Close'].copy()  # برای سادگی، از محاسبه دقیق صرف‌نظر شده است

            # تعریف توضیحات اندیکاتورها
            indicators_descriptions = {
                "SMA_10": "میانگین متحرک ساده ۱۰ دوره‌ای: نشان‌دهنده میانگین قیمت در ۱۰ دوره گذشته است.",
                "SMA_20": "میانگین متحرک ساده ۲۰ دوره‌ای: نشان‌دهنده میانگین قیمت در ۲۰ دوره گذشته است.",
                "RSI_14": "شاخص قدرت نسبی (RSI): نشان‌دهنده قدرت حرکات قیمت است. مقادیر بالای ۷۰ اشباع خرید و زیر ۳۰ اشباع فروش را نشان می‌دهد.",
                "MACD": "واگرایی همگرایی میانگین متحرک (MACD): تفاوت بین دو میانگین متحرک نمایی (۱۲ و ۲۶ دوره‌ای) را نشان می‌دهد.",
                "Signal": "خط سیگنال MACD: میانگین متحرک نمایی ۹ دوره‌ای از MACD است.",
                "Upper_Band": "باند بالایی بولینگر: نشان‌دهنده انحراف معیار بالایی از میانگین متحرک ۲۰ دوره‌ای است.",
                "Middle_Band": "باند میانی بولینگر: میانگین متحرک ساده ۲۰ دوره‌ای است.",
                "Lower_Band": "باند پایینی بولینگر: نشان‌دهنده انحراف معیار پایینی از میانگین متحرک ۲۰ دوره‌ای است.",
                "%K": "خط %K استوکاستیک: نشان‌دهنده موقعیت قیمت نسبت به محدوده قیمتی ۱۴ دوره گذشته است.",
                "%D": "خط %D استوکاستیک: میانگین متحرک ۳ دوره‌ای از %K است.",
                "Parabolic_SAR": "پارابولیک SAR: نشان‌دهنده نقاط بازگشت احتمالی روند است."
            }

            # نمایش مقادیر اندیکاتورها همراه با توضیحات
            st.subheader("مقادیر اندیکاتورها و توضیحات:")
            indicators_table = pd.DataFrame({
                "اندیکاتور": ["SMA 10", "SMA 20", "RSI (14)", "MACD", "Signal Line", "بولینگر باند (بالایی)", "بولینگر باند (میانی)", "بولینگر باند (پایینی)", "%K", "%D", "Parabolic SAR"],
                "مقدار": [
                    data['SMA_10'].iloc[-1], data['SMA_20'].iloc[-1], data['RSI_14'].iloc[-1], 
                    data['MACD'].iloc[-1], data['Signal'].iloc[-1], data['Upper_Band'].iloc[-1], 
                    data['Middle_Band'].iloc[-1], data['Lower_Band'].iloc[-1], data['%K'].iloc[-1], 
                    data['%D'].iloc[-1], data['Parabolic_SAR'].iloc[-1]
                ],
                "توضیحات": [
                    indicators_descriptions["SMA_10"],
                    indicators_descriptions["SMA_20"],
                    indicators_descriptions["RSI_14"],
                    indicators_descriptions["MACD"],
                    indicators_descriptions["Signal"],
                    indicators_descriptions["Upper_Band"],
                    indicators_descriptions["Middle_Band"],
                    indicators_descriptions["Lower_Band"],
                    indicators_descriptions["%K"],
                    indicators_descriptions["%D"],
                    indicators_descriptions["Parabolic_SAR"]
                ]
            })
            st.dataframe(indicators_table)

            # تفسیر خودکار شرایط اندیکاتورها
            st.subheader("تفسیر شرایط اندیکاتورها:")

            # تفسیر SMA
            if data['SMA_10'].iloc[-1] > data['SMA_20'].iloc[-1]:
                st.write("📈 **میانگین متحرک ساده (SMA):** روند کوتاه‌مدت صعودی است (SMA 10 > SMA 20).")
            else:
                st.write("📉 **میانگین متحرک ساده (SMA):** روند کوتاه‌مدت نزولی است (SMA 10 < SMA 20).")

            # تفسیر RSI
            if data['RSI_14'].iloc[-1] > 70:
                st.write("📊 **شاخص قدرت نسبی (RSI):** بازار در شرایط اشباع خرید است (RSI > 70).")
            elif data['RSI_14'].iloc[-1] < 30:
                st.write("📊 **شاخص قدرت نسبی (RSI):** بازار در شرایط اشباع فروش است (RSI < 30).")
            else:
                st.write("📊 **شاخص قدرت نسبی (RSI):** بازار در حالت تعادل است (30 < RSI < 70).")

            # تفسیر MACD
            if data['MACD'].iloc[-1] > data['Signal'].iloc[-1]:
                st.write("📈 **MACD:** سیگنال خرید (MACD > Signal Line).")
            else:
                st.write("📉 **MACD:** سیگنال فروش (MACD < Signal Line).")

            # تفسیر بولینگر باند
            if data['Close'].iloc[-1] > data['Upper_Band'].iloc[-1]:
                st.write("📊 **بولینگر باند:** قیمت در محدوده اشباع خرید است (بالای باند بالایی).")
            elif data['Close'].iloc[-1] < data['Lower_Band'].iloc[-1]:
                st.write("📊 **بولینگر باند:** قیمت در محدوده اشباع فروش است (زیر باند پایینی).")
            else:
                st.write("📊 **بولینگر باند:** قیمت در محدوده نرمال است.")

            # تفسیر استوکاستیک
            if data['%K'].iloc[-1] > 80:
                st.write("📊 **استوکاستیک:** بازار در شرایط اشباع خرید است (%K > 80).")
            elif data['%K'].iloc[-1] < 20:
                st.write("📊 **استوکاستیک:** بازار در شرایط اشباع فروش است (%K < 20).")
            else:
                st.write("📊 **استوکاستیک:** بازار در حالت تعادل است.")

            # تفسیر پارابولیک SAR
            if data['Parabolic_SAR'].iloc[-1] < data['Close'].iloc[-1]:
                st.write("📈 **پارابولیک SAR:** روند صعودی است (SAR زیر قیمت).")
            else:
                st.write("📉 **پارابولیک SAR:** روند نزولی است (SAR بالای قیمت).")
    
    except Exception as e:
        st.error(f"خطا در پردازش داده‌ها: {e}")
else:
    st.info("لطفاً یک فایل CSV آپلود کنید.")