from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
import streamlit as st
def connect_to_mariadb():
    # Load environment variables from .env file
        load_dotenv()


        # Retrieve credentials from environment variables
        config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT')),
            'database': os.getenv('DB_NAME')
        }

        # Establish the connection
        connection = mysql.connector.connect(**config)

        if connection.is_connected():
            print("✅ Successfully connected to the MariaDB database!")
            return connection
        else :
             print("can not connect")
             return None

        

   
import streamlit as st

def rtl_write(text):
    """
    A helper function to write right-to-left (RTL) text in Streamlit.
    """
    # Wrap the text in an HTML div with RTL direction
    rtl_html = f'<div dir="rtl" style="text-align: right; font-family: Arial, sans-serif;">{text}</div>'
    # Render the HTML using st.write
    st.write(rtl_html, unsafe_allow_html=True)


