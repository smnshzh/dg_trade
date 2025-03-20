import streamlit as st
from pages.trade.eod_historical_data import main as eod
from pages.trade.news_impact import main as nip
from pages.trade.strategy import main as stg
from pages.trade.trade_deepseek import main as dss



st.sidebar.title("DigiKala")
page = st.sidebar.radio("Go to", ["eod historical data",
                                   "news impact", 
                                   "strategy",
                                  "deep seek strategy"
                                    ])

if page == "eod historical data":    
    eod()
if page == "news impact":
    nip()
if page ==  "strategy":
    stg()
if page == "deep seek strategy":
    dss()     
if page == "qwen strategy":
    qws()    