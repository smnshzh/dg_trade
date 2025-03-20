import streamlit as st
import pandas as pd
import talib
def main():
    # عنوان برنامه
    st.title("Trade Plan Generator")

    # توضیحات
    st.write("""
    این برنامه داده‌های قیمتی را از فایل CSV خوانده و یک طرح معاملاتی (Trade Plan) بر اساس تحلیل‌های پیشرفته ارائه می‌دهد.
    """)

    # آپلود فایل CSV
    uploaded_file = st.file_uploader("فایل CSV خود را آپلود کنید:", type=["csv"])

    def calculate_pivot_points(data):
        high = data['High'].max()
        low = data['Low'].min()
        close = data['Close'].iloc[-1]  # آخرین قیمت بسته شدن
        
        # محاسبه Pivot Point
        pp = (high + low + close) / 3
        r1 = 2 * pp - low
        s1 = 2 * pp - high
        r2 = pp + (high - low)
        s2 = pp - (high - low)
        
        return {
            "Pivot Point": pp,
            "Support 1": s1,
            "Resistance 1": r1,
            "Support 2": s2,
            "Resistance 2": r2
        }

    def calculate_fibonacci_retracement(data):
        high = data['High'].max()
        low = data['Low'].min()
        
        # محاسبه سطوح فیبوناچی
        diff = high - low
        fib_38_2 = high - 0.382 * diff
        fib_50 = high - 0.5 * diff
        fib_61_8 = high - 0.618 * diff
        
        return {
            "Fibonacci 38.2%": fib_38_2,
            "Fibonacci 50%": fib_50,
            "Fibonacci 61.8%": fib_61_8
        }

    if uploaded_file is not None:
        try:
            # خواندن داده‌ها با کدگذاری UTF-16 LE
            data = pd.read_csv(uploaded_file, encoding='utf-16-le', header=None, names=["Date", "Open", "High", "Low", "Close", "Volume", "Additional"])
            st.success("داده‌ها با موفقیت بارگذاری شدند.")
            
            # نمایش جدول داده‌ها
            st.subheader("داده‌های بارگذاری شده:")
            st.dataframe(data)

            # انتخاب تعداد ردیف‌های قابل پردازش
            row_count = st.selectbox(
                "تعداد ردیف‌هایی که می‌خواهید برای تحلیل استفاده شوند را انتخاب کنید:",
                options=[10, 20, 50, 100, len(data)],  # گزینه‌ها شامل مقادیر ثابت و تعداد کل ردیف‌ها
                index=4  # پیش‌فرض: همه ردیف‌ها
            )

            # محدود کردن داده‌ها به تعداد ردیف انتخاب‌شده
            data = data.head(row_count)

            # محاسبه پیوت‌پوینت
            pivot_points = calculate_pivot_points(data)

            # محاسبه فیبوناچی ریتریسمنت
            fib_levels = calculate_fibonacci_retracement(data)

            # محاسبه RSI و MACD
            data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
            macd, macdsignal, _ = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
            data['MACD'] = macd
            data['MACD_Signal'] = macdsignal

            # تحلیل حجم معاملات
            average_volume = data['Volume'].mean()
            current_volume = data['Volume'].iloc[-1]

            # نمایش Trade Plan
            st.subheader("Trade Plan:")
            st.write(f"تعداد ردیف‌های پردازش‌شده: {row_count}")

            # نمایش سطوح پیوت‌پوینت
            st.write("سطوح پیوت‌پوینت:")
            st.write(f"Pivot Point: {pivot_points['Pivot Point']:.5f}")
            st.write(f"Support 1: {pivot_points['Support 1']:.5f}")
            st.write(f"Resistance 1: {pivot_points['Resistance 1']:.5f}")
            st.write(f"Support 2: {pivot_points['Support 2']:.5f}")
            st.write(f"Resistance 2: {pivot_points['Resistance 2']:.5f}")

            # نمایش سطوح فیبوناچی
            st.write("سطوح فیبوناچی ریتریسمنت:")
            st.write(f"Fibonacci 38.2%: {fib_levels['Fibonacci 38.2%']:.5f}")
            st.write(f"Fibonacci 50%: {fib_levels['Fibonacci 50%']:.5f}")
            st.write(f"Fibonacci 61.8%: {fib_levels['Fibonacci 61.8%']:.5f}")

            # نمایش اندیکاتورها
            st.write("اندیکاتورها:")
            st.write(f"آخرین مقدار RSI: {data['RSI'].iloc[-1]:.2f}")
            st.write(f"آخرین مقدار MACD: {data['MACD'].iloc[-1]:.5f}")
            st.write(f"آخرین مقدار Signal Line: {data['MACD_Signal'].iloc[-1]:.5f}")

            # نمایش تحلیل حجم
            st.write("تحلیل حجم معاملات:")
            st.write(f"میانگین حجم: {average_volume:.2f}")
            st.write(f"حجم آخرین دوره: {current_volume:.2f}")
            if current_volume > average_volume:
                st.write("حجم معاملات بالاتر از میانگین است. ممکن است نشان‌دهنده تغییر روند باشد.")
            else:
                st.write("حجم معاملات در حد معمول است.")

        except Exception as e:
            st.error(f"خطا در خواندن فایل CSV: {e}")
    else:
        st.info("لطفاً یک فایل CSV آپلود کنید.")