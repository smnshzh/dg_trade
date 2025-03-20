import streamlit as st
from PIL import Image

# تنظیمات صفحه
st.set_page_config(page_title="بارگذاری عکس", page_icon="📸")

# عنوان صفحه
st.title("📸 بارگذاری عکس با گوشی")
st.write("لطفاً یک عکس از طریق دکمه زیر بارگذاری کنید.")

# بخش بارگذاری فایل
uploaded_file = st.file_uploader("انتخاب عکس", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # نمایش اطلاعات فایل بارگذاری شده
    st.success("عکس با موفقیت بارگذاری شد!")
    st.write(f"نام فایل: {uploaded_file.name}")
    st.write(f"اندازه فایل: {round(uploaded_file.size / 1024, 2)} KB")

    # خواندن و نمایش تصویر
    image = Image.open(uploaded_file)
    st.image(image, caption="عکس بارگذاری شده", use_column_width=True)

    # ذخیره تصویر در سرور (اختیاری)
    if st.button("ذخیره عکس"):
        with open(f"uploaded_{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("عکس با موفقیت ذخیره شد!")

else:
    st.info("هنوز عکسی بارگذاری نشده است.")