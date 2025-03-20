import json
import pyodbc
import requests
import logging
import streamlit as st
import pandas as pd
from funcy import connect_to_mariadb as cm
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



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
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        product_data['id'],
        product_data['title_fa'],
        product_data['title_en'],
        product_data['categoryLevel1'],
        product_data['categoryLevel2'],
        product_data['categoryLevel3'],
        product_data['categoryLevel4'],
        product_data['categoryLevel5'],
        product_data['brand'],
        product_data['brand_id']
    )
    cursor.execute(query, values)

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
    st.title("Product Data Fetcher and Database Inserter")
    uploaded_file = st.file_uploader("Upload an Excel file with product IDs", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            if 'ProductID' not in df.columns:
                st.error("The Excel file must contain a column named 'ProductID'.")
                return
            
            if df['ProductID'].duplicated().any():
                st.error("The Excel file contains duplicate Product IDs.")
                return

            if not pd.api.types.is_integer_dtype(df['ProductID']):
                st.error("The 'ProductID' column must contain integer values.")
                return

            product_ids = df['ProductID'].dropna().astype(int).tolist()
            total_products = len(product_ids)
            
            if st.button("Start Processing"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, product_id in enumerate(product_ids):
                    status_text.text(f"Processing product ID: {product_id} ({i + 1}/{total_products})")
                    logging.info(f"Processing product ID: {product_id} ({i + 1}/{total_products})")

                    try:
                        data = fetch_product_data(product_id)
                        if not data or 'data' not in data or 'product' not in data['data']:
                            logging.warning(f"No valid data found for product ID: {product_id}")
                            continue

                        product_data = {
                            'id': data["data"]['product'].get('id', 0),
                            'title_fa': data["data"]['product'].get('title_fa', ''),
                            'title_en': data["data"]['product'].get('title_en', ''),
                            'categoryLevel1': data["data"]['product']["data_layer"].get('category', ''),
                            'categoryLevel2': data["data"]['product']["data_layer"].get('item_category2', ''),
                            'categoryLevel3': data["data"]['product']["data_layer"].get('item_category3', ''),
                            'categoryLevel4': data["data"]['product']["data_layer"].get('item_category4', ''),
                            'categoryLevel5': data["data"]['product']["data_layer"].get('item_category5', ''),
                            'brand': data["data"]['product']['brand'].get('title_fa', ''),
                            'brand_id': data["data"]['product']['brand'].get('id', 0)
                        }

                        with cm() as conn:
                            with conn.cursor() as cursor:
                                insert_product_details(cursor, product_data)
                                conn.commit()
                        logging.info(f"Successfully inserted product ID: {product_id}")
                        status_text.text(f"✅ Successfully processed product ID: {product_id}")

                    except requests.exceptions.RequestException as e:
                        logging.error(f"Network error fetching product {product_id}: {e}")
                        status_text.text(f"❌ Network error for product ID: {product_id}")
                    except KeyError as e:
                        logging.error(f"Missing key in API response for product ID {product_id}: {e}")
                        status_text.text(f"❌ Missing data for product ID: {product_id}")
                    except pyodbc.Error as e:
                        logging.error(f"Database error for product ID {product_id}: {e}")
                        status_text.text(f"❌ Database error for product ID: {product_id}")
                    except Exception as e:
                        logging.error(f"Unexpected error for product ID {product_id}: {e}")
                        status_text.text(f"❌ Unexpected error for product ID: {product_id}")

                    progress_bar.progress((i + 1) / total_products)

                status_text.text("🎉 All products processed successfully!")

        except Exception as e:
            st.error(f"Error reading the Excel file: {e}")

main()    