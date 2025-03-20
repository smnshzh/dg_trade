import json
import pyodbc
import requests
import logging
import streamlit as st
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to connect to SQL Server
def connect_to_sql_server():
    server = '.'  # SQL Server name
    database = 'marketing'  # Database name
    username = 'sa'  # Username
    password = '123456'  # Password
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    return pyodbc.connect(connection_string)

# Function to insert product details into the database
def insert_product_details(cursor, product_data):
    query = """
    INSERT INTO ProductDetails (
        ProductID,
        TitleFa,
        TitleEn,
        SubCategory1,
        SubCategory2,
        SubCategory3,
        SubCategory4,
        SubCategory5,
        Brand,
        Brand_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, 
                   product_data['id'], 
                   product_data['title_fa'], 
                   product_data['title_en'], 
                   product_data['categoryLevel1'], 
                   product_data['categoryLevel2'], 
                   product_data['categoryLevel3'], 
                   product_data['categoryLevel4'], 
                   product_data['categoryLevel5'], 
                   product_data['brand'], 
                   product_data['brand_id'])

# Function to fetch product data from the API
def fetch_product_data(product_id):
    url = f"https://api.digikala.com/v2/product/{product_id}/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching product {product_id}: {e}")
        return None

# Main function to process products and insert into the database
def main():
    # Streamlit UI
    st.title("Product Data Fetcher and Database Inserter")
    uploaded_file = st.file_uploader("Upload an Excel file with product IDs", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # Read product IDs from the Excel file
            df = pd.read_excel(uploaded_file)
            if 'ProductID' not in df.columns:
                st.error("The Excel file must contain a column named 'ProductID'.")
                return
            
            product_ids = df['ProductID'].dropna().astype(int).tolist()
            total_products = len(product_ids)
            
            if st.button("Start Processing"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, product_id in enumerate(product_ids):
                    with st.spinner(f"Processing product ID: {product_id}..."):
                        try:
                            logging.info(f"Processing product ID: {product_id}")

                            # Fetch product data from the API
                            data = fetch_product_data(product_id)

                            if not data or 'data' not in data or 'product' not in data['data']:
                                logging.warning(f"No valid data found for product ID: {product_id}")
                                continue

                            # Extract relevant product information
                            product_data = {
                                'id': data["data"]['product']['id'],
                                'title_fa': data["data"]['product']['title_fa'],
                                'title_en': data["data"]['product'].get('title_en', ''),
                                'categoryLevel1': data["data"]['product']["data_layer"]['category'],
                                'categoryLevel2': data["data"]['product']["data_layer"].get('item_category2', ''),
                                'categoryLevel3': data["data"]['product']["data_layer"].get('item_category3', ''),
                                'categoryLevel4': data["data"]['product']["data_layer"].get('item_category4', ''),
                                'categoryLevel5': data["data"]['product']["data_layer"].get('item_category5', ''),
                                'brand': data["data"]['product']['brand']['title_fa'],
                                'brand_id': data["data"]['product']['brand']['id']
                            }

                            # Insert product data into the database
                            try:
                                with connect_to_sql_server() as conn:
                                    with conn.cursor() as cursor:
                                        insert_product_details(cursor, product_data)
                                        conn.commit()
                                logging.info(f"Successfully inserted product ID: {product_id}")
                                status_text.text(f"✅ Successfully processed product ID: {product_id}")
                            except pyodbc.Error as e:
                                logging.error(f"Database error for product ID {product_id}: {e}")
                                status_text.text(f"❌ Database error for product ID: {product_id}")

                        except Exception as e:
                            logging.error(f"Unexpected error for product ID {product_id}: {e}")
                            status_text.text(f"❌ Unexpected error for product ID: {product_id}")

                    # Update progress bar
                    progress = (i + 1) / total_products
                    progress_bar.progress(progress)

                status_text.text("🎉 All products processed successfully!")

        except Exception as e:
            st.error(f"Error reading the Excel file: {e}")


main()    