import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# تنظیمات اولیه برای Selenium
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # اجرای مرورگر در حالت غیرقابل مشاهده
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # استفاده از ChromeDriverManager برای مدیریت خودکار ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# استخراج لینک‌ها از یک صفحه
def extract_links_from_page(driver, page_url):
    driver.get(page_url)
    time.sleep(5)  # صبر کردن تا صفحه کامل لود شود

    # پیدا کردن تمام المنت‌هایی که دارای کلاس مشخص شده هستند
    product_elements = driver.find_elements(By.CSS_SELECTOR, "div.product-list_ProductList__item__LiiNI")

    links = []
    for element in product_elements:
        try:
            link_element = element.find_element(By.TAG_NAME, "a")
            href = link_element.get_attribute("href")
            links.append(href)
        except Exception as e:
            print(f"خطا در استخراج لینک: {e}")
    return links

# تابع اصلی
def main():
    link = st.text_input("write the url")
    if link:
        st.title("استخراج لینک‌های محصولات از دیجی‌کالا")
        st.write("این برنامه لینک‌های محصولات را از صفحات مشخص شده استخراج می‌کند و به صورت لایو در جدول نمایش می‌دهد.")

        # دریافت تعداد صفحات از کاربر
        num_pages = st.number_input("تعداد صفحات مورد نظر را وارد کنید:", min_value=1, value=1, step=1)

        if st.button("شروع استخراج"):
            # ایجاد یک DataFrame خالی برای ذخیره لینک‌ها
            data = {"لینک": []}
            df = pd.DataFrame(data)

            # نمایش جدول خالی در ابتدا
            table_placeholder = st.empty()
            table_placeholder.dataframe(df)

            # تنظیم WebDriver
            driver = setup_driver()

            try:
                total_rows = len(range(1, num_pages + 1))
                st.write(f"تعداد ردیف‌ها: {total_rows}")
                progress_bar = st.progress(0)
                status_text = st.empty()
                for page_num in range(1, num_pages + 1):
                    url = f"{link}/?page={page_num}"
                    status_text.text(f"در حال پردازش صفحه {page_num}...")
                    links = extract_links_from_page(driver, url)

                    # اضافه کردن لینک‌ها به DataFrame
                    for link in links:
                        new_row = {"لینک": link}
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

                    # به‌روزرسانی جدول به صورت لایو
                    table_placeholder.dataframe(df)
                    progress_bar.progress((page_num ) / total_rows)

            except Exception as e:
                st.error(f"خطا در استخراج اطلاعات: {e}")

            finally:
                driver.quit()


main()    