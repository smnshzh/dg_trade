import streamlit as st
from pages.digikala.product_dgkala_pric import main as dpg
from pages.digikala.excel_product_digikala import main as epd
from pages.digikala.digikala_geting_product_from_brands import main as dgb
st.sidebar.title("DigiKala")
page = st.sidebar.radio("Go to", ["digikala price getter",
                                   "getting product by excel", 
                                   "getting product from brand link"])

if page == "digikala price getter":
    
    dpg()
if page == "getting product by excel":
    epd()
if page ==  "getting product from brand link":
    dgb()
